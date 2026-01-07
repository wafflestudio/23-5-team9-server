from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.auth.utils import get_current_user  # 기존 인증 함수
from app.api.chat import schemas, service  # 로직 분리를 위한 service 계층 가정
from app.models import User

chat_router = APIRouter()

# 1. 내가 참여 중인 채팅방 목록 조회
@chat_router.get("/rooms", response_model=List[schemas.ChatRoomListResponse])
async def get_my_rooms(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    로그인한 유저가 참여하고 있는 모든 채팅방의 목록을 가져옵니다.
    마지막 메시지 내용과 읽지 않은 메시지 개수가 포함됩니다.
    """
    return await service.get_rooms_for_user(db, current_user.id)


# 2. 특정 채팅방의 과거 메시지 내역 조회
@chat_router.get("/rooms/{room_id}/messages", response_model=List[schemas.ChatMessageResponse])
async def get_room_messages(
    room_id: str,
    limit: int = 30,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    특정 방에 입장했을 때 이전 대화 내용을 불러옵니다. (페이징 처리)
    """
    return await service.get_messages_by_room(db, room_id, limit, offset)


# 3. 새로운 채팅방 생성 (예: 상품 상세 페이지에서 '채팅하기' 클릭 시)
@chat_router.post("/rooms", status_code=status.HTTP_201_CREATED, response_model=schemas.ChatRoomResponse)
async def create_chat_room(
    room_data: schemas.ChatRoomCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    새로운 채팅방을 만듭니다. 이미 방이 존재하면 기존 방 정보를 반환합니다.
    """
    return await service.create_or_get_room(db, room_data, current_user.id)


# 4. 메시지 읽음 처리
@chat_router.patch("/rooms/{room_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_messages_as_read(
    room_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    채팅방에 들어갔을 때, 상대방이 보낸 메시지들을 모두 '읽음' 상태로 변경합니다.
    """
    await service.mark_as_read(db, room_id, current_user.id)
    return None