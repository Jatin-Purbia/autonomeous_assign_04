"""Reproducible experiment tables; no plotting or UI dependencies."""
from itertools import product
import numpy as np
import pandas as pd
from .core import (VALUES, STRATEGIES, BOOK_COSTS, rival_bids,
                   second_price_expected, first_price_expected, vcg)


def estimate(samples):
    return float(np.mean(samples)), float(np.std(samples, ddof=1) / np.sqrt(len(samples)))


def monte_carlo_close(frame, trials):
    """Conservative bounded-sample check, including unobserved rare wins.

    All utilities in these scenarios have range at most 1. The 36/N term
    prevents an empirical SE of zero from falsely rejecting rare events.
    This is a validation tolerance, separate from displayed 95% intervals.
    """
    return (frame.mean_utility-frame.exact_utility).abs() <= 6*frame.standard_error + 36/trials


def second_price_experiments(trials=100_000, seed=42):
    rng = np.random.default_rng(seed)
    rows = []
    for rivals, strategy in product((1, 2), STRATEGIES):
        _, bids = rival_bids(rng, trials, rivals, strategy)
        maximum = bids.max(axis=1)
        for v in VALUES:
            utility = np.maximum(v - maximum, 0)
            mean, se = estimate(utility)
            rows.append(dict(rivals=rivals, value=v, strategy=strategy,
                             mean_utility=mean, standard_error=se,
                             ci95_low=mean-1.96*se, ci95_high=mean+1.96*se,
                             exact_utility=second_price_expected(v, rivals, strategy),
                             win_fraction=float(np.mean(v >= maximum))))
    return pd.DataFrame(rows)


def fixed_bid_experiments():
    """All 3 fixed bids for one rival and all 9 ordered two-rival profiles."""
    rows = []
    for rivals in (1, 2):
        for profile in product((.1, .4, .9), repeat=rivals):
            maximum = max(profile)
            for v in VALUES:
                truthful = max(v - maximum, 0.)
                for b in np.linspace(0, 1, 101):
                    utility = v - maximum if b >= maximum else 0.
                    rows.append(dict(rivals=rivals, rival_bids="/".join(map(str, profile)),
                                     max_rival_bid=maximum, value=v, bid=float(b),
                                     utility=utility, truthful_utility=truthful,
                                     truthful_is_optimal=utility <= truthful + 1e-12))
    return pd.DataFrame(rows)


def second_price_bid_sweeps(trials=100_000, seed=42):
    """Part A: every own bid 0,.01,...,1 against each random-rival model.

    Sorted rival maxima and prefix sums compute sample moments without a
    trials-by-bids matrix. Every candidate bid uses the same rival draws.
    """
    rng = np.random.default_rng(seed)
    rows = []
    grid = np.linspace(0, 1, 101)
    for rivals, strategy in product((1, 2), STRATEGIES):
        _, bids = rival_bids(rng, trials, rivals, strategy)
        maximum = np.sort(bids.max(axis=1))
        sums = np.r_[0., np.cumsum(maximum)]
        squares = np.r_[0., np.cumsum(maximum**2)]
        counts = np.searchsorted(maximum, grid, side='right')
        for v in VALUES:
            means = (v*counts - sums[counts])/trials
            second_moments = (v*v*counts-2*v*sums[counts]+squares[counts])/trials
            errors = np.sqrt(np.maximum(second_moments-means**2,0)/(trials-1))
            truthful = float(means[round(v*100)])
            for b, mean, se, count in zip(grid, means, errors, counts):
                rows.append(dict(rivals=rivals, value=v, strategy=strategy,
                    bid=float(b), mean_utility=float(mean), standard_error=float(se),
                    ci95_low=float(mean-1.96*se), ci95_high=float(mean+1.96*se),
                    exact_utility=second_price_expected(v,rivals,strategy,float(b)),
                    win_fraction=float(count/trials), truthful_mean_utility=truthful,
                    truthful_is_optimal=bool(mean<=truthful+1e-12)))
    return pd.DataFrame(rows)


def first_price_experiments(trials=100_000, seed=42):
    if trials < 2:
        raise ValueError("Need at least two trials.")
    rng = np.random.default_rng(seed)
    rows = []
    for n in (2, 3, 4):
        a = (n-1)/n
        other_bids = a * rng.uniform(0, 1, (trials, n-1))
        random_values = rng.uniform(0, 1, trials)
        # Shared draws across k reduce noise in comparisons.
        for label in (*VALUES, "uniform"):
            values = random_values if label == "uniform" else np.full(trials, label)
            # Include the exact equilibrium even when it is absent from the required grid.
            grid = sorted(set([round(i / 10, 1) for i in range(1, 21)] + [a]))
            for k in grid:
                own_bids = k * values
                all_bids = np.column_stack((own_bids, other_bids))
                wins = own_bids >= other_bids.max(axis=1)
                utility = np.where(wins, values-own_bids, 0.)
                mean, se = estimate(utility)
                ordered = np.sort(all_bids, axis=1)
                gap = ordered[:, -1] - ordered[:, -2]
                rows.append(dict(n=n, value=str(label), k=k,
                                 is_equilibrium=abs(k-a)<1e-12,
                                 on_required_grid=abs(k*10-round(k*10))<1e-10,
                                 mean_utility=mean, standard_error=se,
                                 ci95_low=mean-1.96*se, ci95_high=mean+1.96*se,
                                 exact_utility=first_price_expected(n,k,None if label=="uniform" else label),
                                 win_fraction=float(wins.mean()),
                                 winner_could_pay_less_fraction=float(np.mean(gap>0)),
                                 winner_could_save_001_fraction=float(np.mean(gap>.01)),
                                 mean_winning_margin=float(gap.mean())))
    return pd.DataFrame(rows)


def vcg_experiments():
    baseline = vcg()
    payments = pd.DataFrame([dict(edge=e, true_cost=c, selected=e in
        [baseline['path'][i:i+2] for i in range(len(baseline['path'])-1)],
        payment=baseline['payments'][e], utility=baseline['utilities'][e])
        for e,c in BOOK_COSTS.items()])
    deviations = []
    for edge in ("AB", "AC"):
        for report in np.arange(0, 10.01, .5):
            reports = dict(BOOK_COSTS, **{edge: float(report)})
            result = vcg(reports)
            utility = result['utilities'][edge]
            deviations.append(dict(edge=edge, true_cost=BOOK_COSTS[edge], report=report,
                path=result['path'], payment=result['payments'][edge], utility=utility,
                truthful_utility=baseline['utilities'][edge],
                utility_change=utility-baseline['utilities'][edge]))
    return payments, pd.DataFrame(deviations)


def run_all(trials=100_000, seed=42):
    payments, deviations = vcg_experiments()
    return dict(second_price=second_price_experiments(trials,seed),
                second_price_bids=second_price_bid_sweeps(trials,seed),
                fixed_bids=fixed_bid_experiments(),
                first_price=first_price_experiments(trials,seed),
                vcg_payments=payments, vcg_deviations=deviations)
