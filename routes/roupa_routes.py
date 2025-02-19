from fastapi import APIRouter, HTTPException
from config import db
from schemas import Roupa
from bson import ObjectId

router = APIRouter()

@router.post("/", response_model=Roupa)
async def criar_roupa(roupa: Roupa):
    roupa_dict = roupa.dict(by_alias=True, exclude={"id"})
    nova_roupa = await db.roupas.insert_one(roupa_dict)

    roupa_criada = await db.roupas.find_one({"_id": nova_roupa.inserted_id})

    if not roupa_criada:
        raise HTTPException(status_code=400, detail="Erro ao criar roupa")

    roupa_criada["_id"] = str(roupa_criada["_id"])

    return roupa_criada


@router.get("/", response_model=dict)
async def listar_roupas(skip: int = 0, limit: int = 10):
    total_roupas = await db.roupas.count_documents({})
    roupas = await db.roupas.find().skip(skip).limit(limit).to_list(100)

    for roupa in roupas:
        roupa["_id"] = str(roupa["_id"])

    # Metadados de paginação
    metadados = {
        "total": total_roupas,
        "skip": skip,
        "limit": limit,
        "page": (skip // limit) + 1 if limit else 0
    }

    return {"data": roupas, "metadados": metadados}

@router.get("/roupa/{roupa_id}", response_model=Roupa)
async def obter_roupa(roupa_id: str):
    if not ObjectId.is_valid(roupa_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    roupa = await db.roupas.find_one({"_id": ObjectId(roupa_id)})

    if not roupa:
        raise HTTPException(status_code=404, detail="Roupa não encontrada")

    roupa["_id"] = str(roupa["_id"])

    return roupa


@router.put("/{roupa_id}", response_model=Roupa)
async def atualizar_roupa(roupa_id: str, roupa: Roupa):
    if not ObjectId.is_valid(roupa_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    roupa_dict = roupa.dict(by_alias=True, exclude={"id"})
    resultado = await db.roupas.update_one({"_id": ObjectId(roupa_id)}, {"$set": roupa_dict})

    if resultado.matched_count == 0:
        raise HTTPException(status_code=404, detail="Roupa não encontrada")

    roupa_atualizada = await db.roupas.find_one({"_id": ObjectId(roupa_id)})
    roupa_atualizada["_id"] = str(roupa_atualizada["_id"])

    return roupa_atualizada


@router.delete("/{roupa_id}")
async def deletar_roupa(roupa_id: str):
    if not ObjectId.is_valid(roupa_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    resultado = await db.roupas.delete_one({"_id": ObjectId(roupa_id)})

    if resultado.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Roupa não encontrada")

    return {"message": "Roupa deletada com sucesso"}

@router.get("/count", response_model=int)
async def contar_roupas():
    total_roupas = await db.roupas.count_documents({})
    return total_roupas
