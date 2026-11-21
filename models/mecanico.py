from sqlalchemy import Column, String, Boolean, Integer
from core.database import Base

class Mecanico(Base):
    __tablename__ = "mecanicos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    documento = Column(String(15), unique=True, nullable=False)
    nombre_completo = Column(String(100), nullable=False)
    especialidad = Column(String(50), nullable=False)
    activo = Column(Boolean, default=True)


    