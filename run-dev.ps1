$ErrorActionPreference = 'Stop'
$Root = $PSScriptRoot
$ApiPython = Join-Path $Root 'apps\api\.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $ApiPython -PathType Leaf)) { throw 'Backend dependencies missing. Create apps\api\.venv and install requirements.txt.' }
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) { throw 'npm is required but was not found on PATH.' }
if (-not (Test-Path -LiteralPath (Join-Path $Root 'apps\web\node_modules') -PathType Container)) { throw 'Frontend dependencies missing. Run: cd apps\web; npm install' }
Write-Host 'MEIP backend: http://localhost:8000'
Write-Host 'MEIP frontend: http://localhost:5173'
Start-Process -FilePath $ApiPython -ArgumentList '-m','uvicorn','app.main:app','--reload','--port','8000' -WorkingDirectory (Join-Path $Root 'apps\api') -WindowStyle Hidden
Start-Process -FilePath 'npm.cmd' -ArgumentList 'run','dev','--','--host','localhost' -WorkingDirectory (Join-Path $Root 'apps\web') -WindowStyle Hidden
Write-Host 'Both development servers were started.'
