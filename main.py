from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from routers.ordenes import router as router_ordenes
from dependencias import simular_base_datos
from routers import mecanicos, repuestos, facturas, ordenes
from core.config import settings
from models.orden import OrdenRepuesto
from core.database import engine, base

app = FastAPI()

app.include_router(ordenes.router)
app.include_router(facturas.router)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("conectando conl la bd  y creando las tablas...")
    async with engine.begin() as conn:
        await conn.run_sync(base.metadata.create_all)

    print("base de datos lista.")

    yield

    print("apagando el servidor y limpiendo recursos")

app= FastAPI(
    title=settings.PROJECT_NAME,
    description="sitema de triaje y facturacion",
    version="1.0",
    lifespan=lifespan
)

app.include_router(mecanicos.router)
app.include_router(repuestos.router)
