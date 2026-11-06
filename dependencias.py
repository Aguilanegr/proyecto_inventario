from fastapi import HTTPException, Header, Query

async def verificar_api_key(x_api_key: str = Header(..., description="API Key secreta del taller")):
    if x_api_key != "Sena2026":
        raise HTTPException(status_code=401, detail="Acceso denegado. API key invalido")
    return x_api_key

async def parametros_paginacion(
    skip: int = Query(0, description="Cuantos registros saltar"),
    limit: int = Query(10, description="Limite de registros a devolver")
):
    return {"skip": skip, "limit": limit}

async def simular_base_datos():
    print("1. [DEPENDENCIA] Abriendo la conexion con el json...")
    yield "Conexion esta lista"
    print("3. [DEPENDENCIA] Cerrando archivo json y liberando memoria...")

async def verificar_gerente(x_role: str = Header(default=None, alias="x_Role")):
    if x_role != "gerente":
        raise HTTPException(status_code=403, detail="Acceso denegado se necesita rol de gerente")
    return x_role
async def vereficar_auditor(x_role: str = Header(default=None, alias="x_Role")):
    if x_role not in ["gerente", "auditor"]:
        raise HTTPException(status_code=403, detail="Acceso denegado se necesita rol de gerente o auditor")
    return x_role