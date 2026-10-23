from fastapi import FastAPI, HTTPException, Request
from database import leer_base_datos, obtener_producto, guardar_base_datos
from schemas import ProductoCreate

# Inicializar la aplicación
apiRest = FastAPI(
    title="API inventarios SENA",
    description="Mi primera API asíncrona",
    version="1.0.0"
)

# 1. Ruta principal
@apiRest.get("/")
async def ruta_principal():
    return {"mensaje": "¡Bienvenido a mi primera API Rest!"}

@apiRest.get("/estado")
async def estado_servidor():
    return {"status": "En línea", "servicios": "Operativos sin ningun invonveniente"}

# 2. Listar todos los productos
@apiRest.get("/productos")
async def listar_productos():
    datos = await leer_base_datos()
    return {"cantidad": len(datos), "productos": datos}

@apiRest.get("/categorias")
async def obtener_categorias():
    datos = await leer_base_datos()
    categorias = set()
    for producto in datos:
        cat = producto.get("categoria")
        if cat:
            categorias.add(cat)
    return {"categorias": list(categorias)}

@apiRest.get("/alertas/stock")
async def alerta_stock():
    datos = await leer_base_datos()
    productos_criticos = []
    for producto in datos:
        if producto.get("stock", 999) <= 3:
            productos_criticos.append(producto)
    return {"cantidad": len(productos_criticos), "productos": productos_criticos}

@apiRest.get("/productos/buscar/{palabra_clave}")
async def buscar_productos(palabra_clave: str):
    datos = await leer_base_datos()
    resultados = []
    for producto in datos:
        if palabra_clave.lower() in producto.get("nombre","").lower():
            resultados.append(producto)
    return {"cantidad": len(resultados), "productos": resultados}

@apiRest.get("/productos/{codigo_producto}")
async def buscar_un_producto(codigo_producto: str):
    try:
        producto = await obtener_producto(codigo_producto)
        return producto
    except KeyError:
        raise HTTPException(status_code=404, detail="El producto solicitado no existe en la BD.")

@apiRest.post("/productos", status_code=201)
async def registrar_nuevo_producto(producto: ProductoCreate):
    datos = await leer_base_datos()
    for dato in datos:
        if dato["codigo"] == producto.codigo:
            raise HTTPException(status_code=400, detail="El código de producto ya existe.")
    nuevo_producto = producto.model_dump()
    datos.append(nuevo_producto)
    await guardar_base_datos(datos)
    return {"mensaje": "Producto registrado correctamente", "producto": nuevo_producto}

@apiRest.put("/productos/{codigo_producto}")
async def actualizar_producto(codigo_producto: str, producto_actualizado: ProductoCreate):
    datos = await leer_base_datos()
    for posicion, dato in enumerate(datos):
        if dato["codigo"] == codigo_producto:
            datos[posicion] = producto_actualizado.model_dump()
            datos[posicion]["codigo"] = codigo_producto
            await guardar_base_datos(datos)
            return {"mensaje": "Producto actualizado", "producto": datos[posicion]}
    raise HTTPException(status_code=404, detail="Producto no encontrado")