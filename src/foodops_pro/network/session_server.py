"""Asynchronous TCP session server with scoreboard and observer support."""

import asyncio
import json
from typing import Dict, List


class SessionServer:
    """Host a multiplayer session.

    Players and observers connect via a simple newline-delimited JSON protocol. Each
    client must send an initial JSON object declaring its ``role`` (``player`` or
    ``observer``) and a ``name``. Players can then send decisions or score updates
    which are broadcast to all observers.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 8765):
        self.host = host
        self.port = port
        self.players: Dict[str, asyncio.StreamWriter] = {}
        self.observers: List[asyncio.StreamWriter] = []
        self.scores: Dict[str, float] = {}
        self.decisions: Dict[str, List[str]] = {}
        self._server: asyncio.AbstractServer | None = None

    async def _send(self, writer: asyncio.StreamWriter, message: Dict[str, object]) -> None:
        writer.write((json.dumps(message) + "\n").encode())
        await writer.drain()

    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            raw = await reader.readline()
            data = json.loads(raw.decode().strip())
        except Exception:
            writer.close()
            await writer.wait_closed()
            return

        role = data.get("role")
        name = data.get("name", "")
        if role == "player":
            self.players[name] = writer
            self.scores.setdefault(name, 0.0)
            self.decisions.setdefault(name, [])
            await self._send(writer, {"type": "joined", "role": "player"})
        elif role == "observer":
            self.observers.append(writer)
            await self._send(writer, {"type": "joined", "role": "observer"})
        else:
            writer.close()
            await writer.wait_closed()
            return

        try:
            while not reader.at_eof():
                raw = await reader.readline()
                if not raw:
                    break
                payload = json.loads(raw.decode().strip())
                if role == "player" and payload.get("type") == "decision":
                    decision = payload.get("decision")
                    self.decisions[name].append(decision)
                    await self.broadcast({
                        "type": "decision",
                        "player": name,
                        "decision": decision,
                    })
                elif role == "player" and payload.get("type") == "score":
                    score = float(payload.get("score", 0))
                    self.scores[name] = score
                    await self.broadcast({"type": "scoreboard", "scores": self.scores})
        finally:
            if role == "player":
                self.players.pop(name, None)
                self.scores.pop(name, None)
                self.decisions.pop(name, None)
            elif role == "observer":
                if writer in self.observers:
                    self.observers.remove(writer)
            writer.close()
            await writer.wait_closed()

    async def broadcast(self, message: Dict[str, object]) -> None:
        for obs in list(self.observers):
            try:
                await self._send(obs, message)
            except Exception:
                if obs in self.observers:
                    self.observers.remove(obs)

    async def start(self) -> asyncio.AbstractServer:
        """Start the TCP server."""
        self._server = await asyncio.start_server(self._handle_client, self.host, self.port)
        return self._server

    async def stop(self) -> None:
        if self._server is not None:
            self._server.close()
            await self._server.wait_closed()
            self._server = None


async def main(host: str = "127.0.0.1", port: int = 8765) -> None:
    server = SessionServer(host, port)
    srv = await server.start()
    async with srv:
        await srv.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
