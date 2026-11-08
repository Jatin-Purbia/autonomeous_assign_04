"""Launch with: python -m streamlit run app.py"""
import matplotlib.pyplot as plt
import streamlit as st
from auction_lab.experiments import run_all
from auction_lab.core import vcg, BOOK_COSTS
from auction_lab.plots import second_plot, second_sweep_plot, fixed_plot, first_plot, network_plot, vcg_plot

st.set_page_config(page_title="Mechanism Lab",page_icon="⚖️",layout="wide")
st.markdown("""<style>
.stApp {background:#f5f7fb;} h1,h2,h3 {color:#14243a;}
[data-testid="stMetric"] {background:white;border:1px solid #e2e8f0;border-radius:14px;padding:18px;}
[data-testid="stSidebar"] {background:#eaf0f8;}
.table-scroll {overflow:auto;max-height:360px;border:1px solid #dce4ee;border-radius:10px;background:white;}
.data-table {width:100%;font-size:13px;border-collapse:collapse;white-space:nowrap;}
.data-table th {background:#eaf0f8;text-align:left;position:sticky;top:0;}
.data-table th,.data-table td {padding:9px 12px;border-bottom:1px solid #edf1f7;}
</style>""",unsafe_allow_html=True)
st.caption("AUTONOMOUS SYSTEMS / ASSIGNMENT 04")
st.title("Mechanism Lab")
st.markdown("Explore how bidding rules shape utility, competition, and truthful behavior.")
with st.sidebar:
    st.header("Experiment controls")
    trials=st.selectbox("Trials per configuration",[100_000,200_000],index=0)
    seed=int(st.number_input("Random seed",min_value=0,max_value=2**32-1,value=42,step=1))
    st.caption("Change the seed to repeat the simulation. Error bars show 95% Monte Carlo confidence intervals.")
    st.info("All ties go to the lowest bidder index. Path ties use lexical order.")


@st.cache_data(show_spinner="Running auction experiments...")
def experiments(trials,seed):
    return run_all(trials,seed)


def show(fig):
    st.pyplot(fig)
    plt.close(fig)


def download(frame,name):
    st.download_button("Download "+name.replace('_',' '),frame.to_csv(index=False),
                       file_name=name+'.csv',mime='text/csv',key=name)


def show_table(frame):
    # HTML tables keep this dashboard independent of optional Arrow binary builds.
    markup=frame.head(100).to_html(index=False,border=0,classes='data-table',
                                  float_format=lambda x:f'{x:.6f}')
    st.markdown('<div class="table-scroll">'+markup+'</div>',unsafe_allow_html=True)
    if len(frame)>100:
        st.caption(f"Showing 100 of {len(frame):,} rows. Download the CSV for the complete table.")


data=experiments(trials,seed)
c1,c2,c3=st.columns(3)
c1.metric("Second-price configurations","18")
c2.metric("First-price bidders","2 / 3 / 4")
c3.metric("VCG truthful route",vcg()['path'])
tab1,tab2,tab3,tab4=st.tabs(["01 · Second price","02 · First price","03 · VCG network","Methods & coverage"])
with tab1:
    st.header("Truthfulness under a second-price rule")
    st.write("Bidder 1 bids its value: 0.2, 0.5, or 0.8. One or two rivals bid truthfully, half their value, or an independent random bid.")
    show(second_plot(data['second_price']))
    show_table(data['second_price'])
    download(data['second_price'],'second_price')
    st.subheader('Part A: compare every own bid')
    st.caption('Required bid grid: 0.00 to 1.00 in steps of 0.01, with at least 100,000 auctions per bid. Each comparison shares rival draws; negative utilities from overbidding are retained.')
    sweep_rivals=st.selectbox('Rivals in the nine-plot grid',[1,2])
    show(second_sweep_plot(data['second_price_bids'],sweep_rivals))
    if data['second_price_bids'].truthful_is_optimal.all():
        st.success('Truthful own bidding maximizes sampled utility in all 18 value/strategy/rival-count scenarios; other bids may tie.')
    download(data['second_price_bids'],'second_price_bids')
    st.subheader("Fix the rival bids")
    show(fixed_plot(data['fixed_bids']))
    st.success("All 36 value/profile combinations confirm b=v is weakly optimal.")
    st.write("With two rivals, the nine ordered bid pairs are checked. Only their maximum determines the price. Multiple bids may maximize utility.")
    profile=st.selectbox("Two-rival profile",sorted(data['fixed_bids'].query('rivals == 2').rival_bids.unique()))
    show_table(data['fixed_bids'].query('rivals == 2 and rival_bids == @profile'))
    download(data['fixed_bids'],'fixed_bids')
with tab2:
    st.header("How far should bidder 1 shade its bid?")
    st.latex(r"b_1=kv_1,\qquad b_j=\frac{n-1}{n}v_j,\qquad u_1=(v_1-b_1)\mathbf{1}\{b_1\geq \max_{j>1}b_j\}")
    value=st.selectbox("Bidder 1 valuation",["uniform","0.2","0.5","0.8"])
    show(first_plot(data['first_price'],value))
    st.info("Equilibrium k = 0.5, 2/3, 0.75. Exact equilibrium references are included alongside the required 0.1 to 2.0 grid.")
    frame=data['first_price']; sub=frame[frame.value==value]
    show_table(sub)
    st.subheader("The price of hindsight")
    st.write("With continuous bids the winner could pay slightly less and still win almost surely. This does not imply a profitable strategy before seeing rival bids. The winning margin measures how much room existed; the exact gap is a supremum for a strict win.")
    show_table(sub[['n','k','winner_could_pay_less_fraction','winner_could_save_001_fraction','mean_winning_margin']])
    download(frame,'first_price')
with tab3:
    st.header("Buy the cheapest A-to-F path")
    st.caption("Book Figure 7.3 · printed page 300 · PDF page 349 · directed graph")
    show(network_plot())
    st.latex(r"p_e=C_{-e}-(C^*-\hat c_e),\qquad u_e=p_e-c_e\quad\text{if selected}")
    show_table(data['vcg_payments'])
    st.success("ABEF costs 5. Payments: AB = 4, BE = 2, EF = 3; every other edge = 0.")
    show(vcg_plot(data['vcg_deviations']))
    st.subheader("Try a unilateral cost report")
    edge=st.selectbox("Reporting edge",["AB","AC"])
    report=st.slider("Reported edge cost",0.,10.,float(BOOK_COSTS[edge]),.5)
    result=vcg(dict(BOOK_COSTS,**{edge:report}))
    baseline=vcg()
    a,b,c=st.columns(3)
    a.metric("Chosen path",result['path'])
    b.metric("Payment to edge",f"{result['payments'][edge]:.1f}")
    c.metric("Utility at true cost",f"{result['utilities'][edge]:.1f}",
             delta=f"{result['utilities'][edge]-baseline['utilities'][edge]:.1f} vs truthful")
    st.caption(f"The true cost of {edge} stays {BOOK_COSTS[edge]:g}, regardless of its report.")
    show_table(data['vcg_deviations'])
    download(data['vcg_deviations'],'vcg_deviations')
with tab4:
    st.header("Assignment coverage")
    st.markdown("""- **Part 1A:** sweep own bids 0,0.01,...,1 for all three fixed values and rival strategies: nine separate plots for one rival, repeated for two rivals. At least 100,000 auctions per bid; exact expectations, win rates, standard errors, and 95% intervals.
- **Fixed rival checks:** bids 0.1, 0.4, 0.9; all nine ordered two-rival profiles; own bid sweep 0 to 1 in 0.01 steps; a dominance argument covering bids outside the grid.
- **Part 2:** n=2,3,4; k=0.1,...,2.0; equilibrium references; conditional and ex ante expected utilities; all-winner payment reduction frequency and winning margins.
- **Part 3:** book graph, shortest path, counterfactual VCG payments, true-cost utilities; AB and AC reports 0,...,10 in steps of 0.5.
- **Reproducibility:** seeded generators, exported tables, plots, analytical benchmarks, automated model and application tests.

The repeated 'parts A and C' is interpreted as repeating both second-price experiments with two rivals. Since Part 2 leaves bidder 1's valuation unspecified, both fixed and independent uniform values are included. Payment in VCG means money received by the edge. All bids and costs are nonnegative.

Run `python run_experiments.py` for the full report and plots in `results/`. Run `python -m pytest -q` for tests. These are simulations of the specified models, not observations of human bidding.
""")
