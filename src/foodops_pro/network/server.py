"""Simple websocket game server managing turn state."""

from __future__ import annotations

import asyncio
import json
import threading
import time
from typing import Set

import websockets
from websockets.server import WebSocketServerProtocol


class GameServer:
    """Websocket server to synchronize turns between multiple clients."""

    def __init__(self, host: str = "localhost", port: int = 8765) -> None:
        self.host = host
        self.port = port
        self.current_turn = 0
        self.connected: Set[WebSocketServerProtocol] = set()
        self.ready: Set[WebSocketServerProtocol] = set()
        self._loop: asyncio.AbstractEventLoop | None = None
        self._thread: threading.Thread | None = None
        self._stop_event: asyncio.Event | None = None

    async def _handler(self, websocket: WebSocketServerProtocol) -> None:
        """Handle messages from a single client."""
        self.connected.add(websocket)
        await websocket.send(json.dumps({"turn": self.current_turn}))
        try:
            async for message in websocket:
                data = json.loads(message)
                if data.get("action") == "ready":
                    self.ready.add(websocket)
                    if self.ready == self.connected and self.connected:
                        self.current_turn += 1
                        self.ready.clear()
                        payload = json.dumps({"turn": self.current_turn})
                        await asyncio.gather(*(ws.send(payload) for ws in self.connected))
        finally:
            self.connected.discard(websocket)
            self.ready.discard(websocket)

    async def _serve(self) -> None:
        assert self._stop_event is not None
        async with websockets.serve(self._handler, self.host, self.port):
            await self._stop_event.wait()

    def start(self) -> None:
        """Start the server in a background thread."""
        if self._thread is not None:
            return

        self._loop = asyncio.new_event_loop()
        self._stop_event = asyncio.Event()

        def run() -> None:
            assert self._loop is not None
            asyncio.set_event_loop(self._loop)
            self._loop.run_until_complete(self._serve())

        self._thread = threading.Thread(target=run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the server."""
        if self._loop and self._stop_event:
            self._loop.call_soon_threadsafe(self._stop_event.set)
        if self._thread:
            self._thread.join()
            self._thread = None
            self._loop = None
            self._stop_event = None


if __name__ == "__main__":  # pragma: no cover - manual server launch
    server = GameServer()
    server.start()
    print(f"Game server listening on ws://{server.host}:{server.port}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()
