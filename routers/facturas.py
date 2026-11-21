# routers/facturas.py
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from core.database import obtener_bd
from models.factura import Factura as FacturaModel
from models.orden import Orden as OrdenModel
from models.orden_repuesto import OrdenRepuesto as OrdenRepuestoModel

router = APIRouter(prefix="/facturas", tags=["Facturación"])


class RepuestoFacturaDetalle(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nombre_repuesto: str
    cantidad: int
    precio_unitario_historico: float
    subtotal_linea: float


class FacturaDetalladaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # Datos de la factura
    id: int
    fecha_emision: datetime
    subtotal_repuestos: float
    costo_mano_obra: float
    iva: float
    total_pagar: float

    # Datos de la moto y placa
    placa: str
    modelo: Optional[str] = None

    # Mecánico
    nombre_mecanico: str

    # Lista detallada de repuestos cobrados
    repuestos: List[RepuestoFacturaDetalle]


@router.get("/{orden_id}", response_model=FacturaDetalladaResponse)
async def obtener_factura_por_orden(
    orden_id: int,
    db: AsyncSession = Depends(obtener_bd),
):
    sentencia = (
        select(FacturaModel)
        .options(
            selectinload(FacturaModel.orden).selectinload(OrdenModel.mecanico),
            selectinload(FacturaModel.orden)
            .selectinload(OrdenModel.repuestos_usados)
            .selectinload(OrdenRepuestoModel.repuesto),
        )
        .where(FacturaModel.orden_id == orden_id)
    )
    resultado = await db.execute(sentencia)
    factura = resultado.scalar_one_or_none()

    if not factura or not factura.orden:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe factura registrada para la orden {orden_id}",
        )

    orden = factura.orden

    mecanico = getattr(orden, "mecanico", None)
    nombre_mecanico = (
        getattr(mecanico, "nombre_completo", None) or "No asignado"
        if mecanico
        else "No asignado"
    )

    repuestos_detalle: List[RepuestoFacturaDetalle] = []
    for item in getattr(orden, "repuestos_usados", []) or []:
        repuesto_catalogo = getattr(item, "repuesto", None)
        nombre_repuesto = (
            getattr(item, "nombre_repuesto", None)
            or getattr(repuesto_catalogo, "nombre", None)
            or getattr(repuesto_catalogo, "nombre_repuesto", None)
            or f"Repuesto #{item.repuesto_id}"
        )
        cantidad = int(item.cantidad)
        precio_unitario = float(item.precio_unitario_historico)
        subtotal_linea = round(cantidad * precio_unitario, 2)

        repuestos_detalle.append(
            RepuestoFacturaDetalle(
                nombre_repuesto=nombre_repuesto,
                cantidad=cantidad,
                precio_unitario_historico=precio_unitario,
                subtotal_linea=subtotal_linea,
            )
        )

    return FacturaDetalladaResponse(
        id=factura.id,
        fecha_emision=factura.fecha_emision,
        subtotal_repuestos=factura.subtotal_repuestos,
        costo_mano_obra=factura.costo_mano_obra,
        iva=factura.iva,
        total_pagar=factura.total_pagar,
        placa=orden.placa,
        modelo=orden.modelo,
        nombre_mecanico=nombre_mecanico,
        repuestos=repuestos_detalle,
    )