from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.sql import Subquery
from carrot.app.chat.models import ChatRoom, ChatMessage

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