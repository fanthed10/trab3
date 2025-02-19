from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Roupa(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    nome: str
    tamanho: str
    cor: str
    preco: float
    fornecedor_id: str  # 1:N - Referenciamento

class Fornecedor(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    nome: str
    telefone: str
    email: str
    cidade: str
    frete: float

class Cliente(BaseModel):
    id : Optional[str] = Field(None, alias="_id")
    nome: str
    cpf: str
    telefone: str
    email: str        

class Pedido(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    data: datetime
    status: str
    valor_total: float
    form_pag: str
    cliente: Cliente # 1:1 - Embedding

class ItensPedido(BaseModel): # N:N - Coleção extra 
    id: Optional[str] = Field(None, alias="_id")
    pedido_id: str
    roupa_id: str
    quantidade: int
    preco_unitario: float
    subtotal: float