"""Classic 2×2 DiD + pre-trend check (causaliv backend when available)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

import numpy as np

from policydiff.panel import SyntheticPanel


@dataclass
class DiDEstimate:
    att: float
    se: float
    conf_low: float
    conf_high: float
    n_obs: int
    method: str
    backend: str
    cell_means: dict[str, float] = field(default_factory=dict)
    parallel_trends_note: str = ""
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PreTrendResult:
    """Pre-period placebo DiD (should be ~0 under parallel trends)."""

    placebo_att: float
    se: float
    n_obs: int
    pass_check: bool
    threshold: float
    notes: str
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _try_causaliv_did(
    y: np.ndarray,
    treated: np.ndarray,
    post: np.ndarray,
) -> DiDEstimate | None:
    try:
        from causaliv.did import difference_in_differences  # type: ignore
    except Exception:
        return None
    res = difference_in_differences(y=y, treated=treated, post=post)
    return DiDEstimate(
        att=float(res.att),
        se=float(res.se) if res.se == res.se else float("nan"),
        conf_low=float(res.conf_low) if res.conf_low == res.conf_low else float("nan"),
        conf_high=float(res.conf_high) if res.conf_high == res.conf_high else float("nan"),
        n_obs=int(res.n_obs),
        method=str(res.method),
        backend="causaliv",
        cell_means={
            "pre_treated": float(res.pre_treated_mean),
            "pre_control": float(res.pre_control_mean),
            "post_treated": float(res.post_treated_mean),
            "post_control": float(res.post_control_mean),
        },
        parallel_trends_note=str(res.parallel_trends_note),
        meta=dict(getattr(res, "meta", {}) or {}),
    )


def _minimal_2x2_did(
    y: np.ndarray,
    treated: np.ndarray,
    post: np.ndarray,
) -> DiDEstimate:
    """OLS DiD: y = a + b1*T + b2*P + b3*(T*P); ATT = b3."""
    y = np.asarray(y, dtype=float).reshape(-1)
    t = np.asarray(treated, dtype=float).reshape(-1)
    p = np.asarray(post, dtype=float).reshape(-1)
    n = min(len(y), len(t), len(p))
    y, t, p = y[:n], t[:n], p[:n]
    interact = t * p
    X = np.column_stack([np.ones(n), t, p, interact])
    try:
        beta, *_ = np.linalg.lstsq(X, y, rcond=None)
        att = float(beta[3])
        resid = y - X @ beta
        s2 = float(np.dot(resid, resid) / max(n - 4, 1))
        xtx_inv = np.linalg.pinv(X.T @ X)
        se = float(np.sqrt(s2 * xtx_inv[3, 3]))
    except np.linalg.LinAlgError:
        att, se = 0.0, float("nan")

    zcrit = 1.959963984540054
    lo = att - zcrit * se if np.isfinite(se) else float("nan")
    hi = att + zcrit * se if np.isfinite(se) else float("nan")

    def _mean(mask: np.ndarray) -> float:
        return float(y[mask].mean()) if mask.any() else 0.0

    return DiDEstimate(
        att=round(att, 6),
        se=round(se, 6) if np.isfinite(se) else float("nan"),
        conf_low=round(lo, 6) if np.isfinite(lo) else float("nan"),
        conf_high=round(hi, 6) if np.isfinite(hi) else float("nan"),
        n_obs=n,
        method="ols_2x2_micro",
        backend="policydiff_minimal",
        cell_means={
            "pre_treated": _mean((t == 1) & (p == 0)),
            "pre_control": _mean((t == 0) & (p == 0)),
            "post_treated": _mean((t == 1) & (p == 1)),
            "post_control": _mean((t == 0) & (p == 1)),
        },
        parallel_trends_note=(
            "DiD identifies ATT under parallel trends. "
            "Validate with pre-period placebo / event-study leads."
        ),
    )


def classic_did(
    panel: SyntheticPanel | None = None,
    *,
    y: np.ndarray | None = None,
    treated: np.ndarray | None = None,
    post: np.ndarray | None = None,
) -> DiDEstimate:
    """Run classic 2×2 DiD via causaliv if present, else minimal OLS."""
    if panel is not None:
        y, treated, post = panel.y, panel.treated, panel.post
    if y is None or treated is None or post is None:
        raise ValueError("classic_did requires panel or y/treated/post vectors")
    via = _try_causaliv_did(y, treated, post)
    if via is not None:
        return via
    return _minimal_2x2_did(y, treated, post)


def pre_trend_check(
    panel: SyntheticPanel,
    *,
    threshold: float = 0.5,
) -> PreTrendResult:
    """
    Placebo DiD on pre-periods only: split pre window into early/late.

    Under parallel trends, placebo ATT should be near zero.
    """
    pre_mask = panel.post == 0
    if int(pre_mask.sum()) < 8:
        return PreTrendResult(
            placebo_att=float("nan"),
            se=float("nan"),
            n_obs=int(pre_mask.sum()),
            pass_check=False,
            threshold=threshold,
            notes="Insufficient pre-period observations for placebo DiD.",
        )

    t_pre = panel.time[pre_mask]
    mid = float(np.median(t_pre))
    # Fake "post" = second half of pre window
    y = panel.y[pre_mask]
    treated = panel.treated[pre_mask]
    fake_post = (panel.time[pre_mask] >= mid).astype(float)

    est = classic_did(y=y, treated=treated, post=fake_post)
    ok = bool(np.isfinite(est.att) and abs(est.att) <= threshold)
    return PreTrendResult(
        placebo_att=float(est.att),
        se=float(est.se) if np.isfinite(est.se) else float("nan"),
        n_obs=int(est.n_obs),
        pass_check=ok,
        threshold=threshold,
        notes=(
            f"Pre-period placebo ATT={est.att:.4f} "
            f"({'PASS' if ok else 'FAIL'} vs |ATT|<={threshold}). "
            f"Backend={est.backend}."
        ),
        meta={"fake_post_cutoff": mid, "did_backend": est.backend},
    )
