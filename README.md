# Mechanism Lab — Autonomous Systems, Assignment 04

A reproducible Python course project covering second-price auctions, first-price equilibrium deviations, and VCG cheapest-path procurement. Includes an interactive Streamlit dashboard, batch experiments, analytical benchmarks, plots, CSVs, and automated tests.

## Run on Windows / PowerShell

The current workspace has a tested local `.venv` assembled from compatible installed packages, because the default Anaconda NumPy/pandas combination is broken and package downloads are disabled. No global packages were changed. Use these commands **on this computer**:

```powershell
.\run.ps1 experiments
.\run.ps1 test
.\run.ps1 app
```

If PowerShell blocks local scripts, use `.\.venv\Scripts\python.exe -m streamlit run app.py` directly (and the same interpreter for tests and batch runs). This local environment references installed packages on this computer and is not portable. On another computer, create a clean environment and install the declared requirements:

From this project folder:

```powershell
python -m pip install -r requirements.txt
python run_experiments.py --trials 100000 --seed 42
python -m pytest -q
python -m streamlit run app.py
```

Open the local URL printed by Streamlit, normally http://localhost:8501. Stop the server with Ctrl+C. A virtual environment is optional: create it with `python -m venv .venv`, then use `.\.venv\Scripts\python.exe` instead of `python` in the commands above. No API key, internet access, or book parsing dependency is needed to run the project after installing requirements.

## Deliverables

- [Generated report](results/REPORT.md): experiment assumptions, equations, results, figures, interpretation, and validation flags.
- `results/*.csv`: all experiment rows at full precision, including standard errors and analytical expectations.
- `results/part1a/*.png`: the nine required Part A plots, one per value/strategy combination.
- `results/part1c/*.png`: nine corresponding plots for the two-rival extension.
- `results/*.png`: ten overview figures, including both nine-panel grids and the directed book graph.
- `results/validation.json`: seed, trial count, and checks for the generated run.
- `app.py`: dashboard with simulation controls, downloads, and an interactive VCG misreport experiment.
- `auction_lab/core.py`: auction resolution, exact expectations, Dijkstra, and VCG counterfactual payments.
- `auction_lab/experiments.py`: Monte Carlo and deterministic experiment definitions.
- `tests/`: rules, dominant-strategy checks, numerical benchmarks, CLI artifact generation, and Streamlit application interactions.
- [Testing record](TESTING.md): test results, runtime versions, coverage, and verification limits. Exact tested direct dependencies are in `requirements-tested.txt`.

The book source is `book/multiagent-systems_compress.pdf`, Figure 7.3, printed page 300 (PDF page 349). Edge directions and costs were checked visually. Procurement payments are computed rather than hard-coded.

## Coverage and interpretation

**Part 1A:** bidder 1 values 0.2, 0.5, 0.8; each paired with truthful, half-value, or independent random rival bidding: nine separate plots. For every combination, sweep own bids 0,0.01,...,1 with 100,000 auctions per bid. The two-rival extension repeats these nine plots with independent rivals adopting the same strategy. All 1,818 rows are in `results/second_price_bids.csv`. The truthful-only summary is retained separately. Candidate bids share the same rival draws, and negative utilities from overbidding are retained.

**Fixed rival checks:** bids 0.1, 0.4, 0.9 include all nine ordered two-rival profiles, with own bids swept in steps of 0.01. Truthful bidding is weakly optimal: other bids can tie its utility. A proof in the report covers bids outside the sweep.

**Part 2:** n=2,3,4; bidder 1 bids k*v for every k=0.1,...,2.0; rivals bid ((n-1)/n)*v. Includes both fixed bidder 1 values and a separate uniform-value experiment because the prompt does not specify which to use. Exact equilibrium fractions appear as additional reference rows when absent from the grid. Measures payment-reduction feasibility for the winner of every auction, plus the winning margin and a fixed 0.01 reduction. Continuous bids make the first fraction 1 almost surely; the report explains why this is compatible with equilibrium.

**Part 3:** directed graph from the book; ABEF with cost 5; AB receives 4, BE 2, EF 3, other edges zero. AB and AC each misreport 0,...,10 in 0.5 steps. Utilities always use true costs. Tests additionally check deviations for every edge.

The prompt's repeated “parts A and C” is treated as repeating both second-price experiments with two rivals. Ties favor the lowest bidder index; equal-cost routes use lexical order. Losing bidders and unselected edges receive zero. Random samples are independent across bidders; first-price scenarios share draws across k to reduce comparison noise. Monte Carlo intervals describe sampling error only.

## Demo sequence

1. Open Second price: compare truthful versus half bidding; explain why truthful and random rival bids share a distribution.
2. Inspect fixed-bid curves: show the truthful bid on a maximizing plateau.
3. Open First price: compare each n, then switch bidder 1's value. Explain the exact equilibrium reference and why bidding above value can lose money.
4. Open VCG: show ABEF and payments. Select AC and report 0; the route changes to ACEF but AC loses utility 1. Restore its true cost 2.
5. Show the report, CSVs, and test run as reproducibility evidence.

## Reproduce a smaller run

```powershell
python run_experiments.py --trials 20000 --seed 7 --output results_demo
```

The dashboard defaults to 100,000 trials per configuration and permits 200,000; submitted batch results use 100,000 and seed 42. Smaller CLI runs are for quick demonstrations or automated smoke tests and do not meet the submitted experiment's trial-count requirement. Normal 95% intervals may miss analytical values by chance and can be unreliable for very rare wins. The separate automated simulation checks use tolerance `6*SE + 36/N` for bounded utilities and deterministic seeds; the correction handles zero observed wins. The test suite includes Streamlit AppTest interaction tests; it does not substitute for rendering checks in every browser. Dashboard tables use HTML to avoid depending on optional Arrow binary builds.
