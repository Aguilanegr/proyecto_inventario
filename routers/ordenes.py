from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from core.database import obtener_bd
from models.orden import Orden as OrdenModel
from models.mecanico import Mecanico as MecanicoModel
from models.repuestos import repuestos as RepuestoModel
from models.orden_repuesto import OrdenRepuesto as OrdenRepuestoModel
from typing import Optional, List
from schemas.ordenes import OrdenCreate, OrdenPatch, OrdenResponse, AgregarRepuestoOrden, RepuestoEnOrdenResponse
from dependencias import verificar_api_key, parametros_paginacion
from sqlalchemy.orm import joinedload, selectinload
from models.factura import Factura as FacturaModel

router = APIRouter(prefix="/ordenes", tags=["Gestionar ordenes"])

@router.get("/", response_model=List[OrdenResponse])
async def obtener_ordenes(
    estado: Optional[str] = None,
    paginacion: dict = Depends(parametros_paginacion), 
    db: AsyncSession = Depends(obtener_bd)
):
    sentencia = select(OrdenModel).options(joinedload(OrdenModel.mecanico))
    resultado = await db.execute(sentencia)
    ordenes = resultado.scalars().all() # Traer los objetos (No "lenguaje" sql)

    return ordenes

@router.get("/{orden_id}", response_model=OrdenResponse)
async def obtener_orden_por_id(
    orden_id: int,
    db: AsyncSession = Depends(obtener_bd)
):
    # SELECT * FROM ordenes WHERE id = orden_id
    sentencia = select(OrdenModel).options(joinedload(OrdenModel.mecanico)).where(OrdenModel.id == orden_id)
    resultado = await db.execute(sentencia)

    orden = resultado.scalar_one_or_none()
    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")

    return orden

@router.post("/", status_code=201)
async def crear_orden(
    orden: OrdenCreate,
    api_key: str = Depends(verificar_api_key), 
    db: AsyncSession = Depends(obtener_bd)
):

    consulta_mec = select(MecanicoModel).where(MecanicoModel.id == orden.mecanico_id)
    res_mec = await db.execute(consulta_mec)
    mecanico_db = res_mec.scalar_one_or_none()

    if not mecanico_db or not mecanico_db.activo:
        raise HTTPException(
            status_code=400,
            datail=f"El mecanico con el ID {orden.mecanico_id} no existe o está inactivo."
        )
    
    nueva_orden = OrdenModel(**orden.model_dump())

    db.add(nueva_orden)

    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Error al guardar la base de datos")

    await db.refresh(nueva_orden)

    return {"mensaje": "Orden creada", "orden": nueva_orden}

@router.delete("/{placa}", status_code=204)
async def eliminar_orden(
    placa: str,
    db: AsyncSession = Depends(obtener_bd)
):
    sentencia = select(OrdenModel).where(OrdenModel.placa == placa)
    resultado = await db.execute(sentencia)
    orden = resultado.scalar_one_or_none()

    if not orden:
        raise HTTPException(status_code=404, detail="La orden no existe")

    await db.delete(orden)
    await db.commit()
    return None

@router.patch("/{placa}")
async def actualizacion_parcial(
    placa: str, 
    orden_patch: OrdenPatch,
    db: AsyncSession = Depends(obtener_bd)
):
    # SELECT * FROM ordenes WHERE placa == placa
    sentencia = select(OrdenModel).where(OrdenModel.placa == placa)
    resultado = await db.execute(sentencia)
    orden = resultado.scalar_one_or_none()

    if not orden:
        raise HTTPException(status_code=404, detail="La orden no existe")

    datos_a_actualizar = orden_patch.model_dump(exclude_unset=True)

    if "nuevo_estado" in datos_a_actualizar:
        datos_a_actualizar["estado"] = datos_a_actualizar.pop("nuevo_estado")

    mano_obra_ingresada=datos_a_actualizar.pop("mano_obra", None)
    estado_solicitado=datos_a_actualizar.get("estado")

    if(orden.estado=="reparada" or orden.factura is not None) and(
        estado_solicitado is not None and estado_solicitado != "reparada"):
        raise HTTPException(status_code=400, detail="no se puede modificar repuestos de una orden ya cerrada")

    if estado_solicitado == "reparada":
        res_fac=await db.execute(select(FacturaModel).where(FacturaModel.orden_id == orden.id ))
        factura_existente=res_fac.scalar_one_or_none()
        if factura_existente is not None or orden.factura is not None:
            orden.estado="reparada"
            try:
                await db.commit()
                await db.refresh(orden)
            except Exception:
                await db.rollback()
                raise HTTPException(status_code=500, detail="Error aplicando la actualización parcial.")
            return {"mensaje": "La orden ha sido actualizada con éxito", "orden": orden}

        res_rep=await db.execute(select(OrdenRepuestoModel).where(OrdenRepuestoModel.orden_id == orden.id))
        items_repuesto=res_rep.scalar().all()
        subtotal_repuestos=round(sum(float(item.cantidad)*float(item.precio_unitario_historico)for item in items_repuesto),2 )
        costo_actual=float(orden.costo_reparacion or 0.0)
        if mano_obra_ingresada is not None:
            mano_obra_adicional=round(float(mano_obra_ingresada), 2)
            total_neto=round(subtotal_repuestos + mano_obra_adicional, 2)
            orden.costo_reparacion=total_neto
        else:
            total_neto=round(max(costo_actual, subtotal_repuestos),2)
            orden.costo_reparacion=total_neto

        if orden.costo_reparacion <= 0 or total_neto <= 0:
            raise HTTPException(status_code=400, detail="no se puede marcar como resparada ni facturar una orden si costo_reparacion es igual a 0 ")

        costo_mano_obra=round(max(0.0, total_neto - subtotal_repuestos),2)
        iva=round(total_neto * 0.19, 2)
        total_pagar=round(total_neto + iva, 2)
        nueva_factura=FacturaModel(
            orden_id=orden.id,
            subtotal_repuestos=subtotal_repuestos,
            costo_mano_obra=costo_mano_obra,
            iva=iva,
            total_pagar=total_pagar
        )
        orden.estado="reparada"
        db.add(nueva_factura)
        try:
            await db.commit()
            await db.refresh(orden)
        except Exception:
            await db.rollback()
            raise HTTPException(status_code=500, detail="error aplicando la actualizacion parcial.")
        return{"mensaje":"orden marcada como reparada y factura generada con exito ", "orden":orden}
    for campo, valor in datos_a_actualizar.items():
        setattr(orden, campo, valor)

    if mano_obra_ingresada is not None:
        res_rep=await db.execute(select(OrdenRepuestoModel).where(OrdenRepuestoModel.orden_id == orden.id))
        items_repuesto=res_rep.scalar().all()
        subtotal_repuestos=sum(float(item.cantidad)*float(item.precio_unitario_historico) for item in items_repuesto)
        orden.costo_reparacion=round(subtotal_repuestos + float(mano_obra_ingresada), 2)
        try:
            await db.commit()
            await db.refresh(orden)
        except Exception:
            await db.rollback()
            raise HTTPException(status_code=500, detail="Error aplicando la actualización parcial.")

    return {"mensaje": "La orden ha sido actualizada con éxito", "orden": orden}
        
@router.post("/{orden_id}/repuestos", status_code=201, response_model=RepuestoEnOrdenResponse)
async def agregar_repuesto_a_orden(
    orden_id: int,
    datos: AgregarRepuestoOrden,
    db: AsyncSession = Depends(obtener_bd)
):
    # 1. Validar que la orden exista
    res_orden = await db.execute(select(OrdenModel).where(OrdenModel.id == orden_id))
    orden_db = res_orden.scalar_one_or_none()
    if not orden_db:
        raise HTTPException(status_code=404, detail="La orden de servicio no existe")

    # 2. Validar que el repuesto exista
    res_rep = await db.execute(select(RepuestoModel).where(RepuestoModel.id == datos.repuesto_id))
    rep_db = res_rep.scalar_one_or_none()
    if not rep_db:
        raise HTTPException(status_code=404, detail="El repuesto no existe")

    # 3. Validar stock
    if rep_db.stock_actual < datos.cantidad:
        raise HTTPException(
            status_code=400,
            detail=f"Stock insuficiente. En almacen tengo: {rep_db.stock_actual} y se solicitaron: {datos.cantidad}"
        )

    # Operacion transaccional
    rep_db.stock_actual -= datos.cantidad
    subtotal = rep_db.precio_venta * datos.cantidad
    orden_db.costo_reparacion += subtotal

    detalle = OrdenRepuestoModel(
        orden_id=orden_db.id,
        repuesto_id=rep_db.id,
        cantidad=datos.cantidad,
        precio_unitario_historico=rep_db.precio_venta
    )

    db.add(detalle)

    try:
        await db.commit()
        await db.refresh(detalle)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Error aplicando la actualización parcial.")

    return detalle