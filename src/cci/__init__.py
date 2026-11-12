"""
Causal Credit Intelligence (CCI)
ArqTech Labs

Platform for causal machine learning applied to credit risk analytics.
"""

__version__ = "0.1.0"
__author__ = "ArqTech Labs"
__status__ = "foundation"

from cci.core.config import get_config
from cci.core.logging import get_logger

__all__ = ["__version__", "get_config", "get_logger"]
