from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Annotated

from carrot.app.chat.models import ChatRoom, ChatMessage
from carrot.app.chat.schemas import (
    ChatRoomRead, MessageRead, MessageCreate, ChatRoomListRead, OpponentStatus
)
from carrot.app.chat.services import chat_service 
from carrot.db.connection import get_db_session
from carrot.app.auth.utils import login_with_header
from carrot.app.user.models import User


chat_router = APIRouter()

### 1. 채팅방 생성 및 조회
@chat_router.post("/rooms", response_model=ChatRoomRead)
async def get_or_create_room(
    opponent_id: str, 
    current_user: Annotated[User, Depends(login_with_header)], 
    db: AsyncSession = Depends(get_db_session)
):
    room = await chat_service.get_existing_room_or_create(db, current_user.id, opponent_id)
    return room

### 2. 내 채팅방 목록 불러오기
@chat_router.get("/rooms", response_model=List[ChatRoomListRead])
async def list_my_rooms(
    current_user: Annotated[User, Depends(login_with_header)],
    db: AsyncSession = Depends(get_db_session)
):
    # 각 방의 마지막 메시지와 안 읽은 메시지 수를 포함하는 로직이 들어갈 예정입니다.
    rooms = await chat_service.get_user_chat_rooms(db, current_user.id)
    return rooms

### 3. 메시지 전송
@chat_router.post("/rooms/{room_id}/messages", response_model=MessageRead)
async def send_message(
    room_id: str, 
    msg_in: MessageCreate, 
    current_user: Annotated[User, Depends(login_with_header)], 
    db: AsyncSession = Depends(get_db_session)
):
    new_msg = await chat_service.save_new_message(db, room_id, current_user.id, msg_in.content)
    return new_msg

### 4. 메시지 내역 및 업데이트 확인 (폴링)
@chat_router.get("/rooms/{room_id}/messages", response_model=List[MessageRead])
async def get_messages(
    room_id: str, 
    # 1. 인증된 유저 객체를 주입받습니다.
    current_user: Annotated[User, Depends(login_with_header)], 
    last_id: int = 0, 
    limit: int = 50, 
    db: AsyncSession = Depends(get_db_session)
):
    # 2. 서비스 함수에 current_user.id를 인자로 전달합니다.
    messages = await chat_service.get_messages_after_id(
        db, 
        room_id=room_id, 
        user_id=current_user.id, # 추가된 인자
        last_id=last_id, 
        limit=limit
    )
    return messages

### 5. 읽음 처리
@chat_router.patch("/rooms/{room_id}/messages/read")
async def mark_messages_as_read(
    room_id: str, 
    current_user: Annotated[User, Depends(login_with_header)], 
    db: AsyncSession = Depends(get_db_session)
):
    await chat_service.update_messages_read_status(db, room_id, current_user.id)
    return {"status": "success"}

### 6. 상대방 상태 확인
@chat_router.get("/rooms/{room_id}/status", response_model=OpponentStatus)
async def get_opponent_status(
    room_id: str, 
    current_user: Annotated[User, Depends(login_with_header)], 
    db: AsyncSession = Depends(get_db_session)
):
    # 상대방의 접속 여부나 마지막 확인 시간 등을 반환할 예정입니다.
    status_info = await chat_service.get_chat_partner_status(db, room_id, current_user.id)
    return status_info