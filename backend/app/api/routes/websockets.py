# backend/app/api/routes/websockets.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.api.ws_manager import manager

router = APIRouter(prefix="/ws", tags=["WebSockets"])

@router.websocket("/progress/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(client_id, websocket)
    try:
        while True:
            # We don't expect messages from client, but keep connection open
            data = await websocket.receive_text()
            if data == "ping":
                await manager.send_personal_message("pong", client_id)
    except WebSocketDisconnect:
        manager.disconnect(client_id)
