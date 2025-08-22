"""Utilities to build and export per-turn reports.

The report summarises:
- attractiveness factors (price, quality, waiting time),
- stock incidents (stockouts, promotions),
- customer reviews and reputation changes,
- market events or seasonality.

The module exposes helpers to generate the report structure, display it via a
``ConsoleUI`` instance and export it as JSON or plain text.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Any
import json

from ..domain.restaurant import Restaurant
from ..core.market import AllocationResult, MarketEngine
from .console_ui import ConsoleUI


@dataclass
class TurnReport:
    """Structured data for one game turn."""

    turn: int
    season: str
    events: List[str]
    restaurants: Dict[str, Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        """Return the report as a serialisable dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Serialise the report to JSON."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def to_text(self) -> str:
        """Format the report as a human readable block of text."""
        lines: List[str] = [f"Rapport du tour {self.turn} - Saison: {self.season}"]
        if self.events:
            lines.append("Événements de marché: " + ", ".join(self.events))
        for name, data in self.restaurants.items():
            lines.append("")
            lines.append(name)
            att = data["attractiveness"]
            lines.append(
                "  Attractivité | Prix: {price:.2f} Qualité: {quality:.2f} Attente: {waiting:.2f}".format(
                    price=float(att["price"]),
                    quality=float(att["quality"]),
                    waiting=float(att["waiting"]),
                )
            )
            stock = data["stock_incidents"]
            lines.append(
                f"  Stocks | Ruptures: {stock['stockouts']} Promotions: {stock['promotions']}"
            )
            rev = data["reviews"]
            lines.append(
                "  Avis | Note moyenne: {note:.2f} Δ Réputation: {delta:.2f}".format(
                    note=float(rev["average_review"]),
                    delta=float(rev["reputation_change"]),
                )
            )
        return "\n".join(lines)

    def export(self, directory: Path, fmt: str = "json") -> Path:
        """Export the report to *directory* in the given format.

        Args:
            directory: destination folder
            fmt: "json" (default) or "txt"
        """
        directory.mkdir(parents=True, exist_ok=True)
        suffix = "json" if fmt == "json" else "txt"
        path = directory / f"turn_{self.turn}.{suffix}"
        if fmt == "json":
            path.write_text(self.to_json(), encoding="utf-8")
        else:
            path.write_text(self.to_text(), encoding="utf-8")
        return path


def generate_turn_report(
    turn: int,
    restaurants: List[Restaurant],
    results: Dict[str, AllocationResult],
    market_engine: MarketEngine,
    month: int = 1,
) -> TurnReport:
    """Generate a :class:`TurnReport` from simulation data."""
    season = market_engine._get_season_name(month)  # type: ignore[attr-defined]
    events = [e.name for e in market_engine.competition_manager.active_events]

    report_data: Dict[str, Dict[str, Any]] = {}
    for r in restaurants:
        factors = market_engine._last_factors_by_restaurant.get(r.id, {})
        res = results.get(r.id)
        wait = Decimal("0")
        stockouts = 0
        if res:
            wait = max(Decimal("0"), Decimal("1") - res.utilization_rate)
            stockouts = res.lost_customers
        price_factor = factors.get("price_factor", Decimal("1"))
        quality_factor = factors.get("quality_factor", Decimal("1"))

        # Basic review mechanism: average of price & quality scaled to 10
        review = (price_factor + quality_factor) / 2 * Decimal("5")
        previous_rep = r.reputation
        r.customer_satisfaction_history.append(review)
        r.reputation = (r.reputation + review) / 2
        rep_change = r.reputation - previous_rep

        report_data[r.name] = {
            "attractiveness": {
                "price": price_factor,
                "quality": quality_factor,
                "waiting": wait,
            },
            "stock_incidents": {
                "stockouts": stockouts,
                "promotions": 0,
            },
            "reviews": {
                "average_review": review,
                "reputation_change": rep_change,
            },
        }

    return TurnReport(turn=turn, season=season, events=events, restaurants=report_data)


def display_turn_report(ui: ConsoleUI, report: TurnReport) -> None:
    """Display the report using the provided ``ConsoleUI`` instance."""
    ui.print_box(report.to_text().splitlines(), style="info")
