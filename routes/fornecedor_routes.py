from fastapi import APIRouter, HTTPException
from config import db
from schemas import Fornecedor
from bson import ObjectId

router = APIRouter()

@router.post("/", response_model=Fornecedor)
async def criar_fornecedor(fornecedor: Fornecedor):
    fornecedor_dict = fornecedor.dict(by_alias=True, exclude={"id"})
    novo_fornecedor = await db.fornecedores.insert_one(fornecedor_dict)

    fornecedor_criado = await db.fornecedores.find_one({"_id": novo_fornecedor.inserted_id})

    if not fornecedor_criado:
        raise HTTPException(status_code=400, detail="Erro ao criar fornecedor")

    fornecedor_criado["_id"] = str(fornecedor_criado["_id"])

    return fornecedor_criado


@router.get("/", response_model=dict)
async def listar_fornecedores(skip: int = 0, limit: int = 10):
    total_fornecedores = await db.fornecedores.count_documents({})
    fornecedores = await db.fornecedores.find().skip(skip).limit(limit).to_list(100)

    for fornecedor in fornecedores:
        fornecedor["_id"] = str(fornecedor["_id"])

    metadados = {
        "total": total_fornecedores,
        "skip": skip,
        "limit": limit,
        "page": (skip // limit) + 1 if limit else 0
    }

    return {"data": fornecedores, "metadados": metadados}


@router.get("/fornecedor/{fornecedor_id}", response_model=Fornecedor)
async def obter_fornecedor(fornecedor_id: str):
    if not ObjectId.is_valid(fornecedor_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    fornecedor = await db.fornecedores.find_one({"_id": ObjectId(fornecedor_id)})

    if not fornecedor:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")

    fornecedor["_id"] = str(fornecedor["_id"])

    return fornecedor

@router.put("/{fornecedor_id}", response_model=Fornecedor)
async def atualizar_fornecedor(fornecedor_id: str, fornecedor: Fornecedor):
    if not ObjectId.is_valid(fornecedor_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    fornecedor_dict = fornecedor.dict(by_alias=True, exclude={"id"})
    resultado = await db.fornecedores.update_one({"_id": ObjectId(fornecedor_id)}, {"$set": fornecedor_dict})

    if resultado.matched_count == 0:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")

    fornecedor_atualizado = await db.fornecedores.find_one({"_id": ObjectId(fornecedor_id)})
    fornecedor_atualizado["_id"] = str(fornecedor_atualizado["_id"])

    return fornecedor_atualizado


@router.delete("/{fornecedor_id}")
async def deletar_fornecedor(fornecedor_id: str):
    if not ObjectId.is_valid(fornecedor_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    resultado = await db.fornecedores.delete_one({"_id": ObjectId(fornecedor_id)})

    if resultado.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")

    return {"message": "Fornecedor deletado com sucesso"}

@router.get("/count")
async def contar_fornecedores():
    total_fornecedores = await db.fornecedores.count_documents({})
    return {"quantidade de entidades": total_fornecedores}

@router.get("/filter", response_model=dict)
async def filtrar_fornecedores(nome: str = None, telefone: str = None, cidade: str = None):
    filtro = {}

    if nome:
        filtro["nome"] = {"$regex": nome, "$options": "i"}  
    if telefone:
        filtro["telefone"] = {"$regex": telefone, "$options": "i"}
    if cidade:
        filtro["cidade"] = {"$regex": cidade, "$options": "i"}

    fornecedores = await db.fornecedores.find(filtro).to_list(100)

    for fornecedor in fornecedores:
        fornecedor["_id"] = str(fornecedor["_id"])

    return {"data": fornecedores}