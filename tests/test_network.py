import asyncio
import json
from contextlib import suppress

import pytest
import websockets

from foodops_pro.network.server import GameServer


@pytest.mark.asyncio
async def test_turn_synchronisation():
    server = GameServer()

    async def run():
        await server.run(host="localhost", port=8765)

    task = asyncio.create_task(run())
    await asyncio.sleep(0.1)

    async with websockets.connect("ws://localhost:8765") as c1, websockets.connect(
        "ws://localhost:8765"
    ) as c2:
        state1 = json.loads(await c1.recv())
        state2 = json.loads(await c2.recv())
        assert state1["turn"] == 1
        assert state2["turn"] == 1

        await c1.send(json.dumps({"type": "ready"}))
        await c2.send(json.dumps({"type": "ready"}))

        msg1 = json.loads(await c1.recv())
        msg2 = json.loads(await c2.recv())
        assert msg1["turn"] == 2
        assert msg2["turn"] == 2

    task.cancel()
    with suppress(asyncio.CancelledError):
        await task
