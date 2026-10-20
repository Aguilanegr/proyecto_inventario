from fastapi import FastAPI, HTTPException#import mi framework
from database import leer_base_datos, obtener_producto

#inicializar la aplicacion
apiRest = FastAPI(
    title="API inventarios Sena",
    description="Mi primera APi asincrona",
    version="1.0.0"
)

#nuestra  primera endpoint
@apiRest.get("/")#Decorador  -> Funcion que recibe como parametro otra funcion
async def ruta_principal():
    return {"mensaje": "¡Bienvenido a mi primera API Rest!"}

@apiRest.get("/estado")
async def estado_servidor():
    return {"status": "en linea", "servicios": "operativo"}

tres = 3
dos = 2
resultado = tres + dos
@apiRest.get("/suma")
async def suma_servidor():
    return {"resultado": resultado}

@apiRest.get("/productos")
async def listar_productos():
    datos = await leer_base_datos()
    return {"cantidad": len(datos), "productos": datos}

@apiRest.get("/productos/{codigo_producto}")
async def buscar_un_producto(codigo_producto: str):
    try:
        producto = await obtener_producto(codigo_producto)
        return producto
    except KeyError:
        raise HTTPException(status_code=404, detail="El producto solicitado no existe en la base de datos")





