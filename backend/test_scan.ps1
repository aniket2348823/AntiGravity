$target = "http://localhost:5050"
$scanApi = "http://localhost:5000/api/scan"
$statusApi = "http://localhost:5000/api/status"
$historyApi = "http://localhost:5000/api/history"

# 1. Start Scan
Write-Host "Starting scan on $target..."
$body = @{ target_url = $target } | ConvertTo-Json
try {
    $response = Invoke-RestMethod -Uri $scanApi -Method Post -Body $body -ContentType "application/json"
    Write-Host "Scan started: $($response.message)"
} catch {
    Write-Error "Failed to start scan: $_"
    exit 1
}

# 2. Poll Status
Write-Host "Polling status..."
$maxRetries = 30
$retry = 0
Do {
    Start-Sleep -Seconds 2
    $status = Invoke-RestMethod -Uri $statusApi -Method Get
    $logs = $status.logs | Select-Object -Last 1
    Write-Host "Status: Scanning... Last log: $logs"
    $retry++
} While ($status.is_scanning -and $retry -lt $maxRetries)

if ($status.is_scanning) {
    Write-Host "Scan timed out or is taking too long."
} else {
    Write-Host "Scan Completed!"
}

# 3. Get Results
Write-Host "Findings:"
$status.current_findings | Format-Table -Property name, severity, url -AutoSize

# 4. Get Report ID (Last scan)
$history = Invoke-RestMethod -Uri $historyApi -Method Get
if ($history.Count -gt 0) {
    $lastScan = $history[$history.Count - 1]
    $scanId = $lastScan.id
    Write-Host "Last Scan ID: $scanId"
    
    # Check Report URL
    $reportUrl = "http://localhost:5000/api/report/$scanId"
    Write-Host "Downloading report from $reportUrl..."
    try {
        Invoke-WebRequest -Uri $reportUrl -OutFile "test_report.pdf"
        Write-Host "Report downloaded to test_report.pdf"
    } catch {
       Write-Error "Failed to download report: $_"
    }
} else {
    Write-Host "No history found?"
}
