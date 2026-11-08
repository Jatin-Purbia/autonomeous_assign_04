# Mechanism Lab — Autonomous Systems, Assignment 04

## Setup

```powershell
python -m pip install -r requirements.txt
```

## Run the experiments

```powershell
python run_experiments.py --trials 100000 --seed 42
```

## Run the tests

```powershell
python -m pytest -q
```

## Run the dashboard (needs Node 18+)

```powershell
python export_web_data.py
cd web
npm install
npm run dev
```

Open http://localhost:5173.

## Shortcuts (Windows, uses the local `.venv`)

```powershell
.\run.ps1 experiments
.\run.ps1 test
.\run.ps1 app
```
