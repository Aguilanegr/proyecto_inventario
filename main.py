import asyncio
from database import crear_producto, obtener_producto, actualizar_stock, eliminar_producto, leer_base_datos, guardar_base_datos

async def procesar_venta(codigo, cantidad_a_vender):
    """
    Intenta vender. Aquí es donde se fuerza el ValueError
    """
    try:
        print(f"\n[VENTA] Intentando vender {cantidad_a_vender} de {codigo}...")
        
        producto = await obtener_producto(codigo)
        stock_actual = producto["stock"]

        if cantidad_a_vender > stock_actual:
            raise ValueError(f"Stock insuficiente para {codigo}. Pedido: {cantidad_a_vender}, Disponible: {stock_actual}")

        nuevo_stock = stock_actual - cantidad_a_vender
        await actualizar_stock(nuevo_stock, codigo)
        
        print(f"    VENTA EXITOSA: {codigo} - {producto['nombre']} | Vendidas: {cantidad_a_vender} | Stock restante: {nuevo_stock}")
        return True

    except ValueError as e:
        print(f"    VENTA FALLIDA ATRAPADA: {e}")
        return False
    except KeyError as e:
        print(f"    ERROR: {e}")
        return False
    except Exception as e:
        print(f"    ERROR INESPERADO: {e}")
        return False

async def prueba_de_estres():
    print("--- Iniciando prueba de estrés ---")
    
    await guardar_base_datos([])

    tareas_creacion = [
        crear_producto("M001", "Llanta trasera", 10),
        crear_producto("M002", "Filtro de aire", 25),
        crear_producto("M003", "Bujía", 50),
    ]

    try:
        await asyncio.gather(*tareas_creacion)
        print("Productos creados exitosamente")
    except Exception as e:
        print(f"Error de creación (normal si ya existían): {e}")

    print("\n" + "="*50)
    print("INICIANDO 4 VENTAS SIMULTÁNEAS CON asyncio.gather()")
    print("="*50)

    ventas_simultaneas = [
        procesar_venta("M001", 2),
        procesar_venta("M002", 23),
        procesar_venta("M003", 60),
        procesar_venta("M001", 1)
    ]

    await asyncio.gather(*ventas_simultaneas)

    print("\n" + "="*50)
    print("Prueba terminada. Esperando 3 segundos para ver alertas en segundo plano...")
    print("="*50)    
    await asyncio.sleep(3)

    datos_finales = await leer_base_datos()
    print("\n--- INVENTARIO FINAL ---")
    for p in datos_finales:
        print(p)

asyncio.run(prueba_de_estres())