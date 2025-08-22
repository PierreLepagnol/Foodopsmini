"""Online review mechanics affecting restaurant reputation."""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Optional

from .restaurant import Restaurant


@dataclass
class Review:
    rating: Decimal  # 0-5 stars
    comment: Optional[str] = None


@dataclass
class ReviewManager:
    reviews: List[Review] = field(default_factory=list)

    def add_review(self, restaurant: Restaurant, rating: Decimal, comment: str | None = None) -> Decimal:
        """Add a review and update restaurant reputation.

        The rating is on a 0-5 scale and mapped to the restaurant reputation (0-10).
        A simple moving average (80% previous reputation, 20% new rating) is used.
        Returns the updated reputation.
        """
        review = Review(rating=rating, comment=comment)
        self.reviews.append(review)
        mapped = rating * Decimal("2")  # convert 0-5 -> 0-10
        restaurant.reputation = (restaurant.reputation * Decimal("0.8") + mapped * Decimal("0.2"))
        restaurant.customer_satisfaction_history.append(mapped)
        return restaurant.reputation
