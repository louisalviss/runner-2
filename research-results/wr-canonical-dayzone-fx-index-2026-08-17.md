# Wave Rider Canonical T-day × Zone Validation — FX + Index — 2026-08-17

## Purpose
Re-test non-crypto Wave Rider v2.5.13 with the **full canonical event-day + time-zone regime rules** that were absent from the earlier long cross-asset tests.

## Frozen rules
Wave Rider v2.5.13 core/lifecycle unchanged.

Event anchors:
- CPI release
- Non Farm Payrolls
- FOMC / Fed Interest Rate Decision

Canonical T-day policy:
- ON: T-2, T-1, T0, T+2, T+3
- OFF: T+1 and outside the event window
- When windows overlap, a fresh T0 overrides; otherwise a T+1 state is OFF.

Canonical VN-time zones:
- Zone A: 02:00–08:00, only after a major event has already occurred earlier in the same 08:00-anchored trading day.
- Zone B: 16:00–19:00.
- Zone C: 23:00–02:00.
- Other times OFF.
- Trading-day anchor: 08:00 Asia/Ho_Chi_Minh.
- Major-news guard: ±15 minutes.

Test scope:
- 5m only. 3m/10m were not opened after 5m failed confirmation, to limit multiple-testing.
- Forex: EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, USDCHF, NZDUSD.
- Index: SPXUSD, NSXUSD.
- HistData M1 bid OHLC aggregated strictly to 5m.
- Gross R; no spread, commission, or slippage deduction.

Calendar:
- Machine-readable historical TradingView Economic Calendar.
- Older US CPI releases normalized from `Inflation Rate YoY` to the same CPI release anchor; duplicate same-timestamp CPI labels deduped.
- January 2024 NFP/CPI/FOMC anchor dates were spot-checked against official BLS/Federal Reserve schedules.
- Annual event-count hard audit used before backtest.

---

## Index 5m — 2018–2025 discovery

All-time baseline before canonical filter:
- N=2,046
- Total +59.47R
- Avg +0.0291R/trade
- PF 1.045
- CI95 [-0.0381, +0.0924]

Full canonical T-day × Zone:
- N=313
- Total **-7.96R**
- Avg **-0.0254R/trade**
- PF **0.961**
- CI95 [-0.1823, +0.1191]
- Positive years: **3/8**
- Positive symbols: **1/2**
- Retention: 15.3%

Symbols:
- SPXUSD: N149, +11.00R, +0.0738R/trade, PF 1.118.
- NSXUSD: N164, -18.96R, -0.1156R/trade, PF 0.832.

Era split:
- 2018–2021: N155, -14.58R, -0.0941R/trade.
- 2022–2025: N158, +6.62R, +0.0419R/trade.

Zones:
- A: N53, +0.2706R/trade.
- B: N104, -0.1677R/trade.
- C: N156, -0.0312R/trade.

T-day diagnostics:
- T-2: N65, +0.1596R/trade.
- T-1: N70, -0.0357R/trade.
- T0: N132, +0.0658R/trade.
- T+1 (diagnostic OFF sample): N49, +0.2210R/trade.
- T+2: N26, **-0.7082R/trade**, CI95 fully negative.
- T+3: N20, -0.3056R/trade.

### Index decision
**Full crypto-derived canonical T-day × Zone policy does not transfer to Index 5m.**

Do not open 2014–2017 Index holdout and do not tune Index T-day/Zone rules from these same samples. SPX alone remains a regime-dependent research observation, not a validated production branch.

---

## Forex 5m — 2018–2025 discovery

All-time baseline before canonical filter:
- N=8,375
- Total -253.82R
- Avg **-0.0303R/trade**
- PF 0.954
- CI95 [-0.0614, +0.0007]

Full canonical T-day × Zone:
- N=1,230
- Total **+65.15R**
- Avg **+0.0530R/trade**
- PF **1.084**
- CI95 [-0.0214, +0.1364]
- Positive years: **6/8**
- Positive symbols: **5/7**
- Retention: 14.7%

Era split:
- 2018–2021: N588, +14.65R, **+0.0249R/trade**, PF 1.039.
- 2022–2025: N642, +50.51R, **+0.0787R/trade**, PF 1.125.

This was a material improvement over the unfiltered/full-day baseline and also improved the previously weak pre-2022 period, therefore a pristine older holdout was justified.

Forex symbols, 2018–2025 canonical:
- EURUSD: +0.0766R/trade.
- GBPUSD: +0.1187R/trade.
- USDJPY: +0.0422R/trade.
- AUDUSD: -0.0421R/trade.
- USDCAD: -0.0913R/trade.
- USDCHF: +0.0412R/trade.
- NZDUSD: +0.2047R/trade; discovery CI barely above zero.

Zones, 2018–2025:
- A: N184, +0.1314R/trade.
- B: N477, +0.0020R/trade.
- C: N569, +0.0703R/trade.

T-day diagnostics, 2018–2025:
- T-2: N247, +0.1504R/trade.
- T-1: N278, -0.0421R/trade.
- T0: N488, +0.0331R/trade.
- T+1 (diagnostic OFF sample): N194, +0.0182R/trade.
- T+2: N124, +0.1310R/trade.
- T+3: N93, +0.0787R/trade.

---

## Forex pristine holdout — 2014–2017

The **entire full canonical rule** was frozen before opening 2014–2017. No pair was removed and no T-day/Zone component was changed.

Full canonical holdout:
- N=519
- Total **-7.00R**
- Avg **-0.0135R/trade**
- PF **0.980**
- CI95 [-0.1263, +0.1045]
- Positive years: **2/4**
- Positive symbols: **3/7**

Years:
- 2014: -0.0144R/trade.
- 2015: +0.0439R/trade.
- 2016: +0.0112R/trade.
- 2017: -0.1237R/trade.

Symbols:
- EURUSD: -0.0297R/trade.
- GBPUSD: -0.2619R/trade.
- USDJPY: +0.2083R/trade.
- AUDUSD: +0.1893R/trade.
- USDCAD: -0.0993R/trade.
- USDCHF: +0.0660R/trade.
- NZDUSD: -0.1683R/trade.

Zones:
- A: N73, +0.0421R/trade.
- B: N198, -0.0026R/trade.
- C: N248, -0.0386R/trade.

T-day diagnostics:
- T-2: N105, -0.1935R/trade.
- T-1: N104, +0.0415R/trade.
- T0: N202, -0.0998R/trade.
- T+1 (diagnostic OFF sample): N67, +0.1442R/trade.
- T+2: N43, +0.2586R/trade.
- T+3: N65, +0.2775R/trade.

Calendar audit for every holdout year: CPI 12, NFP 12, FOMC 8.

### Forex decision
**Full canonical T-day × Zone materially improves Forex selection, but does not survive pristine 2014–2017 holdout as a durable standalone production rule.**

Therefore:
- Do not promote full canonical Forex 5m to production yet.
- Do not run cost stress as a promotion test; gross holdout already failed.
- Do not open 3m/10m merely to search for a winner.
- Do not remove GBPUSD/NZDUSD/USDCAD or cherry-pick positive pairs post-hoc.
- Do not rewrite the canonical T-day policy from these diagnostics without a new hypothesis and new untouched data.

For context, simple arithmetic across 2014–2025 full-canonical samples:
- N=1,749
- Total ≈ +58.15R
- Avg ≈ +0.0332R/trade gross

That pooled gross number is **not** sufficient evidence because the pristine holdout itself was negative and real transaction costs are still absent.

---

## What changed versus the earlier non-crypto conclusion

Earlier long tests did not include the full canonical T-day + Zone layer.

After adding it:
- **Index:** conclusion remains negative/unvalidated; the canonical crypto regime map does not transfer.
- **Forex:** conclusion becomes more nuanced. The canonical layer has real screening value and turns the 2018–2025 gross sample from negative baseline to positive, but the exact full rule fails older pristine confirmation.

This supports the broader architecture:

`macro/event regime -> market-specific Stage3 -> Wave Rider v2.5.13 execution`

The current evidence does **not** support using one universal crypto-derived T-day/Zone map unchanged across Crypto, Forex, and Index.

## Current production status
- Crypto: separate evidence track; unchanged by this test.
- Forex 5m full canonical T×Zone: **RESEARCH / UNPROVEN**.
- Index 5m full canonical T×Zone: **REJECT AS UNIVERSAL RULE / UNPROVEN**.
- Wave Rider v2.5.13 core: remains frozen reference/execution engine.
