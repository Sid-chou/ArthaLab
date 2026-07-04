# ArthaLab Architecture

## 1. Purpose

ArthaLab is an offline-first portfolio research framework for Indian investors. Its job is to compare asset allocations by their probability of achieving a financial goal while controlling downside risk, drawdown, and sequence risk.

The first use case is a wedding corpus by December 2030. The portfolio is not the family's only source of wedding funding, so the system should optimize for risk-adjusted growth and capital preservation, not maximum return.

This document describes the solo-developer MVP architecture. It keeps the domain and quantitative design stable, but avoids enterprise abstractions that are not required before Phase 2.

## 2. Product Principles

ArthaLab must follow these rules:

- Do not predict future market returns.
- Do not recommend specific mutual funds.
- Do not provide financial advice.
- Do not guarantee investment outcomes.
- Use local historical data during analysis.
- Do not make live API calls during analysis.
- Prefer reproducible, deterministic, configuration-driven workflows.
- Optimize for goal achievement probability and downside control, not CAGR alone.

## 3. MVP Scope

Phase 1 should build the smallest useful research engine:

- Load local historical data.
- Define current portfolio and candidate allocations.
- Expand SIP and lump sum cashflows.
- Run cashflow-aware historical backtests.
- Run rolling-window analysis.
- Calculate risk and goal metrics.
- Compare portfolio scenarios.
- Produce growth, drawdown, rolling-return, and allocation-drift charts.
- Produce Markdown, CSV, and JSON outputs.

Phase 2 adds:

- Bootstrap simulation.
- Monte Carlo simulation.
- Efficient frontier optimization.
- Rebalancing comparisons.
- Broader risk metrics and sensitivity analysis.

Phase 3 adds dashboards, APIs, richer reports, tax handling, and a broader scenario builder.

The MVP should not build generic interface layers, dependency injection frameworks, web adapters, or database repositories. It should keep pure calculation code separate from I/O so those layers can be added later.

## 4. High-Level Design

Use a simple modular package:

```text
ArthaLab/
  docs/
  configs/
  data/
    raw/
    processed/
    reference/
  reports/
    markdown/
    csv/
    json/
    figures/
  src/
    arthalab/
      domain/
      data/
      analytics/
      engines/
      optimization/
      reporting/
      config/
      workflows/
  tests/
    unit/
    integration/
    fixtures/
```

Package responsibilities:

| Package | MVP responsibility |
| --- | --- |
| `domain` | Core financial objects and validation rules |
| `data` | Local file loading, cleaning, return-matrix construction |
| `analytics` | Risk, return, drawdown, correlation, and goal metrics |
| `engines` | Backtest, rolling-window, simulation, scenario, and sensitivity engines |
| `optimization` | Scenario ranking and later efficient frontier/search logic |
| `reporting` | Markdown, CSV, JSON, and chart artifact assembly |
| `config` | Load and validate analysis configuration |
| `workflows` | End-to-end orchestration for the solo MVP |

The dependency rule is intentionally simple:

```text
config/data -> domain
analytics -> domain
engines -> domain + analytics
optimization -> domain + analytics + engines
reporting -> domain + analytics result objects
workflows -> config + data + engines + optimization + reporting
```

Domain and analytics code should be pure and easy to test. I/O stays in `data`, `config`, `reporting`, and `workflows`.

## 5. Data Flow

The MVP workflow is:

```text
Analysis Config
  -> Validate Goal, Portfolio, Cashflows, Assumptions
  -> Load Local Asset Metadata
  -> Load Local Historical Prices / NAVs / Index Levels
  -> Validate Data Quality
  -> Build Return Matrix
  -> Materialize Candidate Portfolios
  -> Expand Cashflow Schedule
  -> Run Historical Backtest
  -> Run Rolling Windows
  -> Calculate Risk Metrics
  -> Calculate Goal Outcomes
  -> Rank Scenario Portfolios
  -> Generate Charts and Tables
  -> Write Markdown / CSV / JSON Reports
```

External data ingestion is separate from analysis:

```text
Manual Data Download
  -> data/raw/
  -> Normalize and Validate
  -> data/processed/
  -> Dataset Manifest
  -> Analysis Run
```

Analysis runs must only read local files.

## 6. Domain Model

### 6.1 Asset Class

An asset class is an investable category, not a specific fund.

Current asset classes:

- Equity
- Gold
- Silver
- Debt
- Liquid Funds
- Cash

Future asset classes:

- REITs
- International Equity
- ETFs
- Bonds
- Bitcoin

Fields:

| Field | Description |
| --- | --- |
| `asset_class_id` | Stable identifier |
| `name` | Human-readable name |
| `currency` | Base currency, initially INR |
| `risk_category` | Equity-like, debt-like, commodity-like, cash-like, alternative |
| `liquidity_profile` | High, medium, low |
| `data_source` | Local source lineage |
| `benchmark_id` | Optional benchmark mapping |
| `is_supported` | Whether usable in current workflows |

### 6.2 Asset

An asset is a concrete historical return series or proxy used for analysis.

Fields:

| Field | Description |
| --- | --- |
| `asset_id` | Stable identifier |
| `asset_class_id` | Parent asset class |
| `name` | Asset or proxy name |
| `source` | NSE, Nifty Indices, AMFI, RBI, MCX, World Gold Council, or local source |
| `frequency` | Daily, weekly, monthly |
| `return_type` | Price return, total return, NAV return |
| `start_date` | First valid observation |
| `end_date` | Last valid observation |
| `currency` | Currency of observations |
| `metadata` | Data quality and lineage attributes |

### 6.3 Holding

A holding represents a current portfolio position.

Fields:

| Field | Description |
| --- | --- |
| `holding_id` | Stable holding identifier |
| `asset_id` | Linked asset or proxy |
| `asset_class_id` | Linked asset class |
| `instrument_name` | Fund or instrument display name |
| `current_value` | Current market value |
| `allocation_weight` | Weight in current portfolio |
| `xirr` | Optional historical investor return |
| `as_of_date` | Valuation date |

Current portfolio from research notes:

| Holding | Allocation |
| --- | ---: |
| Aditya Birla Liquid Fund | 34.7% |
| HDFC Sensex Index | 27.9% |
| Kotak Multicap | 14.5% |
| Quantum Gold | 17.8% |
| HDFC Silver | 5.2% |

### 6.4 Portfolio

A portfolio is either current holdings or a target asset-class allocation.

Fields:

| Field | Description |
| --- | --- |
| `portfolio_id` | Stable identifier |
| `name` | Display name |
| `description` | Strategy notes |
| `base_currency` | Initially INR |
| `holdings` | Optional concrete holdings |
| `target_allocation` | Asset-class weight map |
| `rebalance_policy_id` | Optional rebalancing policy |
| `created_from` | Current holdings, scenario, optimizer output, or manual config |

Validation:

- Weights must sum to 100%.
- Unsupported assets must fail validation.
- Phase 1 is long-only.
- Leverage and shorting are out of scope.

### 6.5 Portfolio Scenario

A scenario is a named candidate allocation.

Required scenarios:

| Scenario | Allocation |
| --- | --- |
| Version A | 50% Equity, 30% Gold, 20% Silver |
| Version B | Current strategy with liquid fund retained |
| Portfolio C Balanced | 55% Equity, 25% Debt, 15% Gold, 5% Silver |
| Portfolio D Growth | 65% Equity, 20% Debt, 10% Gold, 5% Silver |
| Portfolio E Conservative | 40% Equity, 40% Debt, 15% Gold, 5% Silver |
| Portfolio F Gold Heavy | 50% Equity, 20% Debt, 25% Gold, 5% Silver |
| Portfolio G Aggressive | 80% Equity, 10% Debt, 5% Gold, 5% Silver |
| Portfolio H Professional Consensus | 50% Equity, 30% Debt, 15% Gold, 5% Silver |

### 6.6 Goal

A goal defines the investment target.

Fields:

| Field | Description |
| --- | --- |
| `goal_id` | Stable identifier |
| `goal_type` | Wedding, retirement, education, house, emergency fund, financial independence |
| `name` | Display name |
| `start_date` | Investment start date |
| `target_date` | Goal date |
| `target_values` | One or more corpus targets |
| `inflation_rate` | Default 6% unless overridden |
| `priority` | Optional ranking for later multi-goal planning |
| `funding_context` | Notes about external or partial funding |

Default first goal:

| Field | Value |
| --- | --- |
| Goal | Wedding corpus |
| Target date | December 2030 |
| Target values | INR 7L, INR 8L, INR 9L, INR 10L, custom |
| Inflation rate | 6% |

Reports must state that parents will also contribute, so the portfolio objective is risk-adjusted support rather than sole funding.

### 6.7 Cashflow Schedule

Cashflows represent contributions and withdrawals.

Fields:

| Field | Description |
| --- | --- |
| `cashflow_id` | Stable identifier |
| `portfolio_id` | Optional portfolio link |
| `date` | Cashflow date or schedule anchor |
| `amount` | Positive for contribution, negative for withdrawal |
| `frequency` | One-time, monthly, quarterly, annual |
| `allocation_rule` | Target allocation, current allocation, custom allocation, or cash |
| `source` | SIP, lump sum, withdrawal, manual |

Default assumptions:

| Cashflow | Value |
| --- | ---: |
| Monthly SIP | INR 5,000 |
| Lump sum after Year 1 | INR 80,000 |
| Lump sum after Year 2 | INR 80,000 |

### 6.8 Rebalancing Policy

Fields:

| Field | Description |
| --- | --- |
| `rebalance_policy_id` | Stable identifier |
| `frequency` | None, monthly, quarterly, semiannual, annual |
| `threshold` | Optional drift threshold |
| `cashflow_rebalance` | Whether contributions restore target weights |
| `goal_glidepath` | Optional future rule to reduce risk near goal date |

Default:

- Annual rebalancing.

The architecture must support comparing annual rebalancing against no rebalancing.

### 6.9 Assumption Set

Assumptions are part of the reproducibility contract.

Fields:

| Field | Description |
| --- | --- |
| `assumption_set_id` | Stable identifier |
| `inflation_rate` | Default 6% |
| `risk_free_rate` | Default 6% |
| `benchmark_id` | Default Nifty TRI |
| `tax_policy` | Ignored in Phase 1 |
| `return_frequency` | Daily or monthly |
| `random_seed` | Required for stochastic workflows |
| `simulation_count` | Number of simulation paths |
| `methodology_version` | Version of calculations |

### 6.10 Analysis Result Bundle

The result bundle is the canonical output from an analysis workflow.

Fields:

| Field | Description |
| --- | --- |
| `run_id` | Analysis run identifier |
| `created_at` | Timestamp |
| `config_hash` | Hash of input configuration |
| `data_manifest_id` | Data snapshot identifier |
| `methodology_version` | Version of metric and simulation definitions |
| `portfolio_results` | Per-portfolio result objects |
| `comparison_table` | Cross-portfolio metrics |
| `goal_results` | Per-target probability and outcome statistics |
| `chart_specs` | Chart-ready data structures |
| `report_sections` | Report-ready narrative blocks |
| `warnings` | Data quality, assumptions, and limitations |

## 7. Data Schemas

### 7.1 Market Price Dataset

Purpose: local historical prices, NAVs, or index levels.

Required columns:

| Column | Description |
| --- | --- |
| `date` | Observation date |
| `asset_id` | Asset identifier |
| `value` | Price, NAV, or index level |
| `currency` | Observation currency |
| `source` | Local source lineage |
| `return_type` | Price, total return, NAV |
| `quality_flag` | Valid, missing, interpolated, stale, adjusted |

Validation:

- Dates must be unique per asset.
- Values must be positive.
- Calendar gaps must be reported.
- Missing observations must be handled by a declared alignment policy.
- Source lineage must be preserved.

### 7.2 Return Matrix

Purpose: analysis-ready asset return panel.

Fields:

| Field | Description |
| --- | --- |
| `dates` | Ordered analysis dates |
| `asset_ids` | Ordered asset identifiers |
| `returns` | Return values by date and asset |
| `frequency` | Daily, weekly, monthly |
| `alignment_policy` | Inner join, outer join with fill, business calendar |
| `start_date` | First analysis date |
| `end_date` | Last analysis date |

Return matrices are derived artifacts and must be reproducible from local data.

### 7.3 Benchmark Dataset

Fields:

| Field | Description |
| --- | --- |
| `benchmark_id` | Stable benchmark identifier |
| `name` | Display name |
| `date` | Observation date |
| `value` | Index level or return |
| `return_type` | Price return or total return |
| `source` | Local source lineage |

Default benchmark:

- Nifty TRI.

### 7.4 Risk-Free Rate Dataset

Fields:

| Field | Description |
| --- | --- |
| `date` | Effective date |
| `rate` | Annualized rate |
| `source` | RBI or configured assumption |
| `frequency` | Static, daily, monthly |

Default:

- 6%.

### 7.5 Analysis Configuration

Purpose: versioned input to a full analysis run.

Fields:

| Field | Description |
| --- | --- |
| `config_id` | Stable identifier |
| `version` | Config schema version |
| `goal` | Goal definition |
| `portfolios` | Candidate scenarios |
| `cashflows` | Cashflow schedule |
| `rebalancing` | Rebalancing policy |
| `assumptions` | Assumption set |
| `analysis_modules` | Requested modules |
| `report_outputs` | Requested output formats |

For the MVP, configuration should be a human-editable YAML or JSON file loaded by a workflow.

### 7.6 Simulation Path Dataset

Purpose: output from bootstrap or Monte Carlo engines.

Fields:

| Field | Description |
| --- | --- |
| `run_id` | Analysis run identifier |
| `portfolio_id` | Portfolio identifier |
| `simulation_method` | Monte Carlo or bootstrap |
| `path_id` | Simulation path identifier |
| `date` | Simulated date |
| `portfolio_value` | Simulated value |
| `contribution` | Cashflow applied on date |
| `drawdown` | Path drawdown at date |
| `allocation` | Optional asset allocation snapshot |

### 7.7 Metric Dataset

Purpose: normalized metrics for comparison and reporting.

Fields:

| Field | Description |
| --- | --- |
| `run_id` | Analysis run identifier |
| `portfolio_id` | Portfolio identifier |
| `metric_name` | Canonical metric identifier |
| `metric_value` | Numeric value |
| `unit` | Percent, INR, ratio, probability |
| `period_start` | Optional start date |
| `period_end` | Optional end date |
| `methodology_version` | Calculation definition version |

### 7.8 Goal Outcome Dataset

Purpose: target-specific success and failure metrics.

Fields:

| Field | Description |
| --- | --- |
| `run_id` | Analysis run identifier |
| `portfolio_id` | Portfolio identifier |
| `target_value` | Goal corpus target |
| `success_probability` | Probability of reaching target |
| `failure_probability` | Probability of missing target |
| `median_outcome` | Median terminal value |
| `best_outcome` | High-percentile or maximum terminal value, per methodology |
| `worst_outcome` | Low-percentile or minimum terminal value, per methodology |
| `shortfall_at_risk` | Optional goal shortfall risk metric |

## 8. Asset Abstractions

ArthaLab separates products, proxies, and asset classes.

### 8.1 Product-Level Assets

Examples:

- Aditya Birla Liquid Fund
- HDFC Sensex Index
- Kotak Multicap
- Quantum Gold
- HDFC Silver

Used for current portfolio representation, reports, XIRR context, and holding-level audit trail.

### 8.2 Proxy-Level Assets

Examples:

- Equity index proxy.
- Gold proxy.
- Silver proxy.
- Debt index proxy.
- Liquid fund proxy.
- Cash proxy.

Used for backtesting, rolling analysis, simulation, efficient frontier, and scenario comparison.

### 8.3 Asset Classes

Asset classes are the optimizer's main decision level. This keeps the system aligned with the project constraint: ArthaLab researches allocation, not fund selection.

Mapping:

```text
Holding -> Product-Level Asset -> Proxy-Level Asset -> Asset Class
```

This mapping preserves current portfolio reality while allowing analysis to use stable proxies.

## 9. Analytics

Analytics functions calculate metrics from portfolio paths, return series, and simulation outputs. They should be deterministic and side-effect free.

Required risk metrics: CAGR, XIRR, volatility, maximum drawdown, Sharpe, Sortino, Calmar, VaR, CVaR, downside deviation, sequence risk, and inflation-adjusted return.

Required goal metrics: probability of reaching each target corpus, failure probability, median outcome, best outcome, worst outcome, and optional shortfall-at-risk.

Required relationship metrics: correlation matrix, rolling returns, rolling Sharpe, and allocation drift.

Phase 1 should implement the metrics needed for historical backtest, rolling windows, and scenario comparison first. VaR, CVaR, and advanced sequence-risk diagnostics may deepen in Phase 2.

## 10. Simulation Engine Architecture

The simulation architecture is preserved even though Phase 1 starts with historical backtesting and rolling windows.

### 10.1 Shared Simulation Concepts

All engines must support initial portfolio value, target allocation, cashflows, rebalancing policy, goal date, target values, inflation, risk-free rate, and reproducibility metadata.

Stochastic engines must also support deterministic random seed, simulation count, and methodology version.

Common output: portfolio value paths, terminal values, drawdown paths, goal success indicators, distribution summaries, and warnings.

### 10.2 Shared Portfolio Accounting

Backtesting, rolling windows, bootstrap, and Monte Carlo should reuse the same accounting rules:

- Apply returns at the configured frequency.
- Apply SIPs and lump sums on scheduled dates.
- Allocate new cash according to the configured allocation rule.
- Track asset-level values.
- Track total portfolio value.
- Track allocation drift.
- Apply rebalancing policy.
- Calculate drawdowns from the resulting value path.

This shared accounting logic is the most important internal engine boundary. A weighted-return shortcut is not sufficient because SIPs, lump sums, and sequence risk are core requirements.

### 10.3 Historical Backtest Engine

Purpose:

- Replay historical returns with configured cashflows and rebalancing.

Responsibilities: align portfolio asset returns; apply SIPs, lump sums, and withdrawals; apply annual or no-rebalance policies; track allocation drift; produce value paths, drawdown paths, and terminal goal outcomes.

Phase 1 priority:

- This is the main MVP engine.

### 10.4 Rolling Window Engine

Purpose:

- Test how portfolio behavior changes across historical start dates and market regimes.

Responsibilities: generate rolling windows, run shared accounting inside each window, calculate rolling metrics, and summarize robustness across regimes.

Design decision:

- Rolling windows must reuse the backtest accounting engine to avoid inconsistent treatment of cashflows and rebalancing.

### 10.5 Bootstrap Engine

Purpose:

- Estimate outcome distributions by resampling historical returns without assuming a parametric distribution.

Supported methods:

- Simple return bootstrap.
- Block bootstrap.
- Regime-aware bootstrap later.

Responsibilities: sample rows or blocks from the multi-asset return matrix, preserve cross-asset relationships, apply shared accounting, and generate path and terminal distributions.

Design decision:

- Do not sample each asset independently. Sampling full return-matrix rows or blocks preserves correlation structure better.

Phase:

- Phase 2.

### 10.6 Monte Carlo Engine

Purpose:

- Estimate future outcome distributions under explicit statistical assumptions.

Responsibilities: generate correlated asset return paths, apply shared accounting, produce path and terminal distributions, and use explicit seeds.

Supported assumption modes: historical mean/covariance, conservative adjusted assumptions, user-configured expected returns, and future regime models.

Design decision:

- Monte Carlo outputs must clearly separate historical evidence from forward-looking assumptions. ArthaLab does not predict returns.

Phase:

- Phase 2.

### 10.7 Scenario Engine

Purpose:

- Evaluate deterministic stress and research scenarios.

Examples:

- Equity crash.
- Gold outperformance.
- Silver underperformance.
- Debt rate shock.
- Inflation shock.
- Delayed goal date.
- Reduced SIP.
- No lump sums.

Responsibilities: apply configured shocks, re-run outcome calculations, and compare stressed outcomes against baseline.

Phase:

- Basic scenarios can start in Phase 1. Broader macro scenario tooling belongs in Phase 2 or 3.

### 10.8 Sensitivity Engine

Purpose:

- Test whether conclusions survive assumption changes.

Sensitivity dimensions:

- Equity allocation.
- Gold allocation.
- Silver allocation.
- Debt allocation.
- SIP amount.
- Lump sum timing.
- Inflation rate.
- Goal target.
- Rebalancing frequency.
- Expected return assumptions.

Output: sensitivity matrix, robustness warnings, and ranking changes.

Phase:

- Phase 2.

## 11. Optimization Architecture

### 11.1 Philosophy

Optimization must serve the goal, not the highest CAGR.

Primary objectives: maximize goal success probability; minimize failure probability, drawdown, downside deviation, and sequence risk; improve risk-adjusted returns; preserve capital where appropriate.

Secondary objectives: increase median terminal outcome, improve inflation-adjusted return, maintain diversification, and avoid excessive concentration.

### 11.2 MVP Optimization

For Phase 1, "optimization" means scenario ranking, not a full mathematical optimizer.

Workflow:

```text
Configured Portfolio Scenarios
  -> Historical Backtest
  -> Rolling Window Evaluation
  -> Risk and Goal Metrics
  -> Multi-Criteria Ranking
  -> Evidence-Based Recommendation
```

Default ranking priority:

1. Goal success probability.
2. Failure probability.
3. Maximum drawdown.
4. Downside deviation or worst rolling outcome.
5. Median terminal value.
6. Sharpe, Sortino, or Calmar.
7. CAGR.

This keeps the MVP explainable and aligned with the project principle.

### 11.3 Phase 2 Optimization

Phase 2 may add grid search, random feasible allocation sampling, efficient frontier construction, and cvxpy or PyPortfolioOpt integrations.

Constraint examples:

| Constraint | Example |
| --- | --- |
| Full investment | Weights sum to 100% |
| Long-only | All weights >= 0% |
| Equity bounds | 40% to 80% |
| Debt bounds | 10% to 40% |
| Gold bounds | 5% to 30% |
| Silver bounds | 0% to 20% |
| Cash bounds | 0% to 20% |
| Concentration limit | No single asset class above configured maximum |

Efficient frontier should be a research view, not the final decision-maker. Mean-variance outputs are sensitive to expected-return assumptions and must be validated against goal probability and downside metrics.

### 11.4 Recommendation Output

Reports may rank allocations, but must phrase conclusions as research evidence, not financial advice. Each recommendation needs goal-probability evidence, downside-risk evidence, tradeoff notes, assumption sensitivity, data period, methodology limitations, and a disclaimer.

## 12. Reporting Architecture

### 12.1 MVP Outputs

Phase 1 outputs: Markdown report, CSV tables, JSON result bundle, and static chart figures.

PDF can wait until Phase 3 unless needed for sharing.

### 12.2 Report Sections

The Markdown report should include summary, assumptions, current portfolio, candidate portfolios, data sources, methodology, backtest results, rolling-window results, risk metrics, goal probability table, scenario ranking, recommendation evidence, limitations, disclaimer, and reproducibility appendix.

### 12.3 CSV Exports

CSV exports should cover portfolio comparison, risk metrics, goal outcomes, rolling-window metrics, and scenario rankings.

### 12.4 JSON Export

JSON should preserve the result bundle for regression testing, future APIs, future dashboards, and reproducibility audits.

### 12.5 Charts

Phase 1 charts: portfolio growth, allocation drift, rolling returns, rolling Sharpe, drawdown, and correlation matrix.

Phase 2 charts: Monte Carlo fan chart, efficient frontier, and sensitivity heatmap.

Charts should be generated from structured result data. The calculation engine should not render charts directly.

## 13. Configuration

Use versioned config files to make analysis runs reproducible.

Configuration should include goal, current portfolio, candidate scenarios, cashflows, rebalancing policy, asset-to-proxy mappings, data paths, assumptions, analysis modules, and output settings.

Default assumptions:

| Setting | Default |
| --- | --- |
| Inflation | 6% |
| Risk-free rate | 6% |
| Benchmark | Nifty TRI |
| Rebalancing | Annual |
| Taxes | Ignored in Phase 1 |
| SIP | INR 5,000 monthly |
| Lump sums | INR 80,000 after Year 1 and Year 2 |

Every run should record config version/hash, dataset manifest, data date range, asset universe, methodology version, random seed when applicable, warnings, and artifact paths.

## 14. Validation And Errors

Validation categories: configuration, portfolio weights, asset support, data completeness, date ranges, cashflow schedules, rebalancing policy, simulation parameters, and report outputs.

Severity levels:

| Severity | Meaning |
| --- | --- |
| Fatal | Analysis cannot run |
| Warning | Analysis can run, but report must show caveat |
| Info | Useful reproducibility or methodology note |

Examples:

- Fatal: target allocation sums to 95%.
- Fatal: no historical data for a required asset.
- Warning: silver history starts later than equity history.
- Warning: benchmark range is shorter than portfolio range.
- Info: taxes are ignored in Phase 1.

## 15. Testing Strategy

For a solo MVP, test the parts that can silently corrupt conclusions.

Unit tests: portfolio weight validation, cashflow expansion, rebalancing rules, return calculations, drawdowns, CAGR/volatility, goal outcomes, and scenario ranking.

Integration tests: end-to-end fixture analysis, backtest with SIP and lump sums, rolling-window analysis, and Markdown/CSV/JSON output generation.

Regression tests: golden result bundle, golden Markdown skeleton, and deterministic stochastic-engine outputs once Phase 2 exists.

Data quality tests: missing dates, duplicate observations, non-positive prices, extreme return outliers, and missing asset mappings.

## 16. Technical Decisions And Tradeoffs

| Decision | Rationale | Tradeoff |
| --- | --- | --- |
| Offline-first analysis | Reproducible, deterministic, testable, no hidden live API dependency | Data refresh is separate |
| Asset-class research | Studies allocation and avoids fund recommendations | Product-to-proxy basis risk must be documented |
| Simple workflow layer | A solo MVP does not need service/adaptor/interface layers yet | Workflows may be promoted later for APIs or dashboards |
| Structured result bundle | Enables Markdown, CSV, JSON, tests, and later UI reuse | Requires schema discipline |
| Shared portfolio accounting | Keeps SIPs, lump sums, withdrawals, rebalancing, and sequence risk consistent | Needs strong tests |
| Scenario ranking first | Existing research questions already define useful candidate portfolios | May miss allocations outside configured scenarios until Phase 2 |
| Mean-variance later | Frontier analysis is sensitive to expected-return assumptions | Results will be more nuanced than "highest Sharpe wins" |

## 17. Open Questions

Open questions: best Indian proxy series for each asset class; silver cap; debt glidepath near the goal; lump sum allocation policy; annual versus no rebalancing; percentile versus absolute best/worst outcomes; nominal versus inflation-adjusted success probability; minimum historical window.

## 18. Final Principle

ArthaLab should produce defensible research, not opinions. Every allocation comparison, ranking, and recommendation must trace back to data, assumptions, methodology, and reproducible calculations.
