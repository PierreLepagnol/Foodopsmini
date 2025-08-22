"""Blocking websocket client for turn synchronisation."""

from __future__ import annotations

import json

from websockets.sync.client import connect


class GameClient:
    """Simple client used by the CLI to talk with the :class:`GameServer`."""

    def __init__(self, uri: str) -> None:
        self.uri = uri
        self.connection = None

    def connect(self) -> int:
        """Connect to the server and return current turn."""
        self.connection = connect(self.uri)
        data = json.loads(self.connection.recv())
        return data.get("turn", 0)

    def send_ready(self) -> None:
        """Notify the server that the client finished its turn."""
        assert self.connection is not None
        self.connection.send(json.dumps({"action": "ready"}))

    def wait_for_turn(self) -> int:
        """Block until the server broadcasts the next turn."""
        assert self.connection is not None
        data = json.loads(self.connection.recv())
        return data.get("turn", 0)

    def close(self) -> None:
        if self.connection is not None:
            self.connection.close()
            self.connection = None
