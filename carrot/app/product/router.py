from typing import Annotated, List

from fastapi import APIRouter, Depends, Query

from carrot.app.auth.utils import login_with_header, partial_login_with_header, login_with_header_optional
from carrot.app.user.models import User
from carrot.app.product.models import Product, UserProduct
from carrot.app.product.schemas import (
    ProductPostRequest,
    ProductPatchRequest,
    ProductResponse,
)
from carrot.app.product.services import ProductService
from carrot.app.product.exceptions import ShouldLoginException

product_router = APIRouter()


@product_router.post("/", status_code=201, response_model=ProductResponse)
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

@product_router.patch("/{product_id}", status_code=200, response_model=ProductResponse)
async def update_post(
    product_id: str,
    user: Annotated[User, Depends(login_with_header)],
    request: ProductPatchRequest,
    service: Annotated[ProductService, Depends()],
) -> ProductResponse:
    product = await service.update_post(
        user.id,
        product_id,
        request.title,
        # request.images,
        request.content,
        request.price,
        request.category_id,
    )
    return ProductResponse.model_validate(product)

@product_router.get("/{product_id}", status_code=200, response_model=ProductResponse)
async def view_post(
    product_id: str,
    service: Annotated[ProductService, Depends()],
) -> ProductResponse:
    product = await service.view_post_by_product_id(product_id)
    
    return product 

@product_router.get("/", status_code=200, response_model=List[ProductResponse])
async def view_posts(
    service: Annotated[ProductService, Depends()],
    user: Annotated[User | None, Depends(login_with_header_optional)],
    user_id: str | None = Query(default = None, alias="seller"),
    keyword: str | None = Query(default = None, alias="search"),
) -> List[ProductResponse]:
    if user_id == "me":
        if user is None:
            raise ShouldLoginException
        user_id = user.id
            
    if user_id and keyword:
        return await service.view_posts_by_seller_keyword(user_id, keyword)
    
    if user_id:
        return await service.view_posts_by_seller(user_id)
    
    if keyword:
        return await service.view_posts_by_keyword(keyword)
    
    return await service.view_posts_all()

@product_router.delete("/{product_id}", status_code=200, response_model=None)
async def remove_post(
    product_id: str,
    user: Annotated[User, Depends(login_with_header)],
    service: Annotated[ProductService, Depends()],
):
    await service.remove_post(
        user.id,
        product_id,
    )
    
    return None