from datetime import datetime, timezone
from sqlalchemy import Column, Datetime, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship
from core.database import Base

class Factura(Base):
    __tablename__="facturas"

    id =Column(Integer, primary_key=True, index=True)
    orden_id=Column(Integer, ForeignKey("ordenesid", ondelete="RESTRICT"), unique=True, nullable=False, index=True)
    fecha_emision=Column(Datetime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    subtotal_repuestos=Column(Float, nullable=False)
    costo_mano_obra=Column(Float, nullable=False)
    iva=Column(Float, nulLABLE=False)
    total_pagar=Column(Float, nullable=False)

    orden=relationship("Orden", back_populates="factura")