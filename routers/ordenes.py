from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from schemas import OrdenCreate, OrdenPatch, OrdenUpdate
from database import leer_base_datos, guardar_base_datos

router = APIRouter(prefix="/ordenes", tags=["Gestionar ordenes"])

@router.get("/")
async def obtener_ordenes(
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    modelo: Optional[str] = Query(None, description="Filtrar por modelo ej: Bajaj"),
    costo_minimo: Optional[float] = Query(None, ge=0, description="Costo minimo")
):
    datos = await leer_base_datos()

   
    if estado:
        datos = [o for o in datos if o["estado"].lower() == estado.lower()]
    
    if modelo:
        datos = [o for o in datos if modelo.lower() in o["modelo"].lower()]
        
    if costo_minimo is not None:
        datos = [o for o in datos if o.get("costo_reparacion", 0) >= costo_minimo]
    
    return {"total_ordenes": len(datos), "ordenes": datos}

@router.post("/", status_code=201)
async def crear_orden(orden: OrdenCreate):
    datos = await leer_base_datos()
    
    for item in datos:
        if item["placa"] == orden.placa and item["estado"] != "Entregada":
            raise HTTPException(
                status_code=400, 
                detail=f"La moto con placa {orden.placa} ya se encuentra en el taller ({item['estado']})."
            )
            
    nueva_orden = orden.model_dump()
    nueva_orden["estado"] = "En diagnóstico"
    nueva_orden["costo_reparacion"] = 0.0
    
    datos.append(nueva_orden) 
    await guardar_base_datos(datos)
    
    return {"mensaje": "Orden creada exitosamente", "orden": nueva_orden}

@router.get("/paginadas")
async def obtener_ordenes_paginadas(
    skip: int = Query(0, description="Cuantos registros saltar"),
    limit: int = Query(10, description="Limite de registros a devolver")
):
    datos = await leer_base_datos()
    datos_paginados = datos[skip: skip + limit]
    return {
        "mostrando": len(datos_paginados),
        "total_bd": len(datos),
        "skip": skip,
        "limit": limit,
        "ordenes": datos_paginados
    }

@router.put("/{placa}")
async def actualizar_orden(placa: str, orden_update: OrdenUpdate):
    datos = await leer_base_datos()
    for i, item in enumerate(datos):
        if item["placa"] == placa:
            datos[i]["estado"] = orden_update.nuevo_estado
            datos[i]["costo_reparacion"] = orden_update.costo_reparacion
            await guardar_base_datos(datos)
            return {"mensaje": "Orden actualizada correctamente", "orden": datos[i]}
    raise HTTPException(status_code=404, detail="Orden no encontrada")

@router.delete("/{placa}", status_code=204)
async def eliminar_orden(placa: str):
    datos = await leer_base_datos()
    datos_filtrados = [orden for orden in datos if orden["placa"] != placa]
    if len(datos) == len(datos_filtrados):
        raise HTTPException(status_code=404, detail="La orden no existe.")
    await guardar_base_datos(datos_filtrados)
    return None

@router.patch("/{placa}")
async def actualizacion_parcial(placa: str, orden_patch: OrdenPatch):
    datos = await leer_base_datos()
    for i, orden in enumerate(datos):
        if orden["placa"] == placa:
            datos_a_actualizar = orden_patch.model_dump(exclude_unset=True)
            datos[i].update(datos_a_actualizar)
            await guardar_base_datos(datos)
            return {"mensaje": "La orden ha sido actualizada", "orden": datos[i]} 
    raise HTTPException(status_code=404, detail="La orden no existe.")