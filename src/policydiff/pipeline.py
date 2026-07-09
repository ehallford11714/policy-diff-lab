"""End-to-end PolicyDiff pipeline + markdown report."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from policydiff.did import DiDEstimate, PreTrendResult, classic_did, pre_trend_check
from policydiff.panel import SyntheticPanel, generate_synthetic_panel


@dataclass
class PolicyDiffResult:
    panel: SyntheticPanel
    did: DiDEstimate
    pre_trends: PreTrendResult
    report_md: str
    out_dir: str | None = None
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "panel": {
                "n_obs": int(len(self.panel.y)),
                "event_time": self.panel.event_time,
                "true_att": self.panel.true_att,
                "meta": self.panel.meta,
            },
            "did": self.did.to_dict(),
            "pre_trends": self.pre_trends.to_dict(),
            "out_dir": self.out_dir,
            "meta": self.meta,
            "report_md": self.report_md,
        }


def render_report(result: PolicyDiffResult) -> str:
    d = result.did
    p = result.pre_trends
    panel = result.panel
    lines = [
        "# PolicyDiff Lab report",
        "",
        "## Design",
        f"- Units / obs: **{panel.meta.get('n_units')}** / **{len(panel.y)}**",
        f"- Event time (first post): **{panel.event_time}**",
        f"- True ATT (DGP): **{panel.true_att}**",
        f"- DiD backend: **{d.backend}** (`{d.method}`)",
        "",
        "## Classic DiD",
        f"- ATT = **{d.att}** (se={d.se})",
        f"- 95% CI: [{d.conf_low}, {d.conf_high}]",
        f"- Cell means: `{d.cell_means}`",
        "",
        f"> {d.parallel_trends_note}",
        "",
        "## Pre-trend check",
        f"- Placebo ATT = **{p.placebo_att}** (se={p.se})",
        f"- Pass: **{p.pass_check}** (threshold |ATT| ≤ {p.threshold})",
        f"- Notes: {p.notes}",
        "",
        "## Interpretation",
    ]
    if p.pass_check and abs(d.att - panel.true_att) < 1.0:
        lines.append(
            "- Pre-trends look compatible with parallel trends; "
            "estimated ATT is close to the synthetic true effect."
        )
    elif not p.pass_check:
        lines.append(
            "- Pre-trend placebo failed — do not treat ATT as causal without "
            "further design work (event-study leads, covariates, or SC)."
        )
    else:
        lines.append(
            "- Review CI width and design assumptions before policy claims."
        )
    lines += [
        "",
        "## Next steps",
        "- Event-study leads/lags for staggered adoption",
        "- Callaway–Sant’Anna / Sun–Abraham aggregations",
        "- Synthetic control / SDID when few treated units",
        "",
    ]
    return "\n".join(lines)


def run_policydiff(
    *,
    n_units: int = 40,
    t_pre: int = 5,
    t_post: int = 5,
    true_att: float = 2.0,
    seed: int = 0,
    pretrend_threshold: float = 0.5,
    out_dir: str | Path | None = None,
) -> PolicyDiffResult:
    panel = generate_synthetic_panel(
        n_units=n_units,
        t_pre=t_pre,
        t_post=t_post,
        true_att=true_att,
        seed=seed,
    )
    did = classic_did(panel)
    pre = pre_trend_check(panel, threshold=pretrend_threshold)
    result = PolicyDiffResult(
        panel=panel,
        did=did,
        pre_trends=pre,
        report_md="",
        meta={"seed": seed},
    )
    result.report_md = render_report(result)

    if out_dir is not None:
        path = Path(out_dir)
        path.mkdir(parents=True, exist_ok=True)
        (path / "report.md").write_text(result.report_md, encoding="utf-8")
        import json

        payload = result.to_dict()
        # Drop bulky records from JSON summary
        (path / "summary.json").write_text(
            json.dumps({k: v for k, v in payload.items() if k != "report_md"}, indent=2),
            encoding="utf-8",
        )
        (path / "panel.json").write_text(
            json.dumps(panel.to_dict(), indent=2),
            encoding="utf-8",
        )
        result.out_dir = str(path.resolve())

    return result
