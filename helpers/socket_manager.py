from fastapi import WebSocket
from typing import List
import json
from services import forum_service


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_user_list(self):
        users_list = await forum_service.get_online_users_list()

        data_to_send = [
            user.dict() if hasattr(user, "dict") else user for user in users_list
        ]

        json_data = json.dumps(
            {"type": "UPDATE_LIST", "users": data_to_send}, default=str
        )

        for connection in self.active_connections:
            try:
                await connection.send_text(json_data)
            except Exception:
                pass


manager = ConnectionManager()
