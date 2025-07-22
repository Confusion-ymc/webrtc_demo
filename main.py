import asyncio
import json
import os
import uuid

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

ROOT = os.path.dirname(__file__)

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        # rooms[room_id][client_id] = websocket
        self.rooms: dict[str, dict[str, WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: str, client_id: str):
        await websocket.accept()
        if room_id not in self.rooms:
            self.rooms[room_id] = {}
        
        # Notify existing clients of the new peer
        existing_peers = list(self.rooms[room_id].keys())
        for peer_id, peer_ws in self.rooms[room_id].items():
            await peer_ws.send_text(json.dumps({"type": "new-peer", "peer_id": client_id}))

        # Add new client to the room
        self.rooms[room_id][client_id] = websocket

        # Notify the new client about existing peers
        await websocket.send_text(json.dumps({"type": "welcome", "client_id": client_id, "peers": existing_peers}))

    async def disconnect(self, room_id: str, client_id: str):
        if room_id in self.rooms:
            if client_id in self.rooms[room_id]:
                del self.rooms[room_id][client_id]
                if not self.rooms[room_id]:
                    del self.rooms[room_id]
            await self.broadcast(room_id, json.dumps({"type": "peer-left", "peer_id": client_id}))

    async def send_to_peer(self, room_id: str, client_id: str, message: str):
        if room_id in self.rooms and client_id in self.rooms[room_id]:
            await self.rooms[room_id][client_id].send_text(message)

    async def broadcast(self, room_id: str, message: str):
        if room_id in self.rooms:
            for client_ws in self.rooms[room_id].values():
                await client_ws.send_text(message)

manager = ConnectionManager()

@app.get("/")
async def get():
    return HTMLResponse(open(os.path.join(ROOT, "index.html")).read())

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    client_id = str(uuid.uuid4())
    await manager.connect(websocket, room_id, client_id)

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            message["from"] = client_id
            
            # Route message to the correct peer
            if "to" in message:
                await manager.send_to_peer(room_id, message["to"], json.dumps(message))

    except WebSocketDisconnect:
        await manager.disconnect(room_id, client_id)
