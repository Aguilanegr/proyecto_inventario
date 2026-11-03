from fastapi import FastAPI
from routers.ordenes import router as router_ordenes

app = FastAPI(
    title="API  de las mejortes motos del aguilanegra2 ",
    description="Sistema de triaje y facturación asi bien epica xd ",
    version="1.0"
)

app.include_router(router_ordenes)