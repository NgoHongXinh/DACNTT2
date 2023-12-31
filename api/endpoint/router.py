from fastapi import APIRouter
from api.endpoint.user import router as user_route
from api.endpoint.authen import router as authen_route


router = APIRouter()
router.include_router(router=user_route.router, tags=['USER'])
router.include_router(router=authen_route.router, tags=['AUTHEN'])
