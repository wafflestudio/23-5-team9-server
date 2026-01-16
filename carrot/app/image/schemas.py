from functools import wraps
import re
from typing import Annotated, Callable, TypeVar, List
from fastapi import HTTPException, status
from pydantic import BaseModel, EmailStr, field_validator
from pydantic.functional_validators import AfterValidator

from carrot.common.exceptions import InvalidFormatException
from carrot.app.region.schemas import RegionResponse

class ProductImageRequest(BaseModel):
    image_url: str
    
class UserImageRequest(BaseModel):
    image_url: str
    
class ProductImageResponse(BaseModel):
    id: str
    image_url: str
    product_id: str

    class Config:
        from_attributes = True
        
class UserImageResponse(BaseModel):
    id: str
    image_url: str
    user_id: str

    class Config:
        from_attributes = True

