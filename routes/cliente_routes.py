from fastapi import APIRouter, HTTPException
from config import db
from schemas import Cliente
from bson import ObjectId

router = APIRouter()

@router.post("/", response_model=Cliente)
async def criar_cliente(cliente: Cliente):
    cliente_dict = cliente.dict(by_alias=True, exclude={"id"})
    novo_cliente = await db.clientes.insert_one(cliente_dict)

    cliente_criado = await db.clientes.find_one({"_id": novo_cliente.inserted_id})

    if not cliente_criado:
        raise HTTPException(status_code=400, detail="Erro ao criar cliente")

    cliente_criado["_id"] = str(cliente_criado["_id"])

    return cliente_criado


@router.get("/", response_model=dict)
async def listar_clientes(skip: int = 0, limit: int = 10):
    total_clientes = await db.clientes.count_documents({})
    clientes = await db.clientes.find().skip(skip).limit(limit).to_list(100)

    for cliente in clientes:
        cliente["_id"] = str(cliente["_id"])
        
    metadados = {
        "total": total_clientes,
        "skip": skip,
        "limit": limit,
        "page": (skip // limit) + 1 if limit else 0
    }

    return {"data": clientes, "metadados": metadados}


@router.get("/cliente/{cliente_id}", response_model=Cliente)
async def obter_cliente(cliente_id: str):
    if not ObjectId.is_valid(cliente_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    cliente = await db.clientes.find_one({"_id": ObjectId(cliente_id)})

    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    cliente["_id"] = str(cliente["_id"])

    return cliente

@router.put("/{cliente_id}", response_model=Cliente)
async def atualizar_cliente(cliente_id: str, cliente: Cliente):
    if not ObjectId.is_valid(cliente_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    cliente_dict = cliente.dict(by_alias=True, exclude={"id"})
    resultado = await db.clientes.update_one({"_id": ObjectId(cliente_id)}, {"$set": cliente_dict})

    if resultado.matched_count == 0:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    cliente_atualizado = await db.clientes.find_one({"_id": ObjectId(cliente_id)})
    cliente_atualizado["_id"] = str(cliente_atualizado["_id"])

    return cliente_atualizado


@router.delete("/{cliente_id}")
async def deletar_cliente(cliente_id: str):
    if not ObjectId.is_valid(cliente_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    resultado = await db.clientes.delete_one({"_id": ObjectId(cliente_id)})

    if resultado.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    return {"message": "Cliente deletado com sucesso"}

@router.get("/count")
async def contar_clientes():
    total_clientes = await db.clientes.count_documents({})
    return {"quantidade de entidades": total_clientes}

@router.get("/filter", response_model=dict)
async def filtrar_clientes(nome: str = None, cpf: str = None, email: str = None, cidade: str = None):
    filtro = {}

    if nome:
        filtro["nome"] = {"$regex": nome, "$options": "i"}
    if cpf:
        filtro["cpf"] = {"$regex": cpf, "$options": "i"}    
    if email:
        filtro["email"] = {"$regex": email, "$options": "i"}
    if cidade:
        filtro["endereco.cidade"] = {"$regex": cidade, "$options": "i"}

    clientes = await db.clientes.find(filtro).to_list(100)

    for cliente in clientes:
        cliente["_id"] = str(cliente["_id"])

    return {"data": clientes}
