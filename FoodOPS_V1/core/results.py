from pydantic import BaseModel


class TurnResult(BaseModel):
    """Snapshot des principaux KPI d'un tour pour un restaurant."""

    restaurant_name: str
    tour: int
    clients_attribues: int
    clients_serv: int
    capacity: int
    price_med: float
    ca: float
    cogs: float
    fixed_costs: float
    marketing: float
    rh_cost: float
    funds_start: float
    funds_end: float
    losses: dict
