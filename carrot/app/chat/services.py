from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, update, desc, func
from typing import List

from carrot.app.chat.models import ChatRoom, ChatMessage, User
from carrot.app.chat.utils import (
    get_unread_count_subquery, 
    get_last_message_id_subquery, 
    parse_chat_room_list_data
)

class ChatService:
    ### 1. 채팅방 생성 및 조회
    async def get_existing_room_or_create(self, db: AsyncSession, user_id: str, opponent_id: str) -> ChatRoom:
        stmt = select(ChatRoom).where(
            or_(
                and_(ChatRoom.user_one_id == user_id, ChatRoom.user_two_id == opponent_id),
                and_(ChatRoom.user_one_id == opponent_id, ChatRoom.user_two_id == user_id)
            )
        )
        result = await db.execute(stmt)
        room = result.scalars().first()

        if not room:
            room = ChatRoom(user_one_id=user_id, user_two_id=opponent_id)
            db.add(room)
            await db.commit()
            await db.refresh(room)
        return room

    ### 2. 내 채팅방 목록 불러오기
    async def get_user_chat_rooms(self, db: AsyncSession, user_id: str):
        unread_sub = get_unread_count_subquery(user_id)
        last_msg_sub = get_last_message_id_subquery()

        stmt = (
            select(
                ChatRoom,
                ChatMessage.content,
                ChatMessage.created_at,
                func.coalesce(unread_sub.c.unread_count, 0)
            )
            .outerjoin(last_msg_sub, ChatRoom.id == last_msg_sub.c.room_id)
            .outerjoin(ChatMessage, ChatMessage.id == last_msg_sub.c.last_msg_id)
            .outerjoin(unread_sub, ChatRoom.id == unread_sub.c.room_id)
            .where(or_(ChatRoom.user_one_id == user_id, ChatRoom.user_two_id == user_id))
            .order_by(desc(ChatMessage.created_at))
        )

        result = await db.execute(stmt)
        return parse_chat_room_list_data(result.all(), user_id)

    ### 3. 메시지 저장
    async def save_new_message(self, db: AsyncSession, room_id: str, sender_id: str, content: str) -> ChatMessage:
        new_msg = ChatMessage(room_id=room_id, sender_id=sender_id, content=content)
        db.add(new_msg)
        await db.commit()
        await db.refresh(new_msg)
        return new_msg

    ### 4. 메시지 조회 (폴링용)
    async def get_messages_after_id(self, db: AsyncSession, room_id: str, last_id: int, limit: int) -> List[ChatMessage]:
        stmt = select(ChatMessage).where(
            and_(ChatMessage.room_id == room_id, ChatMessage.id > last_id)
        ).order_by(ChatMessage.id.asc()).limit(limit)
        
        result = await db.execute(stmt)
        return result.scalars().all()

    ### 5. 읽음 처리
    async def update_messages_read_status(self, db: AsyncSession, room_id: str, user_id: str):
        stmt = update(ChatMessage).where(
            and_(
                ChatMessage.room_id == room_id,
                ChatMessage.sender_id != user_id,
                ChatMessage.is_read == False
            )
        ).values(is_read=True)
        
        await db.execute(stmt)
        await db.commit()

    ### 6. 상대방 상태 확인
    async def get_chat_partner_status(self, db: AsyncSession, room_id: str, user_id: str):
        # 방 조회
        room_stmt = select(ChatRoom).where(ChatRoom.id == room_id)
        room = (await db.execute(room_stmt)).scalar_one_or_none()
        if not room: return None
        
        opponent_id = room.user_two_id if room.user_one_id == user_id else room.user_one_id
        
        # 상대 유저 조회
        user_stmt = select(User).where(User.id == opponent_id)
        return (await db.execute(user_stmt)).scalar_one_or_none()

chat_service = ChatService()