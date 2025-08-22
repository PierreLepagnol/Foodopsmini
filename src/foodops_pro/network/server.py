import asyncio
import json
from typing import Dict, Set

import websockets
from websockets.server import WebSocketServerProtocol


class GameServer:
    """Simple WebSocket server managing turn-based game state."""

    def __init__(self) -> None:
        self.clients: Set[WebSocketServerProtocol] = set()
        self.turn: int = 1
        self.ready: Dict[WebSocketServerProtocol, bool] = {}

    async def register(self, websocket: WebSocketServerProtocol) -> None:
        """Register a new client and send current state."""
        self.clients.add(websocket)
        self.ready[websocket] = False
        await websocket.send(json.dumps({"type": "state", "turn": self.turn}))

    async def unregister(self, websocket: WebSocketServerProtocol) -> None:
        self.clients.discard(websocket)
        self.ready.pop(websocket, None)

    async def broadcast(self, message: Dict) -> None:
        if not self.clients:
            return
        data = json.dumps(message)
        await asyncio.gather(*(ws.send(data) for ws in self.clients))

    async def handler(self, websocket: WebSocketServerProtocol) -> None:
        await self.register(websocket)
        try:
            async for msg in websocket:
                data = json.loads(msg)
                if data.get("type") == "ready":
                    self.ready[websocket] = True
                    if self.clients and all(self.ready.values()):
                        self.turn += 1
                        self.ready = {ws: False for ws in self.clients}
                        await self.broadcast({"type": "new_turn", "turn": self.turn})
        finally:
            await self.unregister(websocket)

    async def run(self, host: str = "localhost", port: int = 8765) -> None:
        """Run the websocket server forever."""
        async with websockets.serve(self.handler, host, port):
            await asyncio.Future()


def main() -> None:
    """CLI entry point for the game server."""
    server = GameServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
