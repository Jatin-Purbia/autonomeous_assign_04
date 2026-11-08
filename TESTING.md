# Verification record

Verified locally on 8 November 2026 using Python 3.10.11 and the direct dependency versions in `requirements-tested.txt`. The prepared `.venv` uses compatible installed packages without modifying global installations. For use on another computer, create a fresh environment and install the requirements.

## Automated suite

Command: `./run.ps1 test` (equivalent to `.venv/Scripts/python.exe -m pytest -q` with unrelated pytest plugin autoload disabled).

Observed result with the required nine-plot layout: **22 passed**.

Coverage includes:

- First- and second-price payment rules, loser utility, tie allocation, negative utility from overbidding, invalid inputs.
- Truthful second-price dominance against random bid profiles, including deviations above the plotted bid range.
- All 36 fixed value/rival-profile combinations, covering all nine ordered two-rival profiles and 3,636 bid-sweep rows.
- Rival strategy transformations and independence of random bids from values and of values across rivals.
- Every Part A sweep row compared against individually resolved second-price auctions on the same rival samples, including sample mean, standard error, negative overbid utility, and truthful optimality.
- Analytical second-price expectations, first-price conditional optima, and numerical integration of ex ante first-price utility.
- Book shortest path and all three selected-edge removal counterfactuals; every edge's payment; true-cost utilities under misreporting.
- VCG dominant-strategy checks for every edge over all 21 reports, exceeding the two-edge assignment requirement.
- Seed reproducibility, all 18 second-price configurations, 248 first-price rows including equilibrium references, 42 requested VCG deviations, and Monte Carlo agreement with analytical expectations.
- A batch CLI subprocess that writes six CSVs, ten overview images, nine individual Part A images, nine individual two-rival images, a report, and validation metadata.
- Web export: `export_web_data.py` produces the JSON consumed by the React dashboard; the dashboard build (`npm run build`) and rendered pages were checked in a headless browser.

The analytical optimum tests are separate from the Monte Carlo checks. Numerical checks use `6*SE + 36/N` to cover rare events with zero observed wins; the dashboard's normal 95% intervals are reported separately and are less reliable for rare events.

## Submitted experiment run

Command: `./run.ps1 experiments`.

The generated results use **100,000 trials per configuration, seed 42**. Checks in `results/validation.json` cover fixed and random-rival truthful optimality, analytical agreement, book payments, and VCG deviations. The complete tables and interpretation are in `results/REPORT.md`.

## Application and visual checks

The React dashboard was built with Vite and its Overview, Second price and VCG tabs were checked in headless Edge screenshots.


