from sqlalchemy import select, func, update, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import ChatRoom, UserChatRoom, ChatMessage, User
from app.api.chat import schemas
import uuid

# 1. 채팅방 목록 조회 (마지막 메시지 & 안 읽은 개수 포함)
async def get_rooms_for_user(db: AsyncSession, user_id: str):
    # 유저가 참여 중인 모든 방 ID 가져오기
    room_query = select(UserChatRoom).where(UserChatRoom.user_id == user_id)
    result = await db.execute(room_query)
    user_rooms = result.scalars().all()
    
    room_list = []
    for user_room in user_rooms:
        room_id = user_room.chat_room_id
        
        # 1-1. 마지막 메시지 가져오기
        last_msg_query = (
            select(ChatMessage)
            .where(ChatMessage.chatroom_id == room_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(1)
        )
        last_msg_result = await db.execute(last_msg_query)
        last_msg = last_msg_result.scalars().first()
        
        # 1-2. 안 읽은 메시지 개수 카운트
        # 내가 아닌 사람이 보낸 메시지 중 read_count가 특정 조건인 것 등 로직에 따라 조절
        unread_query = (
            select(func.count(ChatMessage.id))
            .where(
                and_(
                    ChatMessage.chatroom_id == room_id,
                    ChatMessage.sender_id != user_id,
                    ChatMessage.read_count > 0 # 혹은 is_read 필드 활용
                )
            )
        )
        unread_result = await db.execute(unread_query)
        unread_count = unread_result.scalar() or 0
        
        # 1-3. 상대방 정보 가져오기 (방 멤버 중 내가 아닌 사람)
        opponent_query = (
            select(User)
            .join(UserChatRoom)
            .where(
                and_(
                    UserChatRoom.chat_room_id == room_id,
                    UserChatRoom.user_id != user_id
                )
            )
        )
        opponent_result = await db.execute(opponent_query)
        opponent = opponent_result.scalars().first()
        
        room_list.append({
            "room_id": room_id,
            "opponent_nickname": opponent.nickname if opponent else "알 수 없는 사용자",
            "last_message": last_msg.message if last_msg else None,
            "last_message_at": last_msg.created_at if last_msg else None,
            "unread_count": unread_count
        })
        
    return room_list

# 2. 채팅 메시지 저장 (웹소켓에서 사용)
async def save_chat_message(db: AsyncSession, room_id: str, sender_id: str, content: str):
    new_msg = ChatMessage(
        chatroom_id=room_id,
        sender_id=sender_id,
        message=content,
        read_count=1 # 자신을 제외한 읽어야 할 사람 수
    )
    db.add(new_msg)
    
    # 해당 방의 다른 유저들에게 '안 읽은 메시지 있음' 표시(has_unread) 업데이트
    await db.execute(
        update(UserChatRoom)
        .where(and_(UserChatRoom.chat_room_id == room_id, UserChatRoom.user_id != sender_id))
        .values(has_unread=True)
    )
    
    await db.commit()
    await db.refresh(new_msg)
    return new_msg

# 3. 과거 메시지 조회 (페이징)
async def get_messages_by_room(db: AsyncSession, room_id: str, limit: int, offset: int):
    query = (
        select(ChatMessage)
        .where(ChatMessage.chatroom_id == room_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(query)
    messages = result.scalars().all()
    return messages[::-1] # 시간순 정렬을 위해 뒤집어서 반환

# 4. 읽음 처리
async def mark_as_read(db: AsyncSession, room_id: str, user_id: str):
    # 1. 내 UserChatRoom의 has_unread를 False로
    await db.execute(
        update(UserChatRoom)
        .where(and_(UserChatRoom.chat_room_id == room_id, UserChatRoom.user_id == user_id))
        .values(has_unread=False)
    )
    
    # 2. 상대방이 보낸 메시지들의 read_count 감소 (로직에 따라)
    # 실제로는 '어디까지 읽었는지' 저장하는 방식을 더 추천하지만 우선 단순 업데이트
    await db.commit()