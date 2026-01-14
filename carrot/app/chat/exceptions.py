from carrot.common.exceptions import CarrotException

class ChatRoomNotFoundException(CarrotException):
    def __init__(self) -> None:
        super().__init__(
            status_code=404,
            error_code="CHAT_001",
            error_msg="채팅방을 찾을 수 없습니다.",
        )

class ChatRoomAccessDeniedException(CarrotException):
    def __init__(self) -> None:
        super().__init__(
            status_code=403,
            error_code="CHAT_002",
            error_msg="이 채팅방에 접근할 권한이 없습니다.",
        )