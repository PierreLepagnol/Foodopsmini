"""Simple FastAPI server for hosting a FoodOps game.

This lightweight server allows teams to join a session, submit their
turn scores, display a ranking after each round and exchange messages
via a small discussion board.

It is intentionally minimalistic: the state is kept in memory and will be
reset every time the process restarts. The server is meant for small
workshop or classroom games where a quick way to synchronise players is
necessary without deploying heavy infrastructure.
"""

from __future__ import annotations

from datetime import datetime

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="FoodOps Light Server")


class JoinRequest(BaseModel):
    """Payload used when a team joins the game."""

    player_name: str


class SubmitRequest(BaseModel):
    """Payload sent at the end of a turn with the score of a player."""

    player_name: str
    score: int


class MessageRequest(BaseModel):
    """Payload for posting a message on the discussion wall."""

    player_name: str
    message: str


# --- In-memory state -----------------------------------------------------
players: dict[str, int] = {}
# Tracks whether a player has submitted its score for the current turn
turn_submissions: dict[str, bool] = {}
current_turn: int = 1
# List of dicts with keys: player, message, timestamp
messages: list[dict[str, str]] = []


@app.post("/join")
def join(req: JoinRequest) -> dict[str, object]:
    """Register a new player on the server.

    If the player already exists nothing happens and the current state is
    returned. The endpoint answers with the current turn number so the
    client can synchronise.
    """

    if req.player_name not in players:
        players[req.player_name] = 0
    return {"status": "ok", "current_turn": current_turn}


@app.post("/submit")
def submit(req: SubmitRequest) -> dict[str, object]:
    """Submit the result of a player for the current turn.

    The total score of the player is updated. When all registered players
    have submitted their score the server automatically advances to the
    next turn and clears the submission tracker.
    """

    global current_turn
    players.setdefault(req.player_name, 0)
    players[req.player_name] += req.score
    turn_submissions[req.player_name] = True

    if len(turn_submissions) == len(players):
        turn_submissions.clear()
        current_turn += 1

    return {"status": "ok", "current_turn": current_turn}


@app.get("/ranking")
def ranking() -> dict[str, object]:
    """Return the ranking ordered by total score."""

    ordered: list[tuple[str, int]] = sorted(
        players.items(), key=lambda item: item[1], reverse=True
    )
    return {"current_turn": current_turn, "ranking": ordered}


@app.post("/messages")
def post_message(req: MessageRequest) -> dict[str, str]:
    """Store a message on the discussion wall."""

    messages.append(
        {
            "player": req.player_name,
            "message": req.message,
            "timestamp": datetime.utcnow().isoformat(timespec="seconds"),
        }
    )
    return {"status": "ok"}


@app.get("/messages")
def get_messages() -> dict[str, list[dict[str, str]]]:
    """Retrieve all messages posted so far."""

    return {"messages": messages}
