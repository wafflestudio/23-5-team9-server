from carrot.common.exceptions import CarrotException
from fastapi import status


class AuctionAlreadyExistsError(CarrotException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="AUC_001",
            error_msg="Active auction already exists for this product.",
        )

class AuctionNotFoundError(CarrotException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="AUC_002",
            error_msg="Auction not found.",
        )

class NotAllowedActionError(CarrotException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="AUC_003",
            error_msg="Action not allowed on this auction.",
        )

class AuctionAlreadyFinishedError(CarrotException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="AUC_004",
            error_msg="The auction has already finished.",
        )

class BidTooLowError(CarrotException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="AUC_005",
            error_msg="The bid price is too low.",
        )