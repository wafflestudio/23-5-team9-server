from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

# 메시지 전송 요청
class MessageCreate(BaseModel):
    content: str

# 메시지 응답 형식
class MessageRead(BaseModel):
    id: int
    room_id: str
    sender_id: str
    content: str
    created_at: datetime
    is_read: bool

    class Config:
        from_attributes = True

# 채팅방 정보 응답
class ChatRoomRead(BaseModel):
    id: str
    user_one_id: str
    user_two_id: str
    created_at: datetime

    class Config:
        from_attributes = True

# 내 채팅방 목록 조회 응답 (리스트 화면용)
class ChatRoomListRead(BaseModel):
    room_id: str
    opponent_id: str
    opponent_nickname: Optional[str] = None      # 상대방 닉네임 (선택사항)
    opponent_profile_image: Optional[str] = None # 상대방 프로필 이미지 (선택사항)
    last_message: Optional[str] = None           # 마지막 메시지 내용
    last_message_at: Optional[datetime] = None   # 마지막 메시지 시간
    unread_count: int = 0                        # 안 읽은 메시지 수

    class Config:
        from_attributes = True

# 상대방 상태 확인 응답
class OpponentStatus(BaseModel):
    user_id: str
    nickname: Optional[str] = None
    profile_image: Optional[str] = None
    # 'status'는 기존 User 모델의 UserStatus Enum을 사용하거나 문자열로 처리
    status: str                                  
    last_active_at: Optional[datetime] = None    # 마지막 활동 시간 (필요 시)

    class Config:
        from_attributes = True