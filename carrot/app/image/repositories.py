# from typing import Annotated

# from fastapi import Depends
# from sqlalchemy import select, and_
# from sqlalchemy.ext.asyncio import AsyncSession

# from carrot.app.user.models import LocalAccount, SocialAccount, User
# from carrot.app.image.models import ProductImage
# from carrot.db.connection import get_db_session


# class ImageRepository:
#     def __init__(self, session: Annotated[AsyncSession, Depends(get_db_session)]) -> None:
#         self.session = session

#     async def upload_product_image(self, image: ProductImage) -> ProductImage:
#         self.session.add(image)
#         await self.session.commit()
#         await self.session.refresh(image)
#         return image

# async def upload_profile_image(self, image: UserImage) -> UserImage:
#     self.session.add(image)
#     await self.session.commit()
#     await self.session.refresh(image)
#     return image