from fastapi import APIRouter, HTTPException
from config import db
from schemas import Pedido
from bson import ObjectId

router = APIRouter()

@router.post("/", response_model=Pedido)
async def criar_pedido(pedido: Pedido):
    pedido_dict = pedido.dict(by_alias=True, exclude={"id"})

    novo_pedido = await db.pedidos.insert_one(pedido_dict)

    pedido_criado = await db.pedidos.find_one({"_id": novo_pedido.inserted_id})

    if not pedido_criado:
        raise HTTPException(status_code=400, detail="Erro ao criar pedido")

    pedido_criado["_id"] = str(pedido_criado["_id"])

    return pedido_criado


@router.get("/", response_model=dict)
async def listar_pedidos(skip: int = 0, limit: int = 10):
    total_pedidos = await db.pedidos.count_documents({})
    pedidos = await db.pedidos.find().skip(skip).limit(limit).to_list(100)

    for pedido in pedidos:
        pedido["_id"] = str(pedido["_id"])
        
    metadados = {
        "total": total_pedidos,
        "skip": skip,
        "limit": limit,
        "page": (skip // limit) + 1 if limit else 0
    }

    return {"data": pedidos, "metadados": metadados}

@router.get("/pedido/{pedido_id}", response_model=Pedido)
async def obter_pedido(pedido_id: str):
    if not ObjectId.is_valid(pedido_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    pedido = await db.pedidos.find_one({"_id": ObjectId(pedido_id)})

    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    pedido["_id"] = str(pedido["_id"])

    return pedido


@router.put("/{pedido_id}", response_model=Pedido)
async def atualizar_pedido(pedido_id: str, pedido: Pedido):
    if not ObjectId.is_valid(pedido_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    pedido_dict = pedido.dict(by_alias=True, exclude={"id"})
    resultado = await db.pedidos.update_one({"_id": ObjectId(pedido_id)}, {"$set": pedido_dict})

    if resultado.matched_count == 0:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    pedido_atualizado = await db.pedidos.find_one({"_id": ObjectId(pedido_id)})
    pedido_atualizado["_id"] = str(pedido_atualizado["_id"])

    return pedido_atualizado


@router.delete("/{pedido_id}")
async def deletar_pedido(pedido_id: str):
    if not ObjectId.is_valid(pedido_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    resultado = await db.pedidos.delete_one({"_id": ObjectId(pedido_id)})

    if resultado.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    return {"message": "Pedido deletado com sucesso"}

@router.get("/count")
async def contar_pedidos():
    total_pedidos = await db.pedidos.count_documents({})
    return {"quantidade de entidades": total_pedidos}
