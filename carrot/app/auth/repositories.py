from typing import Annotated
from datetime import datetime

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from carrot.db.connection import get_db_session
from carrot.app.auth.models import BlockedToken


class AuthRepository:
    def __init__(self, session: Annotated[Session, Depends(get_db_session)]) -> None:
        self.session = session

    def block_refresh_token(self, token: str, exp: datetime) -> None:
        blocked_token = BlockedToken(token=token, expired_at=exp)
        self.session.add(blocked_token)
        self.session.flush()

    def get_blocked_token(self, token: str) -> BlockedToken | None:
        return self.session.scalar(
            select(BlockedToken).where(BlockedToken.token == token)
        )
