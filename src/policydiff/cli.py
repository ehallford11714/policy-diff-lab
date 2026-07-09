"""CLI: ``policydiff run``."""

from __future__ import annotations

import argparse
import json
import sys

from policydiff.pipeline import run_policydiff


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="policydiff",
        description="PolicyDiff Lab — DiD / event-study workbench",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    run = sub.add_parser("run", help="Synthetic panel → DiD + pre-trends → report")
    run.add_argument("--n-units", type=int, default=40)
    run.add_argument("--t-pre", type=int, default=5)
    run.add_argument("--t-post", type=int, default=5)
    run.add_argument("--true-att", type=float, default=2.0)
    run.add_argument("--seed", type=int, default=0)
    run.add_argument("--pretrend-threshold", type=float, default=0.5)
    run.add_argument("-o", "--out", type=str, default="./out")

    launch = sub.add_parser("streamlit", help="Print Streamlit launch command")
    launch.add_argument("--port", type=int, default=8511)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.cmd == "streamlit":
        print(f"streamlit run apps/streamlit_app.py --server.port {args.port}")
        return 0
    if args.cmd == "run":
        result = run_policydiff(
            n_units=args.n_units,
            t_pre=args.t_pre,
            t_post=args.t_post,
            true_att=args.true_att,
            seed=args.seed,
            pretrend_threshold=args.pretrend_threshold,
            out_dir=args.out,
        )
        summary = {
            "att": result.did.att,
            "se": result.did.se,
            "backend": result.did.backend,
            "true_att": result.panel.true_att,
            "pretrend_pass": result.pre_trends.pass_check,
            "placebo_att": result.pre_trends.placebo_att,
            "out_dir": result.out_dir,
        }
        print(json.dumps(summary, indent=2))
        print(f"\nWrote report: {result.out_dir}/report.md")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
