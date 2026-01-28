from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
import boto3
import io

from carrot.app.auth.utils import login_with_header, partial_login_with_header
from carrot.app.user.models import User
from carrot.app.image.schemas import (
    ImageResponse,
)
from carrot.app.image.services import ImageService

image_router = APIRouter()

@image_router.post("/product", status_code=201, response_model=ImageResponse)
async def upload_product_image(
    service: Annotated[ImageService, Depends()],
    file: UploadFile = File(...),
) -> ImageResponse:
    image = await service.upload_image(
        file,
    )
    return ImageResponse.model_validate(image)

@image_router.post("/user", status_code=201, response_model=ImageResponse)
async def upload_profile_image(
    service: Annotated[ImageService, Depends()],
    file: UploadFile = File(...),
) -> ImageResponse:
    image = await service.upload_image(
        file,
    )
    return ImageResponse.model_validate(image)

@image_router.get("/product/{image_id}", status_code=200, response_model=ImageResponse)
async def view_product_image(
    service: Annotated[ImageService, Depends()],
    image_id: str
) -> ImageResponse:
    image = await service.view_image(image_id)
    
    return ImageResponse.model_validate(image)

@image_router.get("/user/{image_id}", status_code=200, response_model=ImageResponse)
async def view_profile_image(
    service: Annotated[ImageService, Depends()],
    image_id: str
) -> ImageResponse:
    image = await service.view_image(image_id)
    
    return ImageResponse.model_validate(image)