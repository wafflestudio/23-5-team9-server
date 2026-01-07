from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

# --- 메시지 관련 스키마 ---

class ChatMessageResponse(BaseModel):
    id: int
    room_id: str
    sender_id: int
    sender_nickname: str
    content: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


# --- 채팅방 관련 스키마 ---

class ChatRoomCreate(BaseModel):
    """새로운 채팅방을 만들 때 필요한 정보 (예: 상품 ID 등)"""
    product_id: Optional[int] = None
    receiver_id: int  # 대화 상대방 ID


class ChatRoomResponse(BaseModel):
    """채팅방 생성 시 기본 반환 정보"""
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatRoomListResponse(BaseModel):
    """채팅 목록 페이지에서 보여줄 정보 (핵심!)"""
    room_id: str
    opponent_nickname: str  # 상대방 이름
    opponent_profile_img: Optional[str] = None
    
    # 실시간 업데이트를 위한 데이터
    last_message: Optional[str] = Field(None, description="마지막 메시지 내용")
    last_message_at: Optional[datetime] = Field(None, description="마지막 메시지 시간")
    unread_count: int = Field(0, description="읽지 않은 메시지 개수")

    class Config:
        from_attributes = True


# --- 웹소켓 메시지 전송 규격 ---

class ChatMessageCreate(BaseModel):
    """웹소켓을 통해 클라이언트가 보내는 데이터 형식"""
    message: str