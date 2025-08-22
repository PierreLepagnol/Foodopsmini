import asyncio
import importlib.util
import json
import pathlib

import pytest

spec = importlib.util.spec_from_file_location(
    "session_server", pathlib.Path("src/foodops_pro/network/session_server.py")
)
session_server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(session_server)
SessionServer = session_server.SessionServer


@pytest.mark.asyncio
async def test_scoreboard_and_observer_receives_updates():
    server = SessionServer()
    srv = await server.start()
    async with srv:
        # connect observer
        reader_o, writer_o = await asyncio.open_connection("127.0.0.1", 8765)
        writer_o.write(json.dumps({"role": "observer", "name": "trainer"}).encode() + b"\n")
        await writer_o.drain()
        msg = await reader_o.readline()
        assert json.loads(msg.decode())["role"] == "observer"

        # connect player
        reader_p, writer_p = await asyncio.open_connection("127.0.0.1", 8765)
        writer_p.write(json.dumps({"role": "player", "name": "p1"}).encode() + b"\n")
        await writer_p.drain()
        msg = await reader_p.readline()
        assert json.loads(msg.decode())["role"] == "player"

        # send score update
        writer_p.write(json.dumps({"type": "score", "score": 10}).encode() + b"\n")
        await writer_p.drain()
        update = await reader_o.readline()
        data = json.loads(update.decode())
        assert data["type"] == "scoreboard"
        assert data["scores"]["p1"] == 10

        writer_p.close()
        await writer_p.wait_closed()
        writer_o.close()
        await writer_o.wait_closed()
    await server.stop()
