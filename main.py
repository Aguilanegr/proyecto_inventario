from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from routers.ordenes import router as router_ordenes
from dependencias import simular_base_datos
from routers import mecanicos
from core.config import settings
from models.orden import Orden
from core.database import engine, base

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

app = FastAPI(
    title="API  de las mejortes motos del aguilanegra2 ",
    description="Sistema de triaje y facturación asi bien epica xd ",
    version="1.0"
)

app.include_router(router_ordenes)

@app.get("/")
async def probar_yield(conexion: str = Depends(simular_base_datos)):
    print("2. [RUTA] Ejecutando la ruta. Estado:", conexion)
    return {"mensaje": "el codigo"}

@app.get("/")
async def ping():
    return {"mensaje": f"Bienvenido a {settings.PROJECT_NAME}", "db_configurada": True}