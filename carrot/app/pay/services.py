from datetime import datetime
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from carrot.app.pay.exceptions import CoinLackException, ReceiverNotFoundException
from carrot.app.pay.models import Ledger
from carrot.app.pay.repositories import PayRepository
from carrot.app.pay.models import TransactionType
from carrot.app.user.models import User
from carrot.app.user.repositories import UserRepository
from carrot.db.connection import get_db_session


class PayService:
    def __init__(
        self,
        pay_repository: Annotated[PayRepository, Depends()],
        user_repository: Annotated[UserRepository, Depends()],
        session: Annotated[AsyncSession, Depends(get_db_session)],
    ) -> None:
        self.pay_repository = pay_repository
        self.user_repository = user_repository
        self.session = session

    async def deposit(self, amount: int, description: str, user: User) -> Ledger:
        async with self.session.begin_nested():
            ledger = Ledger(
                transaction_type=TransactionType.DEPOSIT,
                amount=amount,
                description=description,
                time=datetime.now(),
                user_id=user.id,
                receive_user_id=None,
            )
            await self.pay_repository.add_ledger(ledger)

            locked_user = await self.user_repository.get_user_for_update(user.id)
            if not locked_user:
                raise RuntimeError(f"User {user.id} disappeared during transaction.")
            locked_user.coin += amount
            await self.user_repository.update_user(locked_user)
            return ledger

    async def withdraw(self, amount: int, description: str, user: User) -> Ledger:
        async with self.session.begin_nested():
            ledger = Ledger(
                transaction_type=TransactionType.WITHDRAW,
                amount=amount,
                description=description,
                time=datetime.now(),
                user_id=user.id,
                receive_user_id=None,
            )
            await self.pay_repository.add_ledger(ledger)

            locked_user = await self.user_repository.get_user_for_update(user.id)
            if not locked_user:
                raise RuntimeError(f"User {user.id} disappeared during transaction.")

            if locked_user.coin <= amount:
                raise CoinLackException()
            locked_user.coin -= amount

            await self.user_repository.update_user(locked_user)
            return ledger

    async def transfer(
        self, amount: int, description: str, receive_user_id: str, send_user: User
    ) -> Ledger:
        async with self.session.begin_nested():
            ledger = Ledger(
                transaction_type=TransactionType.TRANSFER,
                amount=amount,
                description=description,
                time=datetime.now(),
                user_id=send_user.id,
                receive_user_id=receive_user_id,
            )
            await self.pay_repository.add_ledger(ledger)

            send_user_locked = await self.user_repository.get_user_for_update(
                send_user.id
            )
            if not send_user_locked:
                raise RuntimeError(
                    f"User {send_user.id} disappeared during transaction."
                )

            receive_user_locked = await self.user_repository.get_user_for_update(
                receive_user_id
            )
            if not receive_user_locked:
                raise ReceiverNotFoundException()

            if send_user_locked.coin <= amount:
                raise CoinLackException()
            send_user_locked.coin -= amount

            receive_user_locked.coin += amount

            await self.user_repository.update_user(send_user_locked)
            await self.user_repository.update_user(receive_user_locked)

            return ledger

    async def get_transactions(self, user: User, limit: int, offset: int):
        return await self.pay_repository.get_ledgers(user.id, limit, offset)
