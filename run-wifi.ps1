$ErrorActionPreference = 'Stop'
$Root = $PSScriptRoot
$WifiConfiguration = Get-NetIPConfiguration | Where-Object {
    $_.NetAdapter.Status -eq 'Up' -and $_.IPv4Address -and $_.IPv4DefaultGateway
} | Select-Object -First 1
if (-not $WifiConfiguration) { throw 'No active IPv4 network with a default gateway was found.' }
$WifiAddress = $WifiConfiguration.IPv4Address.IPAddress
$ApiDirectory = Join-Path $Root 'apps\api'
$WebDirectory = Join-Path $Root 'apps\web'
$ApiPython = Join-Path $ApiDirectory '.venv\Scripts\python.exe'

if (-not (Test-Path -LiteralPath $ApiPython -PathType Leaf)) {
    throw 'Backend virtual environment is missing.'
}
if (-not (Test-Path -LiteralPath (Join-Path $WebDirectory 'node_modules') -PathType Container)) {
    throw 'Frontend dependencies are missing. Run npm install in apps\web.'
}

$env:CORS_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173,http://${WifiAddress}:5173"
$api = Start-Process -FilePath $ApiPython -ArgumentList '-m','uvicorn','app.main:app','--host','0.0.0.0','--port','8000' -WorkingDirectory $ApiDirectory -WindowStyle Hidden -PassThru

$env:VITE_API_BASE_URL = "http://${WifiAddress}:8000"
$web = Start-Process -FilePath 'npm.cmd' -ArgumentList 'run','dev','--','--host','0.0.0.0' -WorkingDirectory $WebDirectory -WindowStyle Hidden -PassThru

Write-Host "Frontend: http://${WifiAddress}:5173"
Write-Host "Backend:  http://${WifiAddress}:8000"
Write-Host "Process IDs: API=$($api.Id), Web=$($web.Id)"
