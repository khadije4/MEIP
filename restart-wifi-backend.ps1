$ErrorActionPreference = 'Stop'
$listener = Get-NetTCPConnection -State Listen -LocalPort 8000 -ErrorAction Stop
if (@($listener).Count -ne 1) { throw "Expected one backend listener, found $(@($listener).Count)." }
$owner = Get-Process -Id $listener.OwningProcess -ErrorAction Stop
if ($owner.ProcessName -notmatch 'python|uvicorn') { throw "Unexpected port 8000 owner: $($owner.ProcessName)." }
Stop-Process -Id $owner.Id -ErrorAction Stop
$configuration = Get-NetIPConfiguration | Where-Object {
    $_.NetAdapter.Status -eq 'Up' -and $_.IPv4Address -and $_.IPv4DefaultGateway
} | Select-Object -First 1
if (-not $configuration) { throw 'No active IPv4 network with a default gateway was found.' }
$wifiAddress = $configuration.IPv4Address.IPAddress
$env:FRONTEND_URL = "http://localhost:5173,http://127.0.0.1:5173,http://${wifiAddress}:5173"
$python = Join-Path $PSScriptRoot 'apps\api\.venv\Scripts\python.exe'
$apiDirectory = Join-Path $PSScriptRoot 'apps\api'
Start-Process -FilePath $python -ArgumentList '-m','uvicorn','app.main:app','--host','0.0.0.0','--port','8000' -WorkingDirectory $apiDirectory -WindowStyle Hidden
Start-Sleep -Seconds 5
Invoke-RestMethod -Uri "http://${wifiAddress}:8000/" -TimeoutSec 10 | ConvertTo-Json
