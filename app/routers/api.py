from fastapi import APIRouter
from app.routers import events

api_router = APIRouter()

# Register the events router
api_router.include_router(events.router)
