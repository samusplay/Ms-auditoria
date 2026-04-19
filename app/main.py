from contextlib import asynccontextmanager

from app.infrastructure.database import check_db_connection
from app.routers.api import api_router
from fastapi import FastAPI


#gestor de vida
@asynccontextmanager
async def lifespan(app:FastAPI):
    print("\033[94m⚙️  Configurando servicios internos...\033[0m")
    
    if check_db_connection():
        print("\033[92m✅ PERSISTENCIA: Conectado a PostgreSQL\033[0m")
    else:
        print("\033[91m🚨 PERSISTENCIA: Fallo al conectar a PostgreSQL\033[0m")
    
    yield
    print("\033[93m\nFinalizando procesos...\033[0m")

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import Request

#Instaciamos app
app=FastAPI(
    title="API Auditoría y Trazabilidad",
    description="Responsable de registrar y persistir eventos de auditoría de forma inmutable",
    lifespan=lifespan
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    missing_fields = []
    for error in exc.errors():
        if error["type"] == "missing" or error["type"] == "string_too_short":
            missing_fields.append(error["loc"][-1])
            
    return JSONResponse(
        status_code=400,
        content={
            "error": "Validation failed",
            "missing_fields": missing_fields
        }
    )

#llamada a rutas 
app.include_router(api_router)