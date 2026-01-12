from fastapi import APIRouter

from carrot.app.auth.router import auth_router
from carrot.app.user.router import user_router
from carrot.app.region.router import region_router
from carrot.app.pay.router import pay_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(user_router, prefix="/user", tags=["user"])
api_router.include_router(region_router, prefix="/region", tags=["region"])
api_router.include_router(pay_router, prefix="/pay", tags=["pay"])
