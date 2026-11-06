from fastapi import APIRouter, Depends, HTTPException, Query
from dependencias import vereficar_auditor, verificar_gerente
from schemas import MecanicoCreate
from database import leer_mecanicos, guardar_mecanicos

router = APIRouter(prefix="/mecanicos", tags=["mecanicos"])

ARCHIVO = "mecanicos.json"

@router.get("/", dependencies=[Depends(vereficar_auditor)])
async def listar_mecanico(skip: int = Query(0, ge=0), limit: int = Query(10, ge=0, le=100)):
    mecanicos = leer_mecanicos()
    return mecanicos[skip: skip + limit]

@router.post("/", status_code=201, dependencies=[Depends(verificar_gerente)])
async def crear_mecanicos(mecanico: MecanicoCreate):
    mecanicos = leer_mecanicos()
    nuevo_id =max([m["id"] for m in mecanicos], default=0)+1
    nuevo = {
        "id":nuevo_id,
        "nombre":mecanico.nombre,
        "especialidad":mecanico.especialidad,
        "salario":mecanico.salario
    }
    mecanicos.append(nuevo)
    guardar_mecanicos(mecanicos)
    return nuevo

@router.delete("/{id}", dependencies=[Depends(verificar_gerente)])
async def eliminar_mecanicos():
    mecanicos = leer_mecanicos()
    for m in mecanicos:
        if m["id"] == id:
            mecanicos.remove(m)
            guardar_mecanicos(mecanicos)
            return {"mensaje": f"mecanico con {id} eliminado"}
        raise HTTPException(status_code=404, detail="mecanico no encontrado")
