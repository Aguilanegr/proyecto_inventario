from fastapi import FastAPI, HTTPException #importo mi framework
from database import leer_base_datos, obtener_producto

# Inicializar la aplicación
apiRest = FastAPI(
    title="API inventarios SENA",
    description="Mi primera API asíncrona",
    version="1.0.0"
)

# Nuestro primer endpoint
@apiRest.get("/") # Decorador -> Función que recibe como parámetro otra función
async def ruta_principal():
    return {"mensaje": "¡Bienvenido a mi primera API Rest!"}

@apiRest.get("/estado")
async def estado_servidor():
    return {"status": "En línea", "servicios": "Operativos sin ningun invonveniente"}

@apiRest.get("/productos")
async def listar_productos():
    datos = await leer_base_datos()
    return {"cantidad": len(datos), "productos": datos}

@apiRest.get("/productos/{codigo_producto}")
async def buscar_un_producto(codigo_producto: str):
    try:
        # Para llamar a la función de obtener producto
        producto = await obtener_producto(codigo_producto)
        return producto
    except KeyError:
        raise HTTPException(status_code=404, detail="El producto solicitado no existe en la BD.")

@apiRest.get("/categorias")
async def obtener_categorias():
    datos = await leer_base_datos()
    categorias = set()
    for producto in datos:
        if "categoria" in producto:
            categorias.add(producto["categoria"])
            return {"categorias": list(categorias)}
        

@apiRest.get("/alertas/stock")
async def obtener_stock_critico():
    datos = await leer_base_datos()
    productos_criticos = [p for p in datos if p.get("stock", 0) <= 3]
    
    return {
        "total_en_alerta": len(productos_criticos),
        "productos": productos_criticos
    }

@apiRest.get("/productos/buscar/{palabra_clave}")
async def buscar_por_nombre(palabra_clave: str):
    datos = await leer_base_datos()
    
    resultados = []
    for producto in datos:
        if palabra_clave.lower() in producto.get("nombre", "").lower():
            resultados.append(producto)
            
    return {
        "busqueda": palabra_clave,
        "coincidencias": len(resultados),
        "resultados": resultados
    }