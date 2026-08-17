# Wave Rider Cross-Asset Validation Checkpoint — 2026-08-17

## Frozen strategy
- Wave Rider v2.5.13 core/lifecycle was kept unchanged throughout this research path.
- No TP / EMA / CHOP / S/R parameter was tuned from these results.
- Python replication was repeatedly checked against the frozen engine; the instrumented execution runner matched trade-for-trade on the tested samples.

## Main conclusion
**Do not promote any new non-crypto production branch from this research.**

The promising short-window and 2022–2025 findings were regime-dependent and did not survive sufficiently long historical confirmation plus realistic cost stress.

---

## SPXUSD 5m all-day

Promising period:
- 2024 broad index 5m screen: pooled SPXUSD + NSXUSD strongly positive.
- 2025 holdout split the family: SPXUSD remained positive, NSXUSD turned negative.

Frozen older-year confirmation for SPXUSD 5m all-day:
- 2022: N=121, Total=-5.500R, Avg=-0.0455R, PF=0.933.
- 2023: N=112, Total=-7.250R, Avg=-0.0647R, PF=0.900.
- 2022–2023 combined: N=233, Total=-12.750R, Avg=-0.0547R, PF=0.917.

Decision:
- Reject the hypothesis that SPXUSD 5m all-day is a stable universal edge.
- Treat 2024–2025 as a favorable regime, not proof of a durable production rule.
- Do not mine SPX sessions/parameters from the same data in this path.

---

## FX 5m London–New York overlap

### 2022–2025 initially looked strong
Seven majors: EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, USDCHF, NZDUSD.

- 2022: N=128, +11.851R, +0.0926R/trade.
- 2023: N=93, +5.557R, +0.0598R/trade.
- 2024: N=113, +20.644R, +0.1827R/trade.
- 2025: N=119, +25.700R, +0.2160R/trade.
- 2022–2025 combined: N=453, +63.752R, +0.1407R/trade, PF=1.225.
- Block-bootstrap 95% CI for AvgR: approximately [+0.0001, +0.2934]; gross evidence was only barely above zero at the lower bound.
- Positive years: 4/4; positive quarters: 11/16.

Breadth:
- Six of seven pairs had positive total R across 2022–2025; AUDUSD was negative.
- Leave-one-pair-out checks showed the family was not dependent on one single pair.

### Execution sensitivity
Planned stop distance across those 453 trades:
- P10: 2.3 pips
- P25: 3.5 pips
- Median: 5.1 pips
- P75: 7.4 pips
- P90: 9.4 pips
- Mean: 5.82 pips

All-in adverse execution-distance stress:
- 0.25 pip: +37.694R, +0.0832R/trade.
- 0.50 pip: +11.636R, +0.0257R/trade.
- 0.75 pip: -14.422R, -0.0318R/trade.
- Approximate break-even: ~0.61 pip all-in.

This made broker execution a critical constraint even before testing older regimes.

### 2018–2021 pristine prior-era extension — failed
Same frozen hypothesis, same 7 pairs, same 5m London–NY overlap:
- 2018: N=112, -16.599R, -0.1482R/trade.
- 2019: N=107, +2.992R, +0.0280R/trade.
- 2020: N=160, -18.717R, -0.1170R/trade.
- 2021: N=107, -6.503R, -0.0608R/trade.
- 2018–2021 combined: N=486, -38.828R, -0.0799R/trade, PF=0.885.
- Only 1/4 years positive.
- At 0.25 pip all-in cost: -68.994R, -0.1420R/trade.

Simple combined arithmetic for 2018–2025:
- N=939
- Gross Total ≈ +24.924R
- Gross Avg ≈ +0.0265R/trade
- At 0.25 pip all-in cost: ≈ -31.300R total, ≈ -0.0333R/trade
- At 0.50 pip all-in cost: ≈ -87.524R total, ≈ -0.0932R/trade

Decision:
- Reject FX 5m London–NY overlap as a standalone durable edge.
- The 2022–2025 improvement is a regime phenomenon that needs an external/casual Stage3 explanation before any production use.

---

## Stage3 causal diagnostic

Exploratory features were frozen before running and used only completed prior daily data:
- 20-day daily trend efficiency.
- 20-day daily volatility regime.
- Signal direction aligned vs opposite the sign of the prior 20-day daily net move.

No Wave Rider parameter changed.

Important exploratory finding:
- Trend-aligned signals were poor across 2018–2025.
- Countertrend-to-20d-daily-direction signals looked better in discovery:
  - 2018–2025 classified sample: N=418, +69.167R, +0.1655R/trade, gross CI positive.
  - However the effect was heavily concentrated in 2022–2025.
  - 2018–2021 countertrend: only +0.0167R/trade gross and negative after 0.25 pip cost.

### Pristine 2014–2017 countertrend confirmation — failed
The single discovered countertrend rule was frozen and tested without scanning alternatives:
- Combined 2014–2017: N=217, -7.033R, -0.0324R/trade, PF=0.953.
- At 0.25 pip all-in: -18.986R, -0.0875R/trade.
- Positive years: 2/4.

Therefore the simple 20-day countertrend Stage3 rule did **not** replicate and is rejected.

Do not rescue it by pair-picking: pair-level outcomes in the 2014–2017 holdout were highly heterogeneous, which makes post-hoc pair selection especially vulnerable to overfitting.

---

## Broker-cost reality check

The historical strategy is extremely sensitive to transaction cost because stops are usually only a few pips wide.

A broker/account must demonstrate sustained all-in execution materially below the backtested break-even, not merely advertise a near-zero quoted spread.

Because the 2018–2025 combined sample is already negative at a 0.25-pip stress assumption, broker optimization alone cannot rescue the universal FX-overlap hypothesis.

---

## Research decision / guardrails

1. Keep Wave Rider v2.5.13 frozen as the execution engine/reference.
2. Do **not** promote SPXUSD 5m all-day.
3. Do **not** promote raw FX 5m London–NY overlap.
4. Do **not** promote the exploratory 20-day countertrend filter.
5. Do **not** continue threshold/session/pair mining on these same samples.
6. The remaining research problem is Stage3 alpha/regime suitability: it must be economically motivated, causal/past-only, and validated on genuinely untouched data.
7. Any future FX/CFD production candidate must include broker-specific spread + commission + slippage before promotion.
8. Embedded historical news filtering still needs reconstruction for exact parity with the canonical strategy; current tests validate the structural core/lifecycle, not the full historical news calendar.
9. HistData bid M1 and CFD/index proxy feeds can differ from actual execution feeds.

## Current status
**Non-crypto cross-asset expansion: NOT VALIDATED for production.**

The evidence supports the broader interpretation that Wave Rider is primarily an execution/timing engine whose expectancy is strongly conditional on upstream regime/flow, rather than a standalone universal alpha generator.
