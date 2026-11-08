import json
from pathlib import Path
import subprocess
import sys

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


def test_web_data_export(tmp_path):
    import json
    import export_web_data
    out=tmp_path/'data.json'
    export_web_data.main(ROOT/'results',out)
    data=json.loads(out.read_text(encoding='utf-8'))
    assert {'second_price','second_price_bids','fixed_bids','first_price','vcg_payments','vcg_deviations','meta'}<=set(data)
