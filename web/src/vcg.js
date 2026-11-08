// Port of auction_lab.core.vcg: cheapest A->F path with VCG payments to edges.
export const BOOK_COSTS = { AB: 3, AC: 2, BD: 2, BE: 1, CE: 3, CF: 5, DF: 2, EF: 1 };
export const POS = { A: [60, 160], B: [250, 60], C: [250, 260], D: [470, 60], E: [470, 260], F: [660, 160] };

function paths(costs, excluded) {
  const out = [];
  const walk = (node, path, cost) => {
    if (node === "F") return out.push({ path: path.join(""), cost });
    for (const [e, w] of Object.entries(costs))
      if (e !== excluded && e[0] === node && !path.includes(e[1])) walk(e[1], [...path, e[1]], cost + w);
  };
  walk("A", ["A"], 0);
  return out.sort((a, b) => a.cost - b.cost || (a.path < b.path ? -1 : 1));
}

export function vcg(reports = BOOK_COSTS, trueCosts = BOOK_COSTS) {
  const best = paths(reports)[0];
  const sel = new Set();
  for (let i = 0; i < best.path.length - 1; i++) sel.add(best.path[i] + best.path[i + 1]);
  const payments = {}, utilities = {};
  for (const e of Object.keys(reports)) {
    let p = 0;
    if (sel.has(e)) p = paths(reports, e)[0].cost - (best.cost - reports[e]);
    payments[e] = p;
    utilities[e] = sel.has(e) ? p - trueCosts[e] : 0;
  }
  return { path: best.path, cost: best.cost, selected: sel, payments, utilities };
}
