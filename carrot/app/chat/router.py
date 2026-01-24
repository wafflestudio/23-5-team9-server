from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Annotated

from carrot.app.chat.models import GroupChatRoom
from carrot.app.chat.schemas import (
    ChatRoomRead, MessageRead, MessageCreate, ChatRoomListRead, OpponentStatus
)
from carrot.app.chat.services import chat_service 
from carrot.db.connection import get_db_session
from carrot.app.auth.utils import login_with_header
from carrot.app.user.models import User

# For WebSocket management
import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from carrot.db.connection import get_session_factory
from carrot.app.chat.manager import manager
from carrot.app.auth.utils import verify_and_decode_token
from carrot.app.auth.settings import AUTH_SETTINGS

from carrot.app.auth.exceptions import (
    InvalidTokenException,
)



chat_router = APIRouter()

### WebSocket 엔드포인트
@chat_router.websocket("/ws/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    room_id: str,
    session_factory: async_sessionmaker = Depends(get_session_factory)
):
    await websocket.accept()
    current_user_id = None
    
    try:
        # 1. [인증] 첫 메시지로 토큰 받기
        try:
            auth_data = await asyncio.wait_for(websocket.receive_json(), timeout=5.0)
            token = auth_data.get("token")
            
            # 테스트용 우회 로직
            if token == "test_token":
                current_user_id = "37875d15-4555-4897-b53e-eabebc5710a9"
            else:
                # 수정된 함수 호출: claims 반환
                claims = verify_and_decode_token(token, AUTH_SETTINGS.ACCESS_TOKEN_SECRET)
                # claims 내의 유저 식별자 추출 (보통 'sub'나 'user_id' 필드 사용)
                current_user_id = claims.get("sub") 
            
            if not current_user_id:
                raise InvalidTokenException()
                
        except (asyncio.TimeoutError, InvalidTokenException, Exception) as e:
            await websocket.close(code=4003) # Forbidden
            return

        # 2. 인증 성공 시 매니저 등록
        await manager.connect(websocket, room_id)

        # 3. 메인 대화 루프
        while True:
            data = await websocket.receive_json()
            
            async with session_factory() as session:
                try:
                    # DB 저장: current_user_id를 사용하여 저장
                    new_msg = await chat_service.save_new_message(
                        session, 
                        room_id=room_id, 
                        sender_id=current_user_id, 
                        content=data["content"]
                    )
                    await session.commit()
                    
                    # 브로드캐스트 (닉네임 등이 필요하면 session에서 유저를 한 번 조회해야 합니다)
                    await manager.broadcast_to_room(room_id, {
                        "message_id": new_msg.id,
                        "sender_id": current_user_id,
                        "content": new_msg.content,
                        "created_at": new_msg.created_at.isoformat()
                    })
                except Exception as e:
                    await session.rollback()
                    # 이 줄을 추가해서 정확히 어떤 에러인지 터미널에서 확인하세요!
                    print(f"❌ Message Save Error: {type(e).__name__} - {e}") 
                    import traceback
                    traceback.print_exc() # 상세 스택트레이스까지 출력
                    await websocket.send_json({"error": str(e)})

    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)

### 1대1 채팅방 관련 API 엔드포인트

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


### 그룹 채팅방 관련 API 엔드포인트

### 1. 오픈 채팅방 생성 (방장)
@chat_router.post("/rooms/group", response_model=ChatRoomRead)
async def create_open_group_room(
    room_in: GroupChatRoom, # title, description, max_members 포함
    current_user: Annotated[User, Depends(login_with_header)],
    db: AsyncSession = Depends(get_db_session)
):
    # creator_id를 방장으로 설정하여 방 생성
    return await chat_service.create_open_room(db, current_user.id, room_in)

### 2. 채팅방 참여 (유저)
@chat_router.post("/rooms/{room_id}/join")
async def join_chat_room(
    room_id: str,
    current_user: Annotated[User, Depends(login_with_header)],
    db: AsyncSession = Depends(get_db_session)
):
    # 인원 제한 체크 후 참여 로직
    return await chat_service.join_room(db, room_id, current_user.id)

### 3. 채팅방 나가기 / 강퇴
@chat_router.delete("/rooms/{room_id}/members/{user_id}")
async def remove_member(
    room_id: str,
    user_id: str, # 나 자신이면 'leave', 타인이면 'kick'
    current_user: Annotated[User, Depends(login_with_header)],
    db: AsyncSession = Depends(get_db_session)
):
    # 1. 본인이 나가는 경우: OK
    # 2. 타인을 강퇴하는 경우: current_user.is_admin 인지 확인 로직 필요
    await chat_service.remove_member(db, room_id, user_id, requester_id=current_user.id)
    return {"status": "success"}