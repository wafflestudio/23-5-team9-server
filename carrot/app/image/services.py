from typing import Annotated
from fastapi import Depends
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
import boto3
import io
import uuid

from carrot.app.product.repositories import ProductRepository

from carrot.app.image.models import Image
from carrot.app.image.exceptions import FileUploadFailedException
from carrot.app.image.repositories import ImageRepository
from carrot.common.exceptions import InvalidFormatException

BUCKET_NAME = "team9-image-database"
s3_client = boto3.client('s3')

class ImageService:
    def __init__(self, image_repository: Annotated[ImageRepository, Depends()]) -> None:
        self.repository = image_repository

    async def upload_image(self, file) -> Image:       
        image_id = str(uuid.uuid4())
        file_extension = file.filename.split(".")[-1]
        s3_filename = f"{image_id}.{file_extension}"
        
        try:
            s3_client.upload_fileobj(
                file.file,
                BUCKET_NAME,
                s3_filename,
                ExtraArgs={"ContentType": file.content_type}
            )
            file_url = f"https://{BUCKET_NAME}.s3.ap-northeast-2.amazonaws.com/{s3_filename}"
        
        except Exception as e:
            raise FileUploadFailedException
                    
        image = Image(
            id = image_id,
            image_url = file_url
        )
        
        new = await self.repository.upload_image(image)
        return new
    
    async def view_image(self, image_id: str) -> Image:              
        image = await self.repository.get_image_by_image_id(image_id)
        
        return image
    
    async def remove_product_image(self, image_id: str) -> None:
        image = await self.repository.get_image_by_image_id(image_id)
        
        await self.repository.remove_image(image)