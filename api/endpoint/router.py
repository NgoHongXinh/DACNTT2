from fastapi import APIRouter
from api.endpoint.user import router as user_route


router = APIRouter()
router.include_router(router=user_route.router)
