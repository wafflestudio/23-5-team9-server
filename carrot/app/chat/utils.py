from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.sql import Subquery
from carrot.app.chat.models import ChatRoom, ChatMessage
from fastapi import WebSocket, status, Query, Depends
from carrot.app.auth.utils import verify_and_decode_token

def get_unread_count_subquery(user_id: str) -> Subquery:
    """방별 안 읽은 메시지 개수를 계산하는 서브쿼리를 생성합니다."""
    return (
        select(
            ChatMessage.room_id,
            func.count(ChatMessage.id).label("unread_count")
        )
        .where(
            and_(
                ChatMessage.sender_id != user_id,
                ChatMessage.is_read == False
            )
        )
        .group_by(ChatMessage.room_id)
        .subquery()
    )

def get_last_message_id_subquery() -> Subquery:
    """방별 마지막 메시지 ID를 찾는 서브쿼리를 생성합니다."""
    return (
        select(
            ChatMessage.room_id,
            func.max(ChatMessage.id).label("last_msg_id")
        )
        .group_by(ChatMessage.room_id)
        .subquery()
    )

def parse_chat_room_list_data(rows: list, user_id: str) -> list[dict]:
    """DB 조회 결과를 딕셔너리 형태의 리스트로 변환합니다."""
    rooms = []
    for row in rows:
        room_obj, last_msg, last_at, unread_count = row
        # 상대방 ID 결정 로직
        opponent_id = room_obj.user_two_id if room_obj.user_one_id == user_id else room_obj.user_one_id
        
        rooms.append({
            "room_id": room_obj.id,
            "opponent_id": opponent_id,
            "last_message": last_msg,
            "last_message_at": last_at,
            "unread_count": unread_count
        })
    return rooms

async def get_token_from_websocket(
    websocket: WebSocket,
    token: str = Query(None) # ws://.../ws/room_id?token=JWT_TOKEN
):
    if token is None:
        # 토큰이 없으면 연결 거부
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return None
    
    # 토큰 복호화 및 사용자 검증 (기존 로직 활용)
    user_data = await verify_and_decode_token(token) 
    if not user_data:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return None
        
    return user_data # 유저 객체나 유저 정보 반환