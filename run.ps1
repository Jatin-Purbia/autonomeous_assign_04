param(
    [ValidateSet('app','build','experiments','test')]
    [string]$Action = 'app'
)
$ErrorActionPreference = 'Stop'
$projectPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $projectPython)) { $projectPython = 'python' }
Push-Location $PSScriptRoot
try {
    switch ($Action) {
        'app' {
            & $projectPython export_web_data.py
            Push-Location web
            try { if (-not (Test-Path node_modules)) { npm install }; npm run dev } finally { Pop-Location }
        }
        'build' { & $projectPython export_web_data.py; Push-Location web; try { npm install; npm run build } finally { Pop-Location } }
        'experiments' { & $projectPython run_experiments.py --trials 100000 --seed 42 }
        'test' {
            $previousPluginSetting = $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD
            $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = '1'
            try { & $projectPython -m pytest -q }
            finally { $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = $previousPluginSetting }
        }
    }
    $runExitCode = $LASTEXITCODE
} finally { Pop-Location }
exit $runExitCode
