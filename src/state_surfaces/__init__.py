"""
Public package interface for the state_surfaces library.
"""

from .core import StateSurfaceResult, analyze
from .pipeline import process_gauss_code, run_pipeline
from .version import __version__

__all__ = [
    "StateSurfaceResult",
    "analyze",
    "process_gauss_code",
    "run_pipeline",
    "__version__",
]
