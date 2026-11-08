"""Pure auction rules, analytical benchmarks, and directed-path VCG."""
from dataclasses import dataclass
import heapq
import math

import numpy as np

VALUES = (0.2, 0.5, 0.8)
STRATEGIES = ("truthful", "half", "random")
BOOK_COSTS = {"AB": 3., "AC": 2., "BD": 2., "BE": 1.,
              "CE": 3., "CF": 5., "DF": 2., "EF": 1.}


def _nonnegative(values):
    if any(not math.isfinite(float(x)) or float(x) < 0 for x in values):
        raise ValueError("Values and bids must be finite and nonnegative.")


@dataclass(frozen=True)
class Outcome:
    winner: int
    payment: float
    utilities: tuple


def auction(values, bids, pricing="second"):
    """Single item; zero-based lowest index wins ties; losers pay zero."""
    if len(values) != len(bids) or len(bids) < 2:
        raise ValueError("Provide matching values/bids for at least two bidders.")
    _nonnegative([*values, *bids])
    if pricing not in ("first", "second"):
        raise ValueError("pricing must be first or second")
    winner = max(range(len(bids)), key=lambda i: bids[i])
    payment = float(bids[winner] if pricing == "first" else
                    max(b for i, b in enumerate(bids) if i != winner))
    utilities = tuple(float(values[i] - payment) if i == winner else 0.
                      for i in range(len(bids)))
    return Outcome(winner, payment, utilities)


def rival_bids(rng, trials, rivals, strategy):
    if trials < 2 or rivals < 1 or strategy not in STRATEGIES:
        raise ValueError("Need >=2 trials, >=1 rival, and a supported strategy.")
    values = rng.uniform(0, 1, (trials, rivals))
    if strategy == "truthful":
        bids = values.copy()
    elif strategy == "half":
        bids = values / 2
    else:
        bids = rng.uniform(0, 1, (trials, rivals))
    return values, bids


def second_price_expected(v, rivals, strategy, bid=None):
    """E[(v-M)1{M<=bid}], M=max of m independent U[0,s] bids."""
    if not 0 <= v <= 1 or rivals < 1 or strategy not in STRATEGIES:
        raise ValueError("Invalid second-price parameters.")
    scale = .5 if strategy == "half" else 1.
    bid = v if bid is None else bid
    _nonnegative([bid])
    x = min(bid / scale, 1.)
    return v * x ** rivals - scale * rivals / (rivals + 1) * x ** (rivals + 1)


def first_price_expected(n, k, v=None):
    """Conditional on v, or integrated over v~U[0,1] when v=None."""
    if n < 2 or k < 0 or not math.isfinite(k):
        raise ValueError("Need n>=2 and finite k>=0.")
    a = (n - 1) / n
    if v is not None:
        if not 0 <= v <= 1:
            raise ValueError("Value must be in [0,1].")
        return (1 - k) * v * min(k * v / a, 1.) ** (n - 1)
    if k <= a:
        return (1 - k) * (k / a) ** (n - 1) / (n + 1)
    t = a / k
    return (1 - k) * ((k / a) ** (n - 1) * t ** (n + 1) / (n + 1)
                      + (1 - t * t) / 2)


def shortest_path(costs, excluded=None):
    """Dijkstra on the book's directed edges; lexical tie breaking."""
    _nonnegative(costs.values())
    queue = [(0., ("A",), "A")]
    best = {}
    while queue:
        cost, path, node = heapq.heappop(queue)
        if node in best:
            continue
        best[node] = cost
        if node == "F":
            return cost, path
        for edge, weight in sorted(costs.items()):
            if edge != excluded and edge[0] == node:
                heapq.heappush(queue, (cost + weight, path + (edge[1],), edge[1]))
    return math.inf, ()


def vcg(reports=None, true_costs=None):
    """Procurement payments TO edges. Utilities use true, not reported, costs."""
    reports = dict(BOOK_COSTS if reports is None else reports)
    true_costs = dict(BOOK_COSTS if true_costs is None else true_costs)
    if set(reports) != set(BOOK_COSTS) or set(true_costs) != set(reports):
        raise ValueError("Provide costs for exactly the eight book edges.")
    _nonnegative(true_costs.values())
    total, path = shortest_path(reports)
    selected = set(a + b for a, b in zip(path, path[1:]))
    payments, utilities = {}, {}
    for edge in reports:
        payment = 0.
        if edge in selected:
            without, _ = shortest_path(reports, excluded=edge)
            if not math.isfinite(without):
                raise ValueError("A selected edge has no finite alternative path.")
            payment = without - (total - reports[edge])
        payments[edge] = payment
        utilities[edge] = payment - true_costs[edge] if edge in selected else 0.
    return {"path": "".join(path), "reported_cost": total,
            "payments": payments, "utilities": utilities}
