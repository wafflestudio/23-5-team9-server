from typing import Annotated
from fastapi import APIRouter, Depends, Query, status

from carrot.app.auth.exceptions import InvalidAccountException
from carrot.app.auth.utils import login_with_header
from carrot.app.pay.models import Ledger, TransactionType
from carrot.app.pay.schemas import (
    BalanceRequest,
    TransactionResponse,
    TransferRequest,
    TransferResponse,
    create_transaction_response,
)
from carrot.app.pay.services import PayService
from carrot.app.user.models import User

pay_router = APIRouter()


@pay_router.post("/{user_id}/deposit", status_code=status.HTTP_201_CREATED)
async def deposit(
    user_id: str,
    user: Annotated[User, Depends(login_with_header)],
    request: BalanceRequest,
    pay_service: Annotated[PayService, Depends()],
) -> TransactionResponse:
    if user.id != user_id:
        raise InvalidAccountException()

    ledger = await pay_service.deposit(user=user, **request.model_dump())
    return create_transaction_response(ledger)


@pay_router.post("/{user_id}/withdraw", status_code=status.HTTP_201_CREATED)
async def withdraw(
    user_id: str,
    user: Annotated[User, Depends(login_with_header)],
    request: BalanceRequest,
    pay_service: Annotated[PayService, Depends()],
) -> TransactionResponse:
    if user.id != user_id:
        raise InvalidAccountException()

    ledger = await pay_service.withdraw(user=user, **request.model_dump())
    return create_transaction_response(ledger)


@pay_router.post("/{send_user_id}/transfer", status_code=status.HTTP_201_CREATED)
async def transfer(
    send_user_id: str,
    user: Annotated[User, Depends(login_with_header)],
    request: TransferRequest,
    pay_service: Annotated[PayService, Depends()],
) -> TransactionResponse:
    if user.id != send_user_id:
        raise InvalidAccountException()

    ledger = await pay_service.transfer(send_user=user, **request.model_dump())
    return create_transaction_response(ledger)


@pay_router.get("/{user_id}", status_code=status.HTTP_200_OK)
async def get_transactions(
    user_id: str,
    user: Annotated[User, Depends(login_with_header)],
    pay_service: Annotated[PayService, Depends()],
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[TransactionResponse]:
    if user.id != user_id:
        raise InvalidAccountException()

    ledgers = await pay_service.get_transactions(user=user, limit=limit, offset=offset)
    return [create_transaction_response(ledger) for ledger in ledgers]
