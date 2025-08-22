"""
FoodOps Pro - Jeu de gestion de restaurant réaliste et pédagogique.

Ce package implémente un business game complet pour former aux aspects
clés de la gestion d'un restaurant : menu engineering, achats, stocks,
RH France, comptabilité PCG, et analyse de marché.
"""

__version__ = "1.0.0"
__author__ = "FoodOps Team"
__email__ = "contact@foodops.pro"

from .domain import *
from .core import *
from .io import *
from .network import *
