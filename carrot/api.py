from fastapi import APIRouter

from carrot.app.auth.router import auth_router
from carrot.app.user.router import user_router
from carrot.app.chat.router import chat_router
from carrot.app.product.router import product_router
# from carrot.app.chat.websocket import chat_ws_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(user_router, prefix="/user", tags=["user"])
api_router.include_router(chat_router, prefix="/chat", tags=["chat"])
api_router.include_router(product_router, prefix="/product", tags=["product"])
# api_router.include_router(chat_ws_router, prefix="/ws", tags=["chat"])

