from fastapi import APIRouter
from app.api import attendance

router = APIRouter()
router.include_router(attendance.router)
