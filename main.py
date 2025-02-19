from fastapi import FastAPI

from routes import (
    fornecedor_routes,cliente_routes, roupa_routes,pedido_routes,itensPedido_routes
)

app = FastAPI()

app.include_router(fornecedor_routes.router, prefix="/fornecedores", tags=["Fornecedores"])
app.include_router(cliente_routes.router, prefix="/clientes", tags=["Clientes"])
app.include_router(roupa_routes.router, prefix="/roupas", tags=["Roupas"])
app.include_router(pedido_routes.router, prefix="/pedidos", tags=["Pedidos"])
app.include_router(itensPedido_routes.router, prefix="/itensPedidos", tags=["Itens Pedidos"])

@app.get("/")
def home():
    return {"message": "API de Gestão de loja de roupas com FastAPI e MongoDB"}