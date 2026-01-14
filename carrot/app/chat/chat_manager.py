# from fastapi import WebSocket
# from collections import defaultdict

# class ConnectionManager:
#     def __init__(self):
#         # 방 ID별로 연결된 소켓 리스트 관리 {room_id: [ws1, ws2, ...]}
#         self.active_connections: dict[str, list[WebSocket]] = defaultdict(list)

#     async def connect(self, websocket: WebSocket, room_id: str):
#         await websocket.accept()
#         self.active_connections[room_id].append(websocket)

#     def disconnect(self, websocket: WebSocket, room_id: str):
#         if websocket in self.active_connections[room_id]:
#             self.active_connections[room_id].remove(websocket)
#         if not self.active_connections[room_id]:
#             del self.active_connections[room_id]

#     async def send_personal_message(self, message: dict, websocket: WebSocket):
#         await websocket.send_json(message)

#     async def broadcast_to_room(self, room_id: str, message: dict):
#         # 해당 방에 접속 중인 모든 클라이언트에게 메시지 전송
#         for connection in self.active_connections.get(room_id, []):
#             await connection.send_json(message)

# manager = ConnectionManager()