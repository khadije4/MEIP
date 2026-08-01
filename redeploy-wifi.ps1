$ErrorActionPreference = 'Stop'

function Stop-ValidatedListener([int]$Port, [string]$ExpectedProcess) {
    $listeners = @(Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue)
    if ($listeners.Count -eq 0) { return }
    if ($listeners.Count -ne 1) { throw "Expected at most one listener on port $Port; found $($listeners.Count)." }
    $owner = Get-Process -Id $listeners[0].OwningProcess -ErrorAction Stop
    if ($owner.ProcessName -notmatch $ExpectedProcess) {
        throw "Unexpected owner of port ${Port}: $($owner.ProcessName)."
    }
    Stop-Process -Id $owner.Id -ErrorAction Stop
}

Stop-ValidatedListener -Port 8000 -ExpectedProcess 'python|uvicorn'
Stop-ValidatedListener -Port 5173 -ExpectedProcess 'node'
Start-Sleep -Seconds 2
& (Join-Path $PSScriptRoot 'run-wifi.ps1')
