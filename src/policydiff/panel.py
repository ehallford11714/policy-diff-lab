"""Synthetic panel data for DiD / event-study demos."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

import numpy as np


@dataclass
class SyntheticPanel:
    """Long panel: unit × time with treatment timing and outcome."""

    unit_id: np.ndarray
    time: np.ndarray
    treated: np.ndarray  # ever-treated unit flag (0/1)
    post: np.ndarray  # post-event indicator (0/1)
    y: np.ndarray
    event_time: int
    true_att: float
    meta: dict[str, Any] = field(default_factory=dict)

    def to_records(self) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for i in range(len(self.y)):
            rows.append(
                {
                    "unit_id": int(self.unit_id[i]),
                    "time": int(self.time[i]),
                    "treated": int(self.treated[i]),
                    "post": int(self.post[i]),
                    "y": float(self.y[i]),
                }
            )
        return rows

    def to_dict(self) -> dict[str, Any]:
        return {
            "n_obs": int(len(self.y)),
            "n_units": int(len(np.unique(self.unit_id))),
            "event_time": self.event_time,
            "true_att": self.true_att,
            "meta": self.meta,
            "records": self.to_records(),
        }


def generate_synthetic_panel(
    *,
    n_units: int = 40,
    t_pre: int = 5,
    t_post: int = 5,
    treat_share: float = 0.5,
    true_att: float = 2.0,
    unit_fe_sd: float = 1.0,
    time_trend: float = 0.15,
    noise_sd: float = 0.5,
    seed: int = 0,
) -> SyntheticPanel:
    """
    Classic staggered-ready panel with a single common event time.

    Treated units get ``true_att`` added in post periods. Parallel trends hold
    in expectation (shared time trend + unit FE + iid noise).
    """
    rng = np.random.default_rng(seed)
    n_treat = max(1, int(round(n_units * treat_share)))
    treat_ids = set(rng.choice(n_units, size=n_treat, replace=False).tolist())
    event_time = t_pre  # first post period index (0-based: times 0..t_pre-1 pre)

    unit_ids: list[int] = []
    times: list[int] = []
    treated: list[float] = []
    posts: list[float] = []
    ys: list[float] = []

    unit_fe = rng.normal(0.0, unit_fe_sd, size=n_units)
    t_max = t_pre + t_post

    for u in range(n_units):
        is_treated = 1.0 if u in treat_ids else 0.0
        for t in range(t_max):
            post = 1.0 if t >= event_time else 0.0
            y = (
                10.0
                + unit_fe[u]
                + time_trend * t
                + true_att * is_treated * post
                + float(rng.normal(0.0, noise_sd))
            )
            unit_ids.append(u)
            times.append(t)
            treated.append(is_treated)
            posts.append(post)
            ys.append(y)

    return SyntheticPanel(
        unit_id=np.asarray(unit_ids, dtype=int),
        time=np.asarray(times, dtype=int),
        treated=np.asarray(treated, dtype=float),
        post=np.asarray(posts, dtype=float),
        y=np.asarray(ys, dtype=float),
        event_time=event_time,
        true_att=float(true_att),
        meta={
            "n_units": n_units,
            "t_pre": t_pre,
            "t_post": t_post,
            "treat_share": treat_share,
            "seed": seed,
            "design": "common_event_time_2x2",
        },
    )
