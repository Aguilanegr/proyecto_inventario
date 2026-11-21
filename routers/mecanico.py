from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import obtener_bd
from models.mecanico import Mecanico
from schemas.schemas import MecanicoCreate, MecanicoResponse

router = APIRouter(prefix="/mecanicos", tags=["Mecanicos"])

@router.post("/", response_model=MecanicoResponse, status_code=201)
async def crear_mecanico(datos: MecanicoCreate, db: AsyncSession = Depends(obtener_bd)):
    nuevo = Mecanico(
        documento=datos.documento,
        nombre_completo=datos.nombre_completo,
        especialidad=datos.especialidad
    )
    db.add(nuevo)
    await db.commit()
    await db.refresh(nuevo)
    return nuevo

@router.get("/", response_model=list[MecanicoResponse])
async def listar_mecanicos(db: AsyncSession = Depends(obtener_bd)):
    resultado = await db.execute(select(Mecanico).where(Mecanico.activo == True))
    return resultado.scalars().all()