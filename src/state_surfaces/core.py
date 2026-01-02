"""
core.py

High-level public API for the state_surfaces package.

This module is intentionally lightweight: it wraps the smoothing pipeline and
returns a structured result (with a convenient dict conversion) for downstream
use in the CLI, scripts, or notebooks.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional, Sequence

from .pipeline import run_pipeline


@dataclass(frozen=True)
class StateSurfaceResult:
    """
    Result of running the state-surface pipeline on a Gauss code (or DT code).

    Fields mirror the keys produced by `pipeline.run_pipeline`.
    """

    gauss_code: Sequence[Sequence[int]]
    state_code: Sequence[Sequence[int]]
    unoriented_genus: int
    crosscap: int
    simple: bool
    two_sided: bool

    def to_dict(self) -> Dict[str, Any]:
        """Convert the result to a plain dictionary (JSON-friendly)."""
        return asdict(self)


def analyze(*, gauss_code: Any = None, dt_code: Optional[str] = None,) -> StateSurfaceResult:
    """
    Run the full state-surface pipeline and return a structured result.

    Exactly one of `gauss_code` or `dt_code` should be provided.

    Parameters
    ----------
    gauss_code:
        A Gauss code in any format accepted by `gauss_io.clean_gauss_notation`,
        including:
          - list[int] (single component),
          - list[list[int]] (multi-component),
          - or supported string notations.
    dt_code:
        Optional DT code string (if provided, it will be converted to a Gauss code).

    Returns
    -------
    StateSurfaceResult
        Structured result including the Gauss code, state code, and invariants.
    """
    result = run_pipeline(gauss_code=gauss_code, dt_code=dt_code)

    return StateSurfaceResult(
        gauss_code=result["gauss_code"],
        state_code=result["state_code"],
        unoriented_genus=result["unoriented_genus"],
        crosscap=result["crosscap"],
        simple=result["simple"],
        two_sided=result["two_sided"],
    )


__all__ = [
    "StateSurfaceResult",
    "analyze",
]
