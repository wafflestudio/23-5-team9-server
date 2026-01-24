from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, update, desc, func
from typing import List

from carrot.app.chat.models import ChatRoom, ChatMessage, User, GroupChatRoom, GroupChatMember
from carrot.app.chat.utils import (
    get_unread_count_subquery, 
    get_last_message_id_subquery, 
    parse_chat_room_list_data
)
from carrot.app.chat.exceptions import (
    ChatRoomNotFoundException, 
    ChatRoomAccessDeniedException
)

class ChatService:

    async def validate_room_access(self, 
        db: AsyncSession, 
        room_id: str, 
        user_id: str
        ) -> ChatRoom:
        
        # 유저가 해당 채팅방에 접근 권한이 있는지 확인하고, 있다면 방 객체를 반환합니다.
        stmt = select(ChatRoom).where(ChatRoom.id == room_id)
        result = await db.execute(stmt)
        room = result.scalar_one_or_none()

        # 1. 방이 존재하는지 확인
        if not room:
            raise ChatRoomNotFoundException()

        # 2. 유저가 방의 참여자인지 확인
        if room.user_one_id != user_id and room.user_two_id != user_id:
            raise ChatRoomAccessDeniedException()

        return room

    ### 1. 채팅방 생성 및 조회
    async def get_existing_room_or_create(self, 
        db: AsyncSession, 
        user_id: str, 
        opponent_id: str
        ) -> ChatRoom:
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
    async def save_new_message(self, 
        db: AsyncSession, 
        room_id: str, 
        sender_id: str, 
        content: str
        ) -> ChatMessage:
        await self.validate_room_access(db, room_id, sender_id)

        new_msg = ChatMessage(room_id=room_id, sender_id=sender_id, content=content)
        db.add(new_msg)
        await db.commit()
        await db.refresh(new_msg)
        return new_msg

    ### 4. 메시지 조회 (폴링용)
    async def get_messages_after_id(self, 
        db: AsyncSession, 
        room_id: str, 
        user_id: str, 
        last_id: int, 
        limit: int
        ) -> List[ChatMessage]:
        await self.validate_room_access(db, room_id, user_id)

        stmt = select(ChatMessage).where(
            and_(ChatMessage.room_id == room_id, ChatMessage.id > last_id)
        ).order_by(ChatMessage.id.asc()).limit(limit)
        
        result = await db.execute(stmt)
        return result.scalars().all()

    ### 5. 읽음 처리
    async def update_messages_read_status(self, 
        db: AsyncSession, 
        room_id: str, 
        user_id: str
        ):
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
    async def get_chat_partner_status(self, 
        db: AsyncSession, 
        room_id: str, 
        user_id: str
        ):
        room = await self.validate_room_access(db, room_id, user_id)

        # 방 조회
        room_stmt = select(ChatRoom).where(ChatRoom.id == room_id)
        room = (await db.execute(room_stmt)).scalar_one_or_none()
        if not room: return None
        
        opponent_id = room.user_two_id if room.user_one_id == user_id else room.user_one_id
        
        # 상대 유저 조회
        user_stmt = select(User).where(User.id == opponent_id)
        return (await db.execute(user_stmt)).scalar_one_or_none()
    
    ### 7. 오픈 그룹 채팅방 생성 (방장)
    async def create_open_group_room(self, 
        db: AsyncSession, 
        creator_id: str, 
        title: str, 
        description: str = None, 
        max_members: int = 100
        ) -> GroupChatRoom:
        
        # 1. 방 생성
        new_room = GroupChatRoom(
            title=title, 
            description=description, 
            max_members=max_members
        )
        db.add(new_room)
        await db.flush() # ID를 미리 할당받기 위해 flush 사용

        # 2. 생성자를 방장(is_admin=True)으로 멤버 등록
        admin_member = GroupChatMember(
            room_id=new_room.id, 
            user_id=creator_id, 
            is_admin=True
        )
        db.add(admin_member)
        
        await db.commit()
        await db.refresh(new_room)
        return new_room

    ### 8. 채팅방 참여하기 (Join)
    async def join_group_room(self, db: AsyncSession, room_id: str, user_id: str):
        # 1. 방 존재 여부 및 현재 인원 확인
        stmt = select(GroupChatRoom).where(GroupChatRoom.id == room_id)
        result = await db.execute(stmt)
        room = result.scalar_one_or_none()
        
        if not room:
            raise ChatRoomNotFoundException()

        # 2. 이미 참여 중인지 확인
        member_stmt = select(GroupChatMember).where(
            and_(GroupChatMember.room_id == room_id, GroupChatMember.user_id == user_id)
        )
        existing_member = (await db.execute(member_stmt)).scalar_one_or_none()
        if existing_member:
            return room # 이미 참여 중이면 그대로 반환

        # 3. 인원 제한 확인
        count_stmt = select(func.count()).select_from(GroupChatMember).where(GroupChatMember.room_id == room_id)
        current_count = (await db.execute(count_stmt)).scalar() or 0
        
        if current_count >= room.max_members:
            raise ChatRoomFullException() # 인원 초과 예외 발생

        # 4. 멤버 추가
        new_member = GroupChatMember(room_id=room_id, user_id=user_id, is_admin=False)
        db.add(new_member)
        await db.commit()
        return room

    ### 9. 참여자 목록 조회
    async def get_group_room_members(self, db: AsyncSession, room_id: str) -> List[GroupChatMember]:
        # 유저 정보(User 모델)까지 조인해서 가져오는 것이 좋습니다.
        stmt = (
            select(GroupChatMember)
            .where(GroupChatMember.room_id == room_id)
            .order_by(desc(GroupChatMember.is_admin), GroupChatMember.joined_at.asc())
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    ### 10. 채팅방 나가기 (방장 위임 로직 포함)
    async def leave_group_room(self, db: AsyncSession, room_id: str, user_id: str):
        # 1. 해당 유저가 이 방의 멤버인지 확인
        stmt = select(GroupChatMember).where(
            and_(GroupChatMember.room_id == room_id, GroupChatMember.user_id == user_id)
        )
        member = (await db.execute(stmt)).scalar_one_or_none()
        
        if not member:
            return # 참여 중인 멤버가 아니면 아무 작업 안 함

        is_admin = member.is_admin

        # 2. 방장인지 확인
        if is_admin:
            # 방장이 나가면 방 자체를 삭제 (Cascade 설정에 의해 멤버, 메시지도 함께 삭제됨)
            room_stmt = select(GroupChatRoom).where(GroupChatRoom.id == room_id)
            room = (await db.execute(room_stmt)).scalar_one_or_none()
            if room:
                await db.delete(room)
        else:
            # 일반 유저면 본인만 멤버 테이블에서 삭제
            await db.delete(member)

        await db.commit()

chat_service = ChatService()