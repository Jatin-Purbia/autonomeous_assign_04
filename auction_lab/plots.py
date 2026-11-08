"""Publication-style figures shared by the dashboard and batch report."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from .core import BOOK_COSTS, VALUES, STRATEGIES

plt.rcParams.update({"figure.facecolor":"#f7f9fc", "axes.facecolor":"white",
                     "axes.spines.top":False, "axes.spines.right":False,
                     "axes.grid":True, "grid.alpha":.18, "font.size":10})
COLORS = ["#2563eb", "#0d9488", "#e17821"]


def second_plot(df):
    fig, axes = plt.subplots(1,2,figsize=(11,4), constrained_layout=True)
    for ax, rivals in zip(axes,(1,2)):
        for color, strategy in zip(COLORS,("truthful","half","random")):
            sub = df[(df.rivals==rivals)&(df.strategy==strategy)]
            ax.errorbar(sub.value,sub.mean_utility,yerr=1.96*sub.standard_error,
                        marker="o",label=strategy,color=color, capsize=4)
            ax.scatter(sub.value,sub.exact_utility,marker="x",color=color)
        ax.set(title=f"{rivals} rival bidder(s)",xlabel="Bidder 1 value",ylabel="Expected utility")
        ax.legend()
    fig.suptitle("Second price: truthful bidder 1 | bars: 95% CI, crosses: exact")
    return fig


def fixed_plot(df):
    fig, axes=plt.subplots(1,3,figsize=(12,3.8),constrained_layout=True)
    for ax,v in zip(axes,VALUES):
        for color,m in zip(COLORS,(.1,.4,.9)):
            sub=df[(df.rivals==1)&(df.value==v)&(df.max_rival_bid==m)]
            ax.step(sub.bid,sub.utility,where="post",label=f"Max rival = {m}",color=color)
        ax.axvline(v,color="#334155",linestyle="--",label="Truthful bid")
        ax.set(title=f"Value = {v}",xlabel="Bidder 1 bid",ylabel="Utility")
        ax.legend(fontsize=8)
    fig.suptitle("Truthful bidding is weakly optimal for every fixed rival profile")
    return fig


def _draw_second_bid(ax,df,rivals,v,strategy):
    sub=df[(df.rivals==rivals)&(df.value==v)&(df.strategy==strategy)]
    color=COLORS[STRATEGIES.index(strategy)]
    ax.plot(sub.bid,sub.mean_utility,label='Average utility',color=color)
    ax.plot(sub.bid,sub.exact_utility,label='Exact expectation',color='#64748b',linestyle=':',alpha=.7)
    ax.fill_between(sub.bid,sub.ci95_low,sub.ci95_high,color=color,alpha=.12)
    ax.axvline(v,color='#334155',linestyle='--',label='Truthful own bid')
    ax.axhline(0,color='#94a3b8',linewidth=.7)
    ax.set(title=f'Value = {v} | rival strategy: {strategy}',xlabel='Bidder 1 bid',ylabel='Average utility')
    ax.set_xlim(0,1)
    ax.legend(fontsize=7)


def second_bid_plot(df,rivals,v,strategy):
    """One assignment plot for one fixed value and rival strategy."""
    fig,ax=plt.subplots(figsize=(7,4.5),constrained_layout=True)
    _draw_second_bid(ax,df,rivals,v,strategy)
    fig.suptitle(f'Second-price auction | {rivals} rival bidder(s) | shading: 95% CI')
    return fig


def second_sweep_plot(df,rivals=1):
    """Nine separate axes: value rows by rival-strategy columns."""
    fig,axes=plt.subplots(3,3,figsize=(13,10),constrained_layout=True)
    for row,v in enumerate(VALUES):
        for col,strategy in enumerate(STRATEGIES):
            _draw_second_bid(axes[row,col],df,rivals,v,strategy)
    fig.suptitle(f'Nine bid-utility plots | {rivals} rival bidder(s) | rows: value; columns: rival strategy')
    return fig


def first_plot(df, value="uniform"):
    fig,axes=plt.subplots(1,3,figsize=(12,4),constrained_layout=True)
    for ax,n in zip(axes,(2,3,4)):
        sub=df[(df.n==n)&(df.value==str(value))]
        ax.plot(sub.k,sub.exact_utility,color=COLORS[0],label="Exact")
        ax.errorbar(sub.k,sub.mean_utility,yerr=1.96*sub.standard_error,
                    fmt=".",color=COLORS[1],label="Simulation (95% CI)")
        ax.axvline((n-1)/n,color=COLORS[2],linestyle="--",label="Equilibrium k")
        ax.axhline(0,color="#64748b",linewidth=.7)
        ax.set(title=f"n = {n}",xlabel="Bid fraction k",ylabel="Expected utility")
        ax.legend(fontsize=8)
    fig.suptitle(f"First price: bidder 1 value = {value}")
    return fig


def network_plot():
    fig, ax=plt.subplots(figsize=(8,4),constrained_layout=True)
    pos={"A":(0,1),"B":(1,2),"C":(1,0),"D":(2.5,2),"E":(2.5,0),"F":(3.5,1)}
    selected={"AB","BE","EF"}
    for edge,c in BOOK_COSTS.items():
        x,y=pos[edge[0]]; X,Y=pos[edge[1]]
        color=COLORS[1] if edge in selected else "#94a3b8"
        ax.annotate("",(X,Y),(x,y),arrowprops=dict(arrowstyle="->",color=color,
                    lw=3 if edge in selected else 1.5,shrinkA=19,shrinkB=19))
        # Separate labels on the two crossing diagonals.
        t=.36 if edge=="BE" else .58 if edge=="CF" else .5
        ax.text(x+t*(X-x),y+t*(Y-y)+.1,f"{c:g}",ha="center",color="#0f172a",
                bbox=dict(facecolor="white",edgecolor="none",pad=2))
    for name,(x,y) in pos.items():
        ax.scatter(x,y,s=1100,color="white",edgecolors="#334155",zorder=4)
        ax.text(x,y,name,ha="center",va="center",weight="bold",zorder=5)
    ax.set(xlim=(-.4,3.9),ylim=(-.4,2.4),title="Figure 7.3 | selected route A-B-E-F | true cost 5")
    ax.axis("off")
    return fig


def vcg_plot(df):
    fig,axes=plt.subplots(1,2,figsize=(10,4),constrained_layout=True)
    for ax,edge,color in zip(axes,("AB","AC"),COLORS):
        sub=df[df.edge==edge]
        ax.plot(sub.report,sub.utility,"o-",color=color,label="Utility at true cost")
        ax.axvline(sub.true_cost.iloc[0],color="#64748b",linestyle="--",label="Truthful report")
        ax.set(title=f"Edge {edge} ({'on' if edge=='AB' else 'off'} truthful path)",
               xlabel="Reported cost",ylabel="Payment minus true cost if selected")
        ax.legend(fontsize=8)
    fig.suptitle("VCG: unilateral misreporting never improves utility")
    return fig
