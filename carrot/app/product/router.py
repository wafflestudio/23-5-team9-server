from typing import Annotated, List

from fastapi import APIRouter, Depends

from carrot.app.auth.utils import login_with_header, partial_login_with_header
from carrot.app.user.models import User
from carrot.app.product.models import Product, UserProduct
from carrot.app.product.schemas import (
    ProductPostRequest,
    ProductPatchRequest,
    ProductViewRequest,
    ProductDeleteRequest,
    ProductResponse,
)
from carrot.app.product.services import ProductService

product_router = APIRouter()


@product_router.post("/me", status_code=201, response_model=ProductResponse)
async def create_post(
    user: Annotated[User, Depends(login_with_header)],
    request: ProductPostRequest,
    service: Annotated[ProductService, Depends()],
) -> ProductResponse:
    product = await service.create_post(
        user.id,
        request.title,
        # request.images,
        request.content,
        request.price,
        request.category_id,
    )
    return ProductResponse.model_validate(product)

@product_router.patch("/me", status_code=200, response_model=ProductResponse)
async def update_post(
    user: Annotated[User, Depends(login_with_header)],
    request: ProductPatchRequest,
    service: Annotated[ProductService, Depends()],
) -> ProductResponse:
    product = await service.update_post(
        user.id,
        request.id,
        request.title,
        # request.images,
        request.content,
        request.price,
        request.category_id,
    )
    return ProductResponse.model_validate(product)

@product_router.get("/me", status_code=200, response_model=ProductResponse)
async def view_post(
    user: Annotated[User, Depends(login_with_header)],
    request: ProductViewRequest,
    service: Annotated[ProductService, Depends()],
) -> ProductResponse:
    product = await service.view_post(
        user.id,
        request.id,
    )
    return ProductResponse.model_validate(product)

@product_router.get("/", status_code=200, response_model=List[ProductResponse])
async def view_post_all(
    service: Annotated[ProductService, Depends()],
) -> List[ProductResponse]:
    products = await service.view_post_all()

    return products

@product_router.delete("/me", status_code=200, response_model=ProductResponse)
async def remove_post(
    user: Annotated[User, Depends(login_with_header)],
    request: ProductDeleteRequest,
    service: Annotated[ProductService, Depends()],
) -> ProductResponse:
    product = await service.remove_post(
        user.id,
        request.id,
    )
    return ProductResponse.model_validate(product)