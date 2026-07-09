<p align="center">
  <img src="assets/logo.svg" alt="PolicyDiff Lab" width="96" height="96" />
</p>

# PolicyDiff Lab

**DiD / event-study workbench for policy and product launches: synthetic panels, classic 2x2 DiD, pre-trend checks, markdown reports.**

Package: `policydiff` · Product **P11** in the causal research suite.

## Install

```bash
cd PolicyDiffLab
pip install -e ".[dev]"
pip install -e ".[streamlit]"
# Optional: pip install -e ../CausalIVSuite
```

## Quick start

```bash
policydiff run -o ./out
policydiff run --n-units 60 --true-att 2.5 --seed 7 -o ./out
policydiff streamlit
```

## Docs

- [docs/SOTA.md](docs/SOTA.md) — state of the art notes for this product

## Suite

Part of the research product suite. Index: [PRODUCTS.md](../PRODUCTS.md) · GitHub: [policy-diff-lab](https://github.com/ehallford11714/policy-diff-lab)

## License

MIT