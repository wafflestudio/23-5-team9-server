# from typing import Annotated

# from fastapi import APIRouter, Depends

# from carrot.app.auth.utils import login_with_header, partial_login_with_header
# from carrot.app.user.models import User
# from carrot.app.image.schemas import (
#     ProductImageRequest,
#     UserImageRequest,
#     ProductImageResponse,
#     UserImageResponse,
# )
# from carrot.app.image.services import ImageService

# image_router = APIRouter()


# @image_router.post("/me", status_code=201, response_model=ProductImageResponse)
# async def upload_product_image(
#     user: Annotated[User, Depends(login_with_header)],
#     request: ProductImageRequest,
#     service: Annotated[ImageService, Depends()],
# ) -> ProductImageResponse:
#     image = await service.upload_product_image(
#         request.image_url,
#     )
#     return ProductImageResponse.model_validate(image)

# @image_router.post("/me", status_code=201, response_model=UserImageResponse)
# async def upload_profile_image(
#     user: Annotated[User, Depends(login_with_header)],
#     request: UserImageRequest,
#     service: Annotated[ImageService, Depends()],
# ) -> UserImageResponse:
#     image = await service.upload_profile_image(
#         user.id,
#         request.image_url
#     )
#     return UserImageResponse.model_validate(image)

# from fastapi import FastAPI, File, UploadFile, HTTPException
# from fastapi.responses import StreamingResponse
# import boto3
# import io

# app = FastAPI()
# # 설정을 여기에 입력하세요
# BUCKET_NAME = "team9-image-database"
# s3_client = boto3.client('s3')
# @app.post("/upload")
# async def upload_image(file: UploadFile = File(...)):
#     try:
#         # S3에 바로 업로드
#         s3_client.upload_fileobj(
#             file.file,
#             BUCKET_NAME,
#             file.filename,
#             ExtraArgs={"ContentType": file.content_type}
#         )
#         return {"filename": file.filename, "status": "upload success"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    
# @app.get("/download/{file_name}")
# async def download_image(file_name: str):
#     try:
#         # S3에서 파일 객체 가져오기
#         file_obj = s3_client.get_object(Bucket=BUCKET_NAME, Key=file_name)
#         # 파일 내용을 스트림으로 반환 (브라우저에서 바로 확인 가능)
#         return StreamingResponse(
#             io.BytesIO(file_obj['Body'].read()),
#             media_type=file_obj.get('ContentType', 'application/octet-stream')
#         )
#     except Exception as e:
#         raise HTTPException(status_code=404, detail="File not found")
    
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)