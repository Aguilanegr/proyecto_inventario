from pydantic import BaseModel, Field
from typing import Optional

class ProductoCreate(BaseModel):
    codigo: str = Field(..., min_length=3, max_length=10, description="Código único del producto")
    nombre: str = Field(..., min_length=3, max_length=50, description="Nombre del producto")
    categoria: str
    precio: float = Field(..., gt=0, description="El precio debe ser mayor a 0")
    stock: int = Field(default=0, ge=0, description="El stock no puede ser negativo")
    compatible_con: Optional[str] = None