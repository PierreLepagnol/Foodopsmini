"""
Système de marketing et communication pour FoodOps Pro.
"""

from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal
from enum import Enum


class CampaignType(Enum):
    """Types de campagnes marketing."""

    SOCIAL_MEDIA = "reseaux_sociaux"
    LOCAL_ADS = "publicite_locale"
    LOYALTY_PROGRAM = "programme_fidelite"
    EVENTS = "evenements"
    INFLUENCER = "influenceurs"
    TRADITIONAL = "medias_traditionnels"


class CampaignStatus(Enum):
    """Statut des campagnes."""

    PLANNED = "planifiee"
    ACTIVE = "active"
    COMPLETED = "terminee"
    CANCELLED = "annulee"


@dataclass
class MarketingCampaign:
    """
    Campagne marketing avec coûts et impacts.

    Attributes:
        id: Identifiant unique
        name: Nom de la campagne
        type: Type de campagne
        budget: Budget alloué
        duration_days: Durée en jours
        target_segments: Segments ciblés
        start_date: Date de début
        status: Statut actuel
        expected_reach: Portée attendue (nombre de personnes)
        expected_conversion: Taux de conversion attendu
    """

    id: str
    name: str
    type: CampaignType
    budget: Decimal
    duration_days: int
    target_segments: list[str] = field(default_factory=list)
    start_date: date | None = None
    status: CampaignStatus = CampaignStatus.PLANNED
    expected_reach: int = 0
    expected_conversion: Decimal = Decimal("0.02")  # 2% par défaut

    def __post_init__(self) -> None:
        """Validation des données."""
        if self.budget < 0:
            raise ValueError(f"Le budget doit être positif: {self.budget}")
        if self.duration_days <= 0:
            raise ValueError(f"La durée doit être positive: {self.duration_days}")
        if not (0 <= self.expected_conversion <= 1):
            raise ValueError(
                f"Le taux de conversion doit être entre 0 et 1: {self.expected_conversion}"
            )

    @property
    def daily_cost(self) -> Decimal:
        """Coût quotidien de la campagne."""
        return self.budget / Decimal(self.duration_days)

    @property
    def expected_new_customers(self) -> int:
        """Nombre de nouveaux clients attendus."""
        return int(self.expected_reach * self.expected_conversion)

    @property
    def cost_per_acquisition(self) -> Decimal:
        """Coût d'acquisition par client."""
        if self.expected_new_customers == 0:
            return Decimal("0")
        return self.budget / Decimal(self.expected_new_customers)

    def is_active(self, current_date: date) -> bool:
        """Vérifie si la campagne est active à une date donnée."""
        if self.status != CampaignStatus.ACTIVE or not self.start_date:
            return False

        end_date = self.start_date + timedelta(days=self.duration_days)
        return self.start_date <= current_date <= end_date

    def get_daily_impact(self, current_date: date) -> dict[str, Decimal]:
        """Calcule l'impact quotidien de la campagne."""
        if not self.is_active(current_date):
            return {
                "reach": Decimal("0"),
                "conversion": Decimal("0"),
                "cost": Decimal("0"),
            }

        daily_reach = Decimal(self.expected_reach) / Decimal(self.duration_days)
        daily_conversion = daily_reach * self.expected_conversion

        return {
            "reach": daily_reach,
            "conversion": daily_conversion,
            "cost": self.daily_cost,
        }


@dataclass
class CustomerReview:
    """Avis client avec impact sur réputation."""

    customer_id: str
    restaurant_id: str
    rating: Decimal  # 1-5 étoiles
    comment: str
    date: date
    platform: str = "google"  # google, tripadvisor, facebook, etc.
    verified: bool = False

    def __post_init__(self) -> None:
        """Validation des données."""
        if not (1 <= self.rating <= 5):
            raise ValueError(f"La note doit être entre 1 et 5: {self.rating}")

    @property
    def impact_weight(self) -> Decimal:
        """Poids de l'avis selon la plateforme et vérification."""
        base_weight = Decimal("1.0")

        # Bonus selon la plateforme
        platform_bonus = {
            "google": Decimal("1.2"),
            "tripadvisor": Decimal("1.1"),
            "facebook": Decimal("1.0"),
            "yelp": Decimal("1.1"),
        }.get(self.platform, Decimal("1.0"))

        # Bonus si vérifié
        verification_bonus = Decimal("1.3") if self.verified else Decimal("1.0")

        return base_weight * platform_bonus * verification_bonus


class MarketingManager:
    """Gestionnaire du marketing et de la communication."""

    def __init__(self):
        self.campaigns: list[MarketingCampaign] = []
        self.reviews: list[CustomerReview] = []
        self.loyalty_members: dict[str, dict] = {}  # customer_id -> data
        self.reputation_score: Decimal = Decimal("3.0")  # Score moyen des avis
        self.total_marketing_spend: Decimal = Decimal("0")

        # Paramètres par type de campagne
        self.campaign_templates = self._load_campaign_templates()

    def _load_campaign_templates(self) -> dict[CampaignType, dict]:
        """Charge les templates de campagnes avec leurs caractéristiques."""
        return {
            CampaignType.SOCIAL_MEDIA: {
                "cost_per_day": Decimal("50"),
                "reach_per_euro": 20,  # 20 personnes par euro
                "conversion_rate": Decimal("0.025"),  # 2.5%
                "target_segments": ["étudiants", "jeunes_actifs"],
                "min_duration": 7,
                "max_duration": 30,
            },
            CampaignType.LOCAL_ADS: {
                "cost_per_day": Decimal("80"),
                "reach_per_euro": 15,
                "conversion_rate": Decimal("0.035"),  # 3.5%
                "target_segments": ["familles", "seniors"],
                "min_duration": 3,
                "max_duration": 14,
            },
            CampaignType.LOYALTY_PROGRAM: {
                "cost_per_day": Decimal("30"),
                "reach_per_euro": 5,  # Moins de portée mais plus de fidélisation
                "conversion_rate": Decimal("0.15"),  # 15% (clients existants)
                "target_segments": ["tous"],
                "min_duration": 30,
                "max_duration": 365,
            },
            CampaignType.EVENTS: {
                "cost_per_day": Decimal("200"),
                "reach_per_euro": 8,
                "conversion_rate": Decimal("0.08"),  # 8%
                "target_segments": ["foodies", "familles"],
                "min_duration": 1,
                "max_duration": 3,
            },
            CampaignType.INFLUENCER: {
                "cost_per_day": Decimal("150"),
                "reach_per_euro": 25,
                "conversion_rate": Decimal("0.04"),  # 4%
                "target_segments": ["jeunes_actifs", "foodies"],
                "min_duration": 1,
                "max_duration": 7,
            },
            CampaignType.TRADITIONAL: {
                "cost_per_day": Decimal("120"),
                "reach_per_euro": 12,
                "conversion_rate": Decimal("0.02"),  # 2%
                "target_segments": ["seniors", "familles"],
                "min_duration": 7,
                "max_duration": 21,
            },
        }

    def create_campaign(
        self,
        name: str,
        campaign_type: CampaignType,
        budget: Decimal,
        duration_days: int,
        target_segments: list[str] = None,
    ) -> MarketingCampaign:
        """
        Crée une nouvelle campagne marketing.

        Args:
            name: Nom de la campagne
            campaign_type: Type de campagne
            budget: Budget alloué
            duration_days: Durée en jours
            target_segments: Segments ciblés (optionnel)

        Returns:
            Campagne créée
        """
        template = self.campaign_templates[campaign_type]

        # Validation de la durée
        if not (template["min_duration"] <= duration_days <= template["max_duration"]):
            raise ValueError(
                f"Durée invalide pour {campaign_type.value}: "
                f"{template['min_duration']}-{template['max_duration']} jours"
            )

        # Calcul de la portée attendue
        expected_reach = int(float(budget) * template["reach_per_euro"])

        # Segments par défaut si non spécifiés
        if target_segments is None:
            target_segments = template["target_segments"]

        campaign = MarketingCampaign(
            id=f"camp_{len(self.campaigns) + 1:03d}",
            name=name,
            type=campaign_type,
            budget=budget,
            duration_days=duration_days,
            target_segments=target_segments,
            expected_reach=expected_reach,
            expected_conversion=template["conversion_rate"],
        )

        self.campaigns.append(campaign)
        return campaign

    def launch_campaign(self, campaign_id: str, start_date: date) -> bool:
        """
        Lance une campagne marketing.

        Args:
            campaign_id: ID de la campagne
            start_date: Date de début

        Returns:
            True si lancée avec succès
        """
        campaign = self.get_campaign(campaign_id)
        if not campaign:
            return False

        if campaign.status != CampaignStatus.PLANNED:
            return False

        campaign.start_date = start_date
        campaign.status = CampaignStatus.ACTIVE
        return True

    def get_campaign(self, campaign_id: str) -> MarketingCampaign | None:
        """Retourne une campagne par son ID."""
        for campaign in self.campaigns:
            if campaign.id == campaign_id:
                return campaign
        return None

    def get_active_campaigns(self, current_date: date) -> list[MarketingCampaign]:
        """Retourne les campagnes actives à une date donnée."""
        return [c for c in self.campaigns if c.is_active(current_date)]

    def calculate_daily_marketing_impact(self, current_date: date) -> dict[str, any]:
        """
        Calcule l'impact marketing quotidien.

        Args:
            current_date: Date actuelle

        Returns:
            Impact marketing du jour
        """
        active_campaigns = self.get_active_campaigns(current_date)

        total_reach = Decimal("0")
        total_conversions = Decimal("0")
        total_cost = Decimal("0")
        segment_impact = {}

        for campaign in active_campaigns:
            impact = campaign.get_daily_impact(current_date)
            total_reach += impact["reach"]
            total_conversions += impact["conversion"]
            total_cost += impact["cost"]

            # Impact par segment
            for segment in campaign.target_segments:
                if segment not in segment_impact:
                    segment_impact[segment] = Decimal("0")
                segment_impact[segment] += impact["conversion"] / len(
                    campaign.target_segments
                )

        self.total_marketing_spend += total_cost

        return {
            "total_reach": int(total_reach),
            "total_conversions": int(total_conversions),
            "total_cost": total_cost,
            "segment_impact": segment_impact,
            "active_campaigns": len(active_campaigns),
        }

    def add_customer_review(
        self,
        customer_id: str,
        restaurant_id: str,
        rating: Decimal,
        comment: str,
        platform: str = "google",
    ) -> None:
        """Ajoute un avis client."""
        review = CustomerReview(
            customer_id=customer_id,
            restaurant_id=restaurant_id,
            rating=rating,
            comment=comment,
            date=date.today(),
            platform=platform,
        )

        self.reviews.append(review)
        self._update_reputation_score()

    def _update_reputation_score(self) -> None:
        """Met à jour le score de réputation basé sur les avis."""
        if not self.reviews:
            return

        # Calcul pondéré des avis (plus récents = plus de poids)
        total_weighted_score = Decimal("0")
        total_weight = Decimal("0")

        for review in self.reviews[-50:]:  # 50 derniers avis
            # Poids temporel (avis récents plus importants)
            days_old = (date.today() - review.date).days
            time_weight = max(
                Decimal("0.1"), Decimal("1.0") - Decimal(days_old) / Decimal("365")
            )

            # Poids total
            weight = review.impact_weight * time_weight

            total_weighted_score += review.rating * weight
            total_weight += weight

        if total_weight > 0:
            self.reputation_score = total_weighted_score / total_weight

    def get_reputation_summary(self) -> dict[str, any]:
        """Retourne un résumé de la réputation."""
        if not self.reviews:
            return {
                "average_rating": Decimal("3.0"),
                "total_reviews": 0,
                "rating_distribution": {},
                "recent_trend": "stable",
            }

        # Distribution des notes
        rating_distribution = dict.fromkeys(range(1, 6), 0)
        for review in self.reviews:
            rating_distribution[int(review.rating)] += 1

        # Tendance récente (30 derniers jours vs 30 précédents)
        recent_reviews = [r for r in self.reviews if (date.today() - r.date).days <= 30]
        older_reviews = [
            r for r in self.reviews if 30 < (date.today() - r.date).days <= 60
        ]

        recent_avg = (
            sum(r.rating for r in recent_reviews) / len(recent_reviews)
            if recent_reviews
            else Decimal("3.0")
        )
        older_avg = (
            sum(r.rating for r in older_reviews) / len(older_reviews)
            if older_reviews
            else Decimal("3.0")
        )

        if recent_avg > older_avg + Decimal("0.2"):
            trend = "amélioration"
        elif recent_avg < older_avg - Decimal("0.2"):
            trend = "dégradation"
        else:
            trend = "stable"

        return {
            "average_rating": self.reputation_score,
            "total_reviews": len(self.reviews),
            "rating_distribution": rating_distribution,
            "recent_trend": trend,
            "recent_reviews_count": len(recent_reviews),
        }

    def get_marketing_roi(self, period_days: int = 30) -> dict[str, any]:
        """Calcule le ROI marketing sur une période."""
        # Calcul simplifié - à améliorer avec données de ventes réelles
        total_spend = sum(
            c.budget for c in self.campaigns if c.status == CampaignStatus.COMPLETED
        )

        # Estimation des revenus générés (à connecter avec les ventes réelles)
        estimated_revenue = total_spend * Decimal("3.5")  # ROI estimé 3.5x

        return {
            "total_spend": total_spend,
            "estimated_revenue": estimated_revenue,
            "roi_ratio": estimated_revenue / total_spend
            if total_spend > 0
            else Decimal("0"),
            "campaigns_completed": len(
                [c for c in self.campaigns if c.status == CampaignStatus.COMPLETED]
            ),
        }
