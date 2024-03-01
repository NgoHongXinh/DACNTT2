from fastapi import APIRouter

from api.endpoint.group import view

router = APIRouter()

router.include_router(router=view.router)


