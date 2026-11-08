import React, { useEffect, useMemo, useState } from "react";
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ReferenceLine, AreaChart, Area,
} from "recharts";
import { BOOK_COSTS, POS, vcg } from "./vcg.js";

const C = { blue: "#6ea8ff", teal: "#2dd4bf", amber: "#fbbf24", pink: "#f472b6", violet: "#a78bfa", green: "#4ade80", red: "#f87171", grid: "#243049", text: "#94a3b8" };
const STRAT = { truthful: "Truthful", half: "Half value", random: "Random bid" };
const SCOLOR = { truthful: C.teal, half: C.amber, random: C.pink };
const TABS = ["Overview", "Second price", "First price", "VCG network", "Method"];
const f = (x, d = 3) => (x == null ? "–" : Number(x).toFixed(d));

function Seg({ value, onChange, options, label }) {
  return (
    <div className="seg-wrap">
      {label && <span className="seg-label">{label}</span>}
      <div className="seg">
        {options.map(([v, t]) => (
          <button key={String(v)} className={v === value ? "on" : ""} onClick={() => onChange(v)}>{t}</button>
        ))}
      </div>
    </div>
  );
}

const Card = ({ title, sub, children }) => (
  <section className="card">
    {title && <h3>{title}</h3>}
    {sub && <p className="sub">{sub}</p>}
    {children}
  </section>
);

const Stat = ({ label, value, hint, color = C.blue }) => (
  <div className="stat" style={{ "--c": color }}>
    <span>{label}</span><b>{value}</b>{hint && <small>{hint}</small>}
  </div>
);

const tip = { contentStyle: { background: "#0b1220", border: "1px solid #2b3a58", borderRadius: 10, color: "#e2e8f0" }, labelStyle: { color: "#94a3b8" } };
const axis = { stroke: C.text, tick: { fill: C.text, fontSize: 12 } };

function BidChart({ rows, v, height = 320, mini = false, color = C.blue }) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={rows} margin={{ top: 24, right: 14, left: mini ? -22 : 0, bottom: 4 }}>
        <CartesianGrid stroke={C.grid} strokeDasharray="3 3" />
        <XAxis dataKey="bid" type="number" domain={[0, 1]} {...axis} tickCount={6} />
        <YAxis {...axis} tickFormatter={(x) => x.toFixed(2)} />
        {!mini && <Tooltip {...tip} formatter={(x) => f(x, 4)} labelFormatter={(l) => "bid = " + l} />}
        <ReferenceLine x={v} stroke={C.green} strokeDasharray="5 4" label={mini ? undefined : { value: "b = v", fill: C.green, fontSize: 12, position: "top" }} />
        <Line dataKey="exact_utility" name="Exact expectation" stroke={C.text} dot={false} strokeDasharray="4 4" strokeWidth={1.5} isAnimationActive={false} />
        <Line dataKey="mean_utility" name="Simulated mean" stroke={color} dot={false} strokeWidth={2.4} isAnimationActive={false} />
        {!mini && <Legend wrapperStyle={{ color: C.text }} />}
      </LineChart>
    </ResponsiveContainer>
  );
}

function Overview({ data, go }) {
  const vc = vcg();
  return (
    <>
      <div className="stats">
        <Stat label="Auctions per bid" value={(data.meta.trials || 100000).toLocaleString()} hint={`seed ${data.meta.seed}`} color={C.blue} />
        <Stat label="Second-price scenarios" value="18" hint="3 values × 3 strategies × 1–2 rivals" color={C.teal} />
        <Stat label="First-price bidders" value="2 · 3 · 4" hint="k = 0.1 … 2.0" color={C.amber} />
        <Stat label="VCG route" value={vc.path} hint={`cost ${vc.cost}`} color={C.pink} />
      </div>
      <div className="grid3">
        {[
          ["Second price", "Truthful bidding is a dominant strategy: the price you pay never depends on your own bid.", "Second price", C.teal],
          ["First price", "Shading to (n−1)/n of value balances margin against win probability. Bid above value and you lose money.", "First price", C.amber],
          ["VCG network", "Edges are agents. Each is paid its marginal contribution, so lying about cost never helps.", "VCG network", C.pink],
        ].map(([t, d, tab, c]) => (
          <button key={t} className="feature" style={{ "--c": c }} onClick={() => go(tab)}>
            <h3>{t}</h3><p>{d}</p><span>Explore →</span>
          </button>
        ))}
      </div>
      <Card title="Headline findings">
        <ul className="findings">
          <li><b>Truthful bidding is optimal</b> in all 18 second-price scenarios and all 36 fixed-rival profiles (other bids can tie).</li>
          <li><b>Equilibrium shading</b> in first-price auctions is k = 1/2, 2/3, 3/4 for n = 2, 3, 4 – the simulated utility peaks there.</li>
          <li><b>VCG reproduces the book:</b> path ABEF, payments AB = 4, BE = 2, EF = 3, all other edges 0.</li>
        </ul>
      </Card>
    </>
  );
}

function SecondPrice({ data }) {
  const [rivals, setRivals] = useState(1);
  const [value, setValue] = useState(0.5);
  const [strategy, setStrategy] = useState("truthful");
  const [fixedV, setFixedV] = useState(0.5);
  const [fixedR, setFixedR] = useState(1);
  const rows = useMemo(() => data.second_price_bids.filter((r) => r.rivals === rivals && r.value === value && r.strategy === strategy), [data, rivals, value, strategy]);
  const stat = data.second_price.find((r) => r.rivals === rivals && r.value === value && r.strategy === strategy);
  const top = rows.reduce((a, b) => (b.mean_utility > a.mean_utility ? b : a), rows[0]);
  const fixedRows = useMemo(() => {
    const m = {};
    data.fixed_bids.filter((r) => r.rivals === fixedR && r.value === fixedV).forEach((r) => {
      (m[r.bid] = m[r.bid] || { bid: r.bid })["m" + r.max_rival_bid] = r.utility;
    });
    return Object.values(m).sort((a, b) => a.bid - b.bid);
  }, [data, fixedV, fixedR]);
  const maxes = [...new Set(data.fixed_bids.map((r) => r.max_rival_bid))].sort();
  const mcol = [C.blue, C.amber, C.pink];
  return (
    <>
      <Card title="Part A · Expected utility versus own bid" sub="Each point averages 100,000 auctions. The dashed green line marks the truthful bid b = v.">
        <div className="controls">
          <Seg label="Your value" value={value} onChange={setValue} options={[[0.2, "0.2"], [0.5, "0.5"], [0.8, "0.8"]]} />
          <Seg label="Rival strategy" value={strategy} onChange={setStrategy} options={Object.entries(STRAT)} />
          <Seg label="Rivals" value={rivals} onChange={setRivals} options={[[1, "1 rival"], [2, "2 rivals"]]} />
        </div>
        <div className="split">
          <BidChart rows={rows} v={value} height={340} color={SCOLOR[strategy]} />
          <div className="side">
            <Stat label="Utility at b = v" value={f(stat?.mean_utility, 4)} hint={`exact ${f(stat?.exact_utility, 4)}`} color={C.teal} />
            <Stat label="Win rate" value={(100 * (stat?.win_fraction ?? 0)).toFixed(1) + "%"} hint="when bidding truthfully" color={C.blue} />
            <Stat label="Best sampled bid" value={f(top?.bid, 2)} hint={`utility ${f(top?.mean_utility, 4)}`} color={C.amber} />
          </div>
        </div>
        <p className="insight">The curve flattens on a plateau that contains b = v: overbidding adds only auctions that cost more than they are worth, underbidding forfeits profitable wins. So the plots tell bidder 1 nothing beyond “bid your value” – and that holds whichever rival strategy is used.</p>
      </Card>

      <Card title="All nine combinations" sub="One small plot for each value × rival strategy at the selected rival count.">
        <div className="mini-grid">
          {[0.2, 0.5, 0.8].flatMap((v) => Object.keys(STRAT).map((s) => (
            <div className="mini" key={v + s}>
              <div className="mini-title"><span>v = {v}</span><em style={{ color: SCOLOR[s] }}>{STRAT[s]}</em></div>
              <BidChart mini height={150} v={v} color={SCOLOR[s]} rows={data.second_price_bids.filter((r) => r.rivals === rivals && r.value === v && r.strategy === s)} />
            </div>
          )))}
        </div>
      </Card>

      <Card title="Part B · Fixed rival bids" sub="Rival bids fixed at 0.1, 0.4 and 0.9. Utility is highest on a plateau that includes b = v in every case.">
        <div className="controls">
          <Seg label="Your value" value={fixedV} onChange={setFixedV} options={[[0.2, "0.2"], [0.5, "0.5"], [0.8, "0.8"]]} />
          <Seg label="Rivals" value={fixedR} onChange={setFixedR} options={[[1, "1 rival"], [2, "2 rivals"]]} />
        </div>
        <ResponsiveContainer width="100%" height={320}>
          <LineChart data={fixedRows} margin={{ top: 24, right: 14, bottom: 4, left: 0 }}>
            <CartesianGrid stroke={C.grid} strokeDasharray="3 3" />
            <XAxis dataKey="bid" type="number" domain={[0, 1]} {...axis} />
            <YAxis {...axis} />
            <Tooltip {...tip} formatter={(x) => f(x, 3)} />
            <ReferenceLine x={fixedV} stroke={C.green} strokeDasharray="5 4" label={{ value: "b = v", fill: C.green, fontSize: 12, position: "top" }} />
            {maxes.map((m, i) => <Line key={m} type="stepAfter" dataKey={"m" + m} name={`max rival bid ${m}`} stroke={mcol[i]} dot={false} strokeWidth={2.4} isAnimationActive={false} />)}
            <Legend wrapperStyle={{ color: C.text }} />
          </LineChart>
        </ResponsiveContainer>
        <p className="insight">With two rivals only the higher rival bid sets the price, so all nine ordered pairs collapse onto three curves. Truthful bidding is weakly optimal in all 36 value/profile combinations.</p>
      </Card>
    </>
  );
}

function FirstPrice({ data }) {
  const [value, setValue] = useState("uniform");
  const [metric, setMetric] = useState("mean_utility");
  const rows = useMemo(() => {
    const m = {};
    data.first_price.filter((r) => r.value === value && r.on_required_grid).forEach((r) => {
      (m[r.k] = m[r.k] || { k: r.k })["n" + r.n] = r[metric];
    });
    return Object.values(m).sort((a, b) => a.k - b.k);
  }, [data, value, metric]);
  const ns = [2, 3, 4], col = { 2: C.blue, 3: C.teal, 4: C.amber };
  const peak = (n) => data.first_price.filter((r) => r.value === value && r.n === n).reduce((a, b) => (b.mean_utility > a.mean_utility ? b : a));
  const metrics = [["mean_utility", "Expected utility"], ["win_fraction", "Win probability"], ["winner_could_pay_less_fraction", "Winner could pay less"], ["mean_winning_margin", "Winning margin"]];
  return (
    <Card title="First price · deviating from equilibrium" sub="Bidder 1 bids k·v; the other n−1 bidders bid ((n−1)/n)·v. Grid k = 0.1 … 2.0.">
      <div className="controls">
        <Seg label="Bidder 1 value" value={value} onChange={setValue} options={[["uniform", "Uniform"], ["0.2", "0.2"], ["0.5", "0.5"], ["0.8", "0.8"]]} />
        <Seg label="Metric" value={metric} onChange={setMetric} options={metrics} />
      </div>
      <div className="split">
        <ResponsiveContainer width="100%" height={380}>
          <LineChart data={rows} margin={{ top: 24, right: 14, bottom: 14, left: 0 }}>
            <CartesianGrid stroke={C.grid} strokeDasharray="3 3" />
            <XAxis dataKey="k" type="number" domain={[0, 2]} {...axis} tickCount={9} label={{ value: "bid fraction k", position: "insideBottom", offset: -6, fill: C.text }} />
            <YAxis {...axis} />
            <Tooltip {...tip} formatter={(x) => f(x, 4)} labelFormatter={(l) => "k = " + l} />
            <ReferenceLine x={1} stroke={C.red} strokeDasharray="4 4" label={{ value: "k=1 (value)", fill: C.red, fontSize: 11, position: "top" }} />
            {ns.map((n) => <Line key={n} dataKey={"n" + n} name={`n = ${n}`} stroke={col[n]} dot={false} strokeWidth={2.6} isAnimationActive={false} />)}
            <Legend verticalAlign="top" wrapperStyle={{ color: C.text }} />
          </LineChart>
        </ResponsiveContainer>
        <div className="side">
          {ns.map((n) => <Stat key={n} label={`n = ${n} · best k on grid`} value={f(peak(n).k, 2)} hint={`equilibrium ${f((n - 1) / n, 2)}`} color={col[n]} />)}
        </div>
      </div>
      <p className="insight">Utility rises until k reaches the equilibrium shade (n−1)/n and falls beyond it; at k &gt; 1 bidder 1 wins more often but pays more than its value. Nearly every winner could have paid less and still won – hindsight regret that is not exploitable before rival bids are known.</p>
    </Card>
  );
}

function Network({ r, edge, onEdge }) {
  return (
    <svg viewBox="0 0 720 320" className="net">
      <defs>
        <marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10z" fill="#64748b" /></marker>
        <marker id="ahs" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10z" fill={C.teal} /></marker>
      </defs>
      {Object.keys(BOOK_COSTS).map((e) => {
        const [x1, y1] = POS[e[0]], [x2, y2] = POS[e[1]];
        const dx = x2 - x1, dy = y2 - y1, L = Math.hypot(dx, dy), ux = dx / L, uy = dy / L;
        const on = r.selected.has(e), act = e === edge;
        const sx = x1 + ux * 24, sy = y1 + uy * 24, ex = x2 - ux * 26, ey = y2 - uy * 26;
        return (
          <g key={e} onClick={() => onEdge(e)} style={{ cursor: "pointer" }}>
            <line x1={sx} y1={sy} x2={ex} y2={ey} stroke="transparent" strokeWidth="18" />
            <line x1={sx} y1={sy} x2={ex} y2={ey} stroke={on ? C.teal : "#475569"} strokeWidth={on ? 4 : 2} markerEnd={`url(#${on ? "ahs" : "ah"})`} strokeDasharray={on ? "" : "6 4"} />
            <rect x={(sx + ex) / 2 - 30} y={(sy + ey) / 2 - 12} width="60" height="24" rx="12" fill={act ? C.violet : "#0b1220"} stroke={on ? C.teal : "#334155"} />
            <text x={(sx + ex) / 2} y={(sy + ey) / 2 + 4} textAnchor="middle" fill="#e2e8f0" fontSize="12" fontWeight="600">{e} · {f(r.reports[e], 1)}</text>
          </g>
        );
      })}
      {Object.entries(POS).map(([n, [x, y]]) => (
        <g key={n}><circle cx={x} cy={y} r="22" fill="#111c33" stroke={C.blue} strokeWidth="2" /><text x={x} y={y + 6} textAnchor="middle" fill="#fff" fontSize="17" fontWeight="700">{n}</text></g>
      ))}
    </svg>
  );
}

function VCG() {
  const [edge, setEdge] = useState("AB");
  const [report, setReport] = useState(3);
  useEffect(() => setReport(BOOK_COSTS[edge]), [edge]);
  const base = vcg();
  const reports = { ...BOOK_COSTS, [edge]: report };
  const r = { ...vcg(reports), reports };
  const sweep = useMemo(() => {
    const out = [];
    for (let x = 0; x <= 10; x += 0.5) {
      const q = vcg({ ...BOOK_COSTS, [edge]: x });
      out.push({ report: x, utility: q.utilities[edge], path: q.path });
    }
    return out;
  }, [edge]);
  const edges = Object.keys(BOOK_COSTS);
  return (
    <>
      <Card title="Book Figure 7.3 · cheapest path A → F" sub="Click an edge to make it the reporting agent. Teal edges are on the chosen path.">
        <div className="split">
          <Network r={r} edge={edge} onEdge={setEdge} />
          <div className="side">
            <Stat label="Chosen path" value={r.path} hint={`reported cost ${r.cost}`} color={C.teal} />
            <Stat label={`Payment to ${edge}`} value={f(r.payments[edge], 1)} hint={`true cost ${BOOK_COSTS[edge]}`} color={C.amber} />
            <Stat label="Utility at true cost" value={f(r.utilities[edge], 1)} hint={`${(r.utilities[edge] - base.utilities[edge]).toFixed(1)} vs truthful`} color={r.utilities[edge] < base.utilities[edge] ? C.red : C.green} />
          </div>
        </div>
      </Card>
      <Card title="Truthful VCG payments" sub="p = (cheapest path without e) − (cheapest path cost − e's reported cost). Click a row to select the edge.">
        <table className="tbl">
          <thead><tr><th>Edge</th><th>True cost</th><th>Selected</th><th>Payment</th><th>Utility</th></tr></thead>
          <tbody>{edges.map((e) => (
            <tr key={e} className={base.selected.has(e) ? "hl" : ""} onClick={() => setEdge(e)}>
              <td><b>{e}</b></td><td>{BOOK_COSTS[e]}</td><td>{base.selected.has(e) ? "✓" : "–"}</td><td>{f(base.payments[e], 1)}</td><td>{f(base.utilities[e], 1)}</td>
            </tr>))}</tbody>
        </table>
      </Card>
      <Card title={`Misreport experiment · edge ${edge}`} sub="Report any cost from 0 to 10 in steps of 0.5. Utility always uses the true cost.">
        <div className="slider">
          <label>Reported cost <b>{report.toFixed(1)}</b></label>
          <input type="range" min="0" max="10" step="0.5" value={report} onChange={(e) => setReport(+e.target.value)} />
          <button className="ghost" onClick={() => setReport(BOOK_COSTS[edge])}>Reset to truth</button>
        </div>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={sweep} margin={{ top: 24, right: 14, bottom: 4, left: 0 }}>
            <defs><linearGradient id="ug" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor={C.violet} stopOpacity=".5" /><stop offset="100%" stopColor={C.violet} stopOpacity="0" /></linearGradient></defs>
            <CartesianGrid stroke={C.grid} strokeDasharray="3 3" />
            <XAxis dataKey="report" type="number" domain={[0, 10]} {...axis} tickCount={11} />
            <YAxis {...axis} />
            <Tooltip {...tip} formatter={(x, n, p) => [x, `utility (path ${p.payload.path})`]} labelFormatter={(l) => "report = " + l} />
            <ReferenceLine x={BOOK_COSTS[edge]} stroke={C.green} strokeDasharray="5 4" label={{ value: "true cost", fill: C.green, fontSize: 12, position: "top" }} />
            <ReferenceLine x={report} stroke={C.amber} />
            <Area type="stepAfter" dataKey="utility" stroke={C.violet} strokeWidth={2.6} fill="url(#ug)" isAnimationActive={false} />
          </AreaChart>
        </ResponsiveContainer>
        <p className="insight">{base.selected.has(edge)
          ? `${edge} is on the winning path: its payment is independent of its own report while it stays selected, and once it prices itself off the path its utility falls to 0.`
          : `${edge} is off the winning path: underreporting enough to win means being paid less than it truly costs, giving negative utility.`} No misreport beats telling the truth.</p>
      </Card>
    </>
  );
}

function Method() {
  const items = [
    ["Part 1 A", "Own bids 0.00 … 1.00 (step 0.01), at least 100,000 auctions per bid, 3 values × 3 rival strategies, repeated with two rivals. Rival draws are shared across candidate bids."],
    ["Part 1 B", "Rival bids fixed at 0.1, 0.4, 0.9 (all nine ordered pairs for two rivals): b = v is weakly optimal; ties are possible."],
    ["Part 2", "n = 2, 3, 4; bidder 1 bids k·v on k = 0.1 … 2.0 against ((n−1)/n)·v. Reports expected utility and how often the winner could have paid less."],
    ["Part 3", "VCG on the directed graph of Figure 7.3. AB, BE, EF are paid 4, 2, 3; AB and AC are swept over reports 0 … 10."],
    ["Conventions", "Ties go to the lowest bidder index; equal-cost paths use lexical order. Simulations model the stated mechanisms, not human behavior."],
  ];
  return <Card title="Method & coverage"><div className="method">{items.map(([t, d]) => <div key={t}><b>{t}</b><p>{d}</p></div>)}</div></Card>;
}

export default function App() {
  const [data, setData] = useState(null);
  const [tab, setTab] = useState(() => TABS.find((t) => t === decodeURIComponent(location.hash.slice(1))) || "Overview");
  const [err, setErr] = useState(null);
  useEffect(() => {
    fetch("./data.json").then((r) => r.json()).then(setData).catch((e) => setErr(String(e)));
  }, []);
  return (
    <div className="app">
      <header className="hero">
        <div className="orb o1" /><div className="orb o2" />
        <span className="eyebrow">Autonomous Systems · Assignment 04</span>
        <h1>Mechanism <span>Lab</span></h1>
        <p>Second-price auctions, first-price equilibrium deviations and VCG procurement – explored with live, interactive simulations.</p>
        <nav>{TABS.map((t) => <button key={t} className={t === tab ? "on" : ""} onClick={() => setTab(t)}>{t}</button>)}</nav>
      </header>
      <main>
        {err && <Card title="Could not load data">{err}. Run <code>python export_web_data.py</code> first.</Card>}
        {!data && !err && <div className="loading">Loading experiment data…</div>}
        {data && tab === "Overview" && <Overview data={data} go={setTab} />}
        {data && tab === "Second price" && <SecondPrice data={data} />}
        {data && tab === "First price" && <FirstPrice data={data} />}
        {data && tab === "VCG network" && <VCG />}
        {data && tab === "Method" && <Method />}
      </main>
      <footer>Mechanism Lab · seeded, reproducible Monte Carlo experiments</footer>
    </div>
  );
}
