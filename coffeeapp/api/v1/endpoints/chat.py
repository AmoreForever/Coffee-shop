from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
from jose import JWTError, jwt

router = APIRouter()

SECRET_KEY = "hikamoruru"
ALGORITHM = "HS256"

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

def get_username_from_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise JWTError
        return username
    except JWTError as e:
        print(f"Token decoding error: {e}")
        return None

@router.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    token = websocket.query_params.get("token")
    username = get_username_from_token(token)
    if username is None:
        print("Invalid token")
        await websocket.close()
        return

    await websocket.accept()
    await manager.connect(websocket)
    print(f"User {username} connected")
    try:
        while True:
            data = await websocket.receive_text()
            print(f"User {username} sent: {data}")
            await manager.broadcast(f"Message from {username}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print(f"User {username} disconnected")
        await manager.broadcast(f"User {username} disconnected.")
    except Exception as e:
        print(f"Error with user {username}: {e}")
        manager.disconnect(websocket) 
