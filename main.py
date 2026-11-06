from fastapi import FastAPI, Depends
from routers.ordenes import router as router_ordenes
from dependencias import simular_base_datos
from routers import mecanicos


app= FastAPI(
    title="El taller del gerente",
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