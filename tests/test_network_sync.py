import time

from foodops_pro.network import GameServer, GameClient


def test_two_clients_synchronise_turns():
    server = GameServer()
    server.start()
    time.sleep(0.1)  # wait for server to be ready
    try:
        c1 = GameClient("ws://localhost:8765")
        c2 = GameClient("ws://localhost:8765")
        c1.connect()
        c2.connect()
        # start first turn
        c1.send_ready()
        c2.send_ready()
        t1 = c1.wait_for_turn()
        t2 = c2.wait_for_turn()
        assert t1 == t2 == 1
        # next turn
        c1.send_ready()
        c2.send_ready()
        t1 = c1.wait_for_turn()
        t2 = c2.wait_for_turn()
        assert t1 == t2 == 2
    finally:
        c1.close()
        c2.close()
        server.stop()
