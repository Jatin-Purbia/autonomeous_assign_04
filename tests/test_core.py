import itertools
import numpy as np
import pytest
from auction_lab.core import (auction, rival_bids, second_price_expected,
                              first_price_expected, shortest_path, vcg, BOOK_COSTS)
from auction_lab.experiments import (run_all, fixed_bid_experiments, monte_carlo_close,
                                     second_price_bid_sweeps)


@pytest.mark.parametrize('pricing,payment',[('second',.4),('first',.8)])
def test_payment_and_losers(pricing,payment):
    r=auction([.8,.7,.3],[.8,.4,.2],pricing)
    assert r.winner==0 and r.payment==payment
    assert r.utilities==pytest.approx((.8-payment,0,0))


def test_overbidding_can_lose_money_and_ties():
    assert auction([.2,.8],[1.,.9]).utilities[0]==pytest.approx(-.7)
    assert auction([.5,.5],[.5,.5]).winner==0
    assert auction([.2,.9],[.2,.9]).utilities[0]==0


@pytest.mark.parametrize('values,bids', [([1],[1]),([1,2],[1]),([1,-1],[1,0]),([1,1],[float('nan'),0])])
def test_reject_invalid_auction(values,bids):
    with pytest.raises(ValueError): auction(values,bids)


def test_truthful_dominance_including_bids_outside_grid():
    rng=np.random.default_rng(7)
    for rivals in (1,2):
        for _ in range(400):
            v=float(rng.random()); other=rng.random(rivals).tolist()
            values=[v]+[1]*rivals
            truthful=auction(values,[v]+other).utilities[0]
            for b in (0.,2.,float(rng.uniform(0,2))):
                assert auction(values,[b]+other).utilities[0]<=truthful+1e-12
    df=fixed_bid_experiments()
    assert len(df)==3636 and df.truthful_is_optimal.all()
    assert len(df[['rivals','rival_bids','value']].drop_duplicates())==36


def test_rival_strategies_and_independence():
    for strategy in ('truthful','half','random'):
        values,bids=rival_bids(np.random.default_rng(1),20_000,2,strategy)
        if strategy=='truthful': assert np.array_equal(values,bids)
        elif strategy=='half': assert np.array_equal(values/2,bids)
        else: assert abs(np.corrcoef(values.ravel(),bids.ravel())[0,1])<.03
        assert abs(np.corrcoef(values.T)[0,1])<.03


def test_random_rival_own_bid_sweeps_against_auction_rules():
    trials,seed=17,123
    frame=second_price_bid_sweeps(trials,seed)
    assert len(frame)==1818 and frame.truthful_is_optimal.all()
    rng=np.random.default_rng(seed)
    for rivals,strategy in itertools.product((1,2),('truthful','half','random')):
        values,bids=rival_bids(rng,trials,rivals,strategy)
        sub=frame[(frame.rivals==rivals)&(frame.strategy==strategy)]
        for row in sub.itertuples():
            samples=[auction([row.value]+list(vals),[row.bid]+list(bs)).utilities[0]
                     for vals,bs in zip(values,bids)]
            assert row.mean_utility==pytest.approx(np.mean(samples),abs=1e-12)
            assert row.standard_error==pytest.approx(np.std(samples,ddof=1)/np.sqrt(trials),abs=1e-8)
    assert second_price_expected(.2,1,'truthful',bid=1)==pytest.approx(-.3)
    assert second_price_expected(.2,1,'half',bid=1)==pytest.approx(-.05)


@pytest.mark.parametrize('m,strategy,v,expected',[(1,'truthful',.8,.32),(1,'half',.8,.55),
    (2,'truthful',.5,.5**3/3),(2,'half',.8,.8-1/3)])
def test_second_price_exact(m,strategy,v,expected):
    assert second_price_expected(v,m,strategy)==pytest.approx(expected)


@pytest.mark.parametrize('n',[2,3,4])
def test_first_price_equilibrium_and_integral(n):
    a=(n-1)/n
    for v in (.2,.5,.8):
        optimum=first_price_expected(n,a,v)
        assert all(first_price_expected(n,k,v)<=optimum+1e-12 for k in np.linspace(.1,2,1000))
    xs=np.linspace(0,1,20001)
    for k in (.1,a,1.,2.):
        numerical=np.trapz([(1-k)*v*min(k*v/a,1)**(n-1) for v in xs],xs)
        assert first_price_expected(n,k)==pytest.approx(numerical,abs=1e-8)


def test_book_path_counterfactuals_payments():
    r=vcg()
    assert r['path']=='ABEF' and r['reported_cost']==5
    assert r['payments']=={'AB':4,'AC':0,'BD':0,'BE':2,'CE':0,'CF':0,'DF':0,'EF':3}
    assert r['utilities']['AB']==1 and r['utilities']['BE']==1 and r['utilities']['EF']==2
    for edge,cost,path in [('AB',6,('A','C','E','F')),('BE',6,('A','C','E','F')),('EF',7,('A','B','D','F'))]:
        assert shortest_path(BOOK_COSTS,edge)==(cost,path)


def test_vcg_all_edges_truthful_dominance():
    baseline=vcg()
    for edge,report in itertools.product(BOOK_COSTS,np.arange(0,10.01,.5)):
        r=vcg(dict(BOOK_COSTS,**{edge:float(report)}))
        assert r['utilities'][edge]<=baseline['utilities'][edge]+1e-12
    # Misreporting changes allocation but never the true cost in utility.
    r=vcg(dict(BOOK_COSTS,AC=0))
    assert r['path']=='ACEF' and r['payments']['AC']==1 and r['utilities']['AC']==-1


def test_full_simulation_against_theory_and_reproducible():
    data=run_all(20_000,19)
    repeat=run_all(20_000,19)
    for name in data: assert data[name].equals(repeat[name])
    assert len(data['second_price'])==18
    assert len(data['vcg_deviations'])==42
    assert len(data['first_price'])==248
    for name in ('second_price','first_price'):
        df=data[name]
        assert monte_carlo_close(df,20_000).all()
    fp=data['first_price']
    assert (fp.winner_could_pay_less_fraction==1).all()
    assert fp.winner_could_save_001_fraction.between(0,1).all()
    assert (fp.mean_winning_margin>0).all()
    assert (fp[fp.k>1].mean_utility<0).all()
