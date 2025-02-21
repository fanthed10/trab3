from fastapi import APIRouter, HTTPException
from config import db
from bson import ObjectId
from datetime import datetime

router = APIRouter()

@router.get("/itensPedidoPorPedido/{pedido_id}", response_model=dict)
async def itens_por_pedido(pedido_id: str, skip: int = 0, limit: int = 10):
    if not ObjectId.is_valid(pedido_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    itens_pedido = await db.itens_pedidos.find({"pedido_id": pedido_id}).skip(skip).limit(limit).to_list(100)

    for item in itens_pedido:
        item["_id"] = str(item["_id"])

    return {"data": itens_pedido}

@router.get("/search/roupas", response_model=dict)
async def buscar_roupas_por_nome(nome: str, skip: int = 0, limit: int = 10):
    filtro = {"nome": {"$regex": nome, "$options": "i"}}  # 'i' é para case-insensitive
    
    roupas = await db.roupas.find(filtro).skip(skip).limit(limit).to_list(100)
    
    for roupa in roupas:
        roupa["_id"] = str(roupa["_id"])
    
    return {"data": roupas}

@router.get("/pedidosPorAno", response_model=dict)
async def pedidos_por_ano(ano: int, skip: int = 0, limit: int = 10):
    data_inicial = datetime(ano, 1, 1)
    data_final = datetime(ano + 1, 1, 1)

    pedidos = await db.pedidos.find({
        "data": {"$gte": data_inicial, "$lt": data_final}
    }).skip(skip).limit(limit).to_list(100)

    for pedido in pedidos:
        pedido["_id"] = str(pedido["_id"])

    return {"data": pedidos}

@router.get("/contagemPedidosPorStatus")
async def contar_pedidos_por_status():
    pipeline = [
        {"$group": {"_id": "$status", "total": {"$sum": 1}}}
    ]
    resultado = await db.pedidos.aggregate(pipeline).to_list(100)

    return {"data": resultado}

@router.get("/contarPedidosPorCliente", response_model=dict)
async def contar_pedidos_por_cliente():
    pipeline = [
        {"$group": {"_id": "$cliente_id", "quantidade_pedidos": {"$sum": 1}}}
    ]
    resultados = await db.pedidos.aggregate(pipeline).to_list(100)
    
    return {"data": resultados}

@router.get("/totalPedidosPorCliente", response_model=dict)
async def total_pedidos_por_cliente():
    pipeline = [
        {"$group": {"_id": "$cliente_id", "valor_total": {"$sum": "$valor_total"}}}
    ]
    resultados = await db.pedidos.aggregate(pipeline).to_list(100)
    
    return {"data": resultados}


@router.get("/roupasOrdenadasPorPreco", response_model=dict)
async def listar_roupas_ordenadas(ordem: str = "asc"):
    if ordem == "asc":
        roupas = await db.roupas.find().sort("preco", 1).to_list(100)
    else:
        roupas = await db.roupas.find().sort("preco", -1).to_list(100)

    for roupa in roupas:
        roupa["_id"] = str(roupa["_id"])

    return {"data": roupas}

@router.get("/pedidosComItens")
async def pedidos_com_itens():
    pipeline = [
        {
            "$lookup": {
                "from": "itens_pedidos",
                "localField": "_id",
                "foreignField": "pedido_id",
                "as": "itens"
            }
        }
    ]
    pedidos_com_itens = await db.pedidos.aggregate(pipeline).to_list(100)

    for pedido in pedidos_com_itens:
        pedido["_id"] = str(pedido["_id"])
        for item in pedido["itens"]:
            item["_id"] = str(item["_id"])

    return {"data": pedidos_com_itens}

@router.get("/listarRoupasPorFornecedor/{fornecedor_id}", response_model=dict)
async def listar_roupas_por_fornecedor(fornecedor_id: str, skip: int = 0, limit: int = 10):
    roupas = await db.roupas.find({"fornecedor_id": fornecedor_id}).skip(skip).limit(limit).to_list(100)
    
    for roupa in roupas:
        roupa["_id"] = str(roupa["_id"])
    
    return {"data": roupas}

@router.get("/itens_vendidos_por_roupa", response_model=dict)
async def itens_vendidos_por_roupa():
    pipeline = [
        {"$lookup": {
            "from": "itens_pedidos",
            "localField": "_id",
            "foreignField": "pedido_id",
            "as": "itens_pedido"
        }},
        {"$unwind": "$itens_pedido"},
        {"$group": {
            "_id": "$itens_pedido.roupa_id",
            "quantidade_vendida": {"$sum": "$itens_pedido.quantidade"}
        }},
        {"$lookup": {
            "from": "roupas",
            "localField": "_id",
            "foreignField": "_id",
            "as": "roupa"
        }},
        {"$unwind": "$roupa"}
    ]
    
    resultados = await db.pedidos.aggregate(pipeline).to_list(100)
    
    for resultado in resultados:
        resultado["_id"] = str(resultado["_id"])
    
    return {"data": resultados}
