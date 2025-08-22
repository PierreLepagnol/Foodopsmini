import asyncio
import json
from typing import Optional

import websockets


class NetworkClient:
    """WebSocket client used by the CLI to synchronise turns."""

    def __init__(self, uri: str) -> None:
        self.uri = uri
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.turn: int = 1

    async def _connect(self) -> None:
        self.websocket = await websockets.connect(self.uri)
        state = json.loads(await self.websocket.recv())
        self.turn = state.get("turn", 1)

    def connect(self) -> None:
        asyncio.run(self._connect())

    async def _sync(self) -> int:
        assert self.websocket is not None
        await self.websocket.send(json.dumps({"type": "ready"}))
        while True:
            msg = json.loads(await self.websocket.recv())
            if msg.get("type") == "new_turn":
                self.turn = msg["turn"]
                return self.turn

    def sync_turn(self) -> int:
        return asyncio.run(self._sync())
