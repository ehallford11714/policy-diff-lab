"""policydiff — DiD / event-study workbench for policy & product launches."""

from __future__ import annotations

from policydiff.did import DiDEstimate, classic_did, pre_trend_check
from policydiff.panel import SyntheticPanel, generate_synthetic_panel
from policydiff.pipeline import PolicyDiffResult, run_policydiff

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "DiDEstimate",
    "PolicyDiffResult",
    "SyntheticPanel",
    "classic_did",
    "generate_synthetic_panel",
    "pre_trend_check",
    "run_policydiff",
]
