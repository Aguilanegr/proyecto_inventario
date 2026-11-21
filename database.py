import aiofiles
import json
import os

ARCHIVO_DB = "taller.json"

async def leer_base_datos():
    try:
        async with aiofiles.open(ARCHIVO_DB, mode='r', encoding='utf-8') as f:
            contenido = await f.read()
            # Validamos si el archivo está vacíos
            if not contenido.strip():
                return []
            return json.loads(contenido)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

async def guardar_base_datos(datos):
    async with aiofiles.open(ARCHIVO_DB, mode='w', encoding='utf-8') as f:
        await f.write(json.dumps(datos, indent=4))

ARCHIVO ="mecanicos.json"

async def leer_mecanicos():
    if not os.path.exists(ARCHIVO):
        return[]
    with open(ARCHIVO, "r", encoding="utf-8") as f:
        return json.load(f)

async def guardar_mecanicos(datos):
    with open(ARCHIVO, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)
