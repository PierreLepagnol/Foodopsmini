"""Command line interface to start a FoodOps network host."""

from __future__ import annotations

import argparse

from .host import GameServer
from ..core.leaderboard import Leaderboard


def main() -> None:
    parser = argparse.ArgumentParser(description="FoodOps network server")
    parser.add_argument("--host", default="0.0.0.0", help="Interface to bind")
    parser.add_argument("--port", type=int, default=8765, help="TCP port")
    args = parser.parse_args()

    leaderboard = Leaderboard()
    server = GameServer(args.host, args.port, leaderboard)
    print(f"Starting server on {args.host}:{args.port} ...")
    server.start_in_thread()
    try:
        # Keep main thread alive
        import time

        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        print("Server stopped")


if __name__ == "__main__":
    main()
