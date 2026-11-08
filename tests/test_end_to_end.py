import json
from pathlib import Path
import subprocess
import sys
from streamlit.testing.v1 import AppTest

ROOT=Path(__file__).resolve().parents[1]


def test_batch_cli_writes_complete_report(tmp_path):
    result=subprocess.run([sys.executable,str(ROOT/'run_experiments.py'),'--trials','3000',
        '--seed','42','--output',str(tmp_path)],cwd=ROOT,capture_output=True,text=True,timeout=120)
    assert result.returncode==0, result.stdout+result.stderr
    validation=json.loads((tmp_path/'validation.json').read_text())
    assert all(validation['checks'].values())
    assert len(list(tmp_path.glob('*.csv')))==6
    assert len(list(tmp_path.glob('*.png')))==10
    assert len(list((tmp_path/'part1a').glob('*.png')))==9
    assert len(list((tmp_path/'part1c').glob('*.png')))==9
    report=(tmp_path/'REPORT.md').read_text(encoding='utf-8')
    assert all(text in report for text in ('Part 1','Part 2','Part 3','ABEF','weakly','0.01'))
    for image in tmp_path.rglob('*.png'):
        assert image.read_bytes().startswith(b'\x89PNG') and image.stat().st_size>10000


def test_dashboard_controls_and_vcg_deviation():
    app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=90).run()
    assert not app.exception
    assert len(app.tabs)==4
    # Address controls by label; sidebar/main ordering varies by Streamlit release.
    assert next(w for w in app.selectbox if w.label=='Trials per configuration').value==100_000
    next(w for w in app.selectbox if w.label=='Rivals in the nine-plot grid').select(2).run()
    next(w for w in app.selectbox if w.label=='Bidder 1 valuation').select('0.8').run()
    next(w for w in app.selectbox if w.label=='Reporting edge').select('AC').run()
    app.slider[0].set_value(0.).run()
    assert not app.exception
    metric_values={m.label:m.value for m in app.metric}
    assert metric_values['Chosen path']=='ACEF'
    assert metric_values['Payment to edge']=='1.0'
    assert metric_values['Utility at true cost']=='-1.0'
    app.number_input[0].set_value(7).run()
    assert not app.exception
