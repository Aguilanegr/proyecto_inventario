import json
import aiofiles
import asyncio

ARCHIVO_BD = "inventario.json"
db_lock = asyncio.Lock()

# === NUEVA CORRUTINA QUE TE PIDEN ===
async def alerta_stock_bajo(codigo, nombre, stock_actual):
    """
    Simula el envío de un correo al administrador.
    No bloquea la BD porque usa await.
    """
    print("\n" + "="*70)
    print(f" ¡ALERTA CRÍTICA DE STOCK BAJO! ")
    print(f"   CÓDIGO: {codigo} | PRODUCTO: {nombre}")
    print(f"   STOCK ACTUAL: {stock_actual} unidades")
    print(f"   >>> Enviando correo a admin@clinicaveterinaria.com...")
    
    await asyncio.sleep(2) # Simula el envío del correo
    
    print(f"   📧 CORREO ENVIADO: El producto '{nombre}' necesita reposición urgente.")
    print("="*70 + "\n")

async def leer_base_datos():
    try:
        async with aiofiles.open(ARCHIVO_BD, mode="r", encoding='utf-8') as f:
            contenido = await f.read()
            return json.loads(contenido)
    except FileNotFoundError:
        return []

async def guardar_base_datos(datos):
    async with aiofiles.open(ARCHIVO_BD, mode="w", encoding="utf-8") as f:
        await f.write(json.dumps(datos, indent=4))

# === CREATE === Post
async def crear_producto(codigo, nombre, stock, categoria):
    async with db_lock:
        # Simular latencia
        await asyncio.sleep(0.5)
        datos = await leer_base_datos()

        for dato in datos:
            if dato["codigo"] == codigo:
                raise ValueError(f"El producto con el código {codigo} ya existe.")

        nuevo_producto = {"codigo": codigo, "nombre": nombre, "stock": stock, "categoria": categoria}
        datos.append(nuevo_producto)
        await guardar_base_datos(datos)
        
        # Si nace con stock bajo, alertamos
        if stock < 5:
            asyncio.create_task(alerta_stock_bajo(codigo, nombre, stock))
        
        return nuevo_producto

# === READ === Get
async def obtener_producto(codigo):
    async with db_lock:
        await asyncio.sleep(0.2)
        datos = await leer_base_datos()
        for dato in datos:
            if dato["codigo"] == codigo:
                return dato
        raise KeyError(f"Producto {codigo} no ha sido encontrado.")

# === UPDATE === Put
async def actualizar_stock(nuevo_stock, codigo):
    producto_actualizado = None
    necesita_alerta = False
    
    async with db_lock:
        await asyncio.sleep(0.5)
        datos = await leer_base_datos()
        for dato in datos:
            if dato["codigo"] == codigo:
                dato["stock"] = nuevo_stock
                producto_actualizado = dato
                if nuevo_stock < 5:
                    necesita_alerta = True
                break
        
        if not producto_actualizado:
            raise KeyError(f"Producto {codigo} no ha sido encontrado.")
        
        await guardar_base_datos(datos)
    
    # Lanzamos la alerta FUERA del Lock para no bloquear la BD
    if necesita_alerta:
        asyncio.create_task(
            alerta_stock_bajo(codigo, producto_actualizado["nombre"], nuevo_stock)
        )
    
    return producto_actualizado

# === DELETE ===
async def eliminar_producto(codigo):
    async with db_lock:
        await asyncio.sleep(0.5)
        datos = await leer_base_datos()
        nuevos_datos = [dato for dato in datos if dato["codigo"] != codigo]

        if len(datos) == len(nuevos_datos):
            raise KeyError(f"Producto {codigo} no ha sido encontrado.")

        await guardar_base_datos(nuevos_datos)
        return True