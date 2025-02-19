from fastapi import APIRouter, HTTPException
from config import db
from schemas import ItensPedido
from bson import ObjectId

router = APIRouter()

@router.post("/", response_model=ItensPedido)
async def criar_item_pedido(item_pedido: ItensPedido):
    item_pedido_dict = item_pedido.dict(by_alias=True, exclude={"id"})
    novo_item_pedido = await db.itens_pedidos.insert_one(item_pedido_dict)

    item_pedido_criado = await db.itens_pedidos.find_one({"_id": novo_item_pedido.inserted_id})

    if not item_pedido_criado:
        raise HTTPException(status_code=400, detail="Erro ao criar item do pedido")

    item_pedido_criado["_id"] = str(item_pedido_criado["_id"])

    return item_pedido_criado


@router.get("/", response_model=dict)
async def listar_itens_pedidos(skip: int = 0, limit: int = 10):
    total_itens_pedidos = await db.itens_pedidos.count_documents({})
    itens_pedidos = await db.itens_pedidos.find().skip(skip).limit(limit).to_list(100)

    for item in itens_pedidos:
        item["_id"] = str(item["_id"])

    # Metadados de paginação
    metadados = {
        "total": total_itens_pedidos,
        "skip": skip,
        "limit": limit,
        "page": (skip // limit) + 1 if limit else 0
    }

    return {"data": itens_pedidos, "metadados": metadados}



@router.get("/item/{item_id}", response_model=ItensPedido)
async def obter_item_pedido(item_id: str):
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    item = await db.itens_pedidos.find_one({"_id": ObjectId(item_id)})

    if not item:
        raise HTTPException(status_code=404, detail="Item do pedido não encontrado")

    item["_id"] = str(item["_id"])

    return item


@router.put("/{item_id}", response_model=ItensPedido)
async def atualizar_item_pedido(item_id: str, item_pedido: ItensPedido):
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    item_pedido_dict = item_pedido.dict(by_alias=True, exclude={"id"})
    resultado = await db.itens_pedidos.update_one({"_id": ObjectId(item_id)}, {"$set": item_pedido_dict})

    if resultado.matched_count == 0:
        raise HTTPException(status_code=404, detail="Item do pedido não encontrado")

    item_pedido_atualizado = await db.itens_pedidos.find_one({"_id": ObjectId(item_id)})
    item_pedido_atualizado["_id"] = str(item_pedido_atualizado["_id"])

    return item_pedido_atualizado


@router.delete("/{item_id}")
async def deletar_item_pedido(item_id: str):
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    resultado = await db.itens_pedidos.delete_one({"_id": ObjectId(item_id)})

    if resultado.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item do pedido não encontrado")

    return {"message": "Item do pedido deletado com sucesso"}

@router.get("/count", response_model=int)
async def contar_itens_pedidos():
    total_itens_pedidos = await db.itens_pedidos.count_documents({})
    return total_itens_pedidos
