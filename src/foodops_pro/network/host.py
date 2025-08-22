"""Networking utilities to host multiplayer FoodOps sessions.

The :class:`GameServer` implemented here is intentionally lightweight.  It
uses ``asyncio`` to accept TCP connections from players and observers.
Players can send decisions or messages which are broadcast to all other
participants.  Observers receive the same messages but cannot send data back
other than optional chat text.  A :class:`~foodops_pro.core.leaderboard.Leaderboard`
instance is used to maintain a consolidated ranking of all connected players.
"""

from __future__ import annotations

import asyncio
import threading
from typing import Dict, Optional

from ..core.leaderboard import Leaderboard


class GameServer:
    """Basic asynchronous server for multiplayer sessions.

    Parameters
    ----------
    host:
        Interface to bind the server to. ``"0.0.0.0"`` by default so it can be
        reached from other machines on the network.
    port:
        TCP port to listen on.
    leaderboard:
        Optional :class:`Leaderboard` instance for sharing scores with the main
        game logic.  If omitted, a new instance is created.
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 8765, leaderboard: Optional[Leaderboard] = None):
        self.host = host
        self.port = port
        self.leaderboard = leaderboard or Leaderboard()
        self.players: Dict[str, asyncio.StreamWriter] = {}
        self.observers: Dict[str, asyncio.StreamWriter] = {}
        self._server: Optional[asyncio.AbstractServer] = None

    # ------------------------------------------------------------------
    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """Handle a newly connected client."""
        writer.write(b"role (player/observer): ")
        await writer.drain()
        role = (await reader.readline()).decode().strip().lower()

        writer.write(b"name: ")
        await writer.drain()
        name = (await reader.readline()).decode().strip()

        if role == "observer":
            self.observers[name] = writer
            writer.write(b"connected as observer\n")
        else:
            self.players[name] = writer
            self.leaderboard.set_score(name, 0)
            writer.write(b"connected as player\n")
        await writer.drain()

        try:
            while data := await reader.readline():
                msg = data.decode().strip()
                if role != "observer":
                    # Broadcast decision/message from player
                    self.broadcast(f"{name}: {msg}")
        finally:
            # Cleanup on disconnect
            if role == "observer":
                self.observers.pop(name, None)
            else:
                self.players.pop(name, None)
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass

    # ------------------------------------------------------------------
    async def start(self) -> None:
        """Start the server and serve forever."""
        self._server = await asyncio.start_server(self._handle_client, self.host, self.port)
        await self._server.serve_forever()

    def start_in_thread(self) -> None:
        """Launch the server in a background thread.

        This helper is convenient for integrating the asynchronous server with
        the synchronous game loop used by the current CLI interface.
        """

        def runner() -> None:
            asyncio.run(self.start())

        thread = threading.Thread(target=runner, daemon=True)
        thread.start()

    # ------------------------------------------------------------------
    def broadcast(self, message: str) -> None:
        """Send a message to all participants."""
        data = (message + "\n").encode()
        for writer in list(self.players.values()) + list(self.observers.values()):
            try:
                writer.write(data)
            except Exception:
                continue

    def broadcast_leaderboard(self) -> None:
        """Send the current ranking to all participants."""
        ranking = self.leaderboard.get_ranking()
        lines = [f"{i + 1}. {name} {score:.0f}" for i, (name, score) in enumerate(ranking)]
        self.broadcast("LEADERBOARD: " + "; ".join(lines))
