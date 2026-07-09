"""Offline tests for PolicyDiff Lab."""

from __future__ import annotations

from policydiff import classic_did, generate_synthetic_panel, pre_trend_check, run_policydiff


def test_synthetic_panel_shape():
    panel = generate_synthetic_panel(n_units=20, t_pre=4, t_post=4, seed=1)
    assert len(panel.y) == 20 * 8
    assert panel.true_att == 2.0
    assert set(panel.treated.tolist()) <= {0.0, 1.0}


def test_classic_did_recovers_att():
    panel = generate_synthetic_panel(n_units=60, t_pre=5, t_post=5, true_att=2.5, seed=7)
    est = classic_did(panel)
    assert abs(est.att - 2.5) < 0.35
    assert est.backend in ("causaliv", "policydiff_minimal")
    assert est.n_obs == len(panel.y)


def test_pre_trend_pass_on_parallel_dgp():
    panel = generate_synthetic_panel(n_units=50, t_pre=6, t_post=4, true_att=2.0, seed=3)
    pre = pre_trend_check(panel, threshold=0.8)
    assert pre.n_obs > 0
    assert pre.pass_check is True


def test_run_writes_report(tmp_path):
    out = tmp_path / "out"
    result = run_policydiff(n_units=20, seed=0, out_dir=out)
    assert (out / "report.md").exists()
    assert (out / "summary.json").exists()
    assert "Classic DiD" in result.report_md
    assert result.did.att == result.did.att  # finite
