# SOTA brief — PolicyDiff Lab (P11)

## Classic difference-in-differences

**DiD** estimates the average treatment effect on the treated (ATT) by comparing the pre→post change in treated units to the same change in controls:

\[
\widehat{\mathrm{ATT}} = (\bar Y_{1,\mathrm{post}} - \bar Y_{1,\mathrm{pre}}) - (\bar Y_{0,\mathrm{post}} - \bar Y_{0,\mathrm{pre}})
\]

Identification rests on **parallel trends**: absent treatment, treated and control outcome paths would have moved in parallel. The two-way fixed effects (TWFE) regression with a treated×post interaction recovers the same 2×2 ATT in the classic design.

## Staggered adoption

When units adopt treatment at different times, naive TWFE can mix comparisons of early vs late treated and produce **biased** or even wrong-signed weights (Goodman-Bacon decomposition; negative-weight results). Modern estimators:

| Approach | Idea |
|----------|------|
| Callaway & Sant’Anna (2021) | Group-time ATTs, then aggregate |
| Sun & Abraham (2021) | Interaction-weighted event study |
| Stacked DiD / imputation | Clean 2×2 stacks or Y(0) imputation (Borusyak et al., Gardner) |

PolicyDiff Lab MVP uses a **common event time** panel; staggered pipelines are the natural extension.

## Pre-trends & event studies

**Event-study** leads/lags plot dynamic effects relative to adoption. Pre-treatment coefficients near zero support (do not prove) parallel trends. Placebo DiD on pre-only windows is a lightweight check used in this MVP. Failures motivate covariates, matching, or alternative designs.

## Synthetic control (brief)

When few units are treated (often one), **synthetic control** (Abadie et al.) builds a weighted donor pool that matches pre-treatment outcomes. **SDID** (Arkhangelsky et al.) blends SC with DiD regularization. Prefer SC/SDID when treated count is tiny; prefer modern DiD when many units adopt.

## Product / policy launch framing

| Setting | Typical design |
|---------|----------------|
| Region policy rollout | Staggered DiD / CS |
| Feature flag A/B with phased geo | Event study + pre-trends |
| Single-market launch | Synthetic control |
| Pricing / promo calendar | Careful timing + confounders |

## References

1. Angrist & Pischke — mostly harmless econometrics (DiD intuition).
2. Callaway & Sant’Anna (2021) — multiple periods.
3. Sun & Abraham (2021) — interaction-weighted event study.
4. Goodman-Bacon (2021) — TWFE decomposition.
5. Abadie et al. — synthetic control.
6. Arkhangelsky et al. — synthetic DiD.
7. Roth et al. / Baker surveys — modern DiD practice.
