$target = '192.168.233.129'
$openPorts = @()

$ranges = @(
    @(1..1024),
    @(1080..1090),
    @(1433..1435),
    @(1521..1522),
    @(2049..2050),
    @(3000..3010),
    @(3306..3307),
    @(3389..3390),
    @(4000..4010),
    @(4443..4445),
    @(5000..5010),
    @(5432..5433),
    @(5900..5910),
    @(5985..5986),
    @(6000..6010),
    @(6379..6380),
    @(7000..7010),
    @(7777..7780),
    @(8000..8100),
    @(8080..8090),
    @(8443..8450),
    @(8888..8890),
    @(9000..9010),
    @(9090..9100),
    @(9999..10010),
    @(10000..10010),
    @(27017..27018),
    @(30000..30100),
    @(50000..50100)
)

Write-Host "Scanning $target ..."
$startTime = Get-Date

$runspacePool = [RunspaceFactory]::CreateRunspacePool(1, 100)
$runspacePool.Open()
$jobs = @()

foreach ($range in $ranges) {
    foreach ($port in $range) {
        $ps = [PowerShell]::Create()
        $ps.RunspacePool = $runspacePool
        $null = $ps.AddScript({
            param($t, $p)
            $tcp = New-Object System.Net.Sockets.TCPClient
            $tcp.ReceiveTimeout = 800
            $tcp.SendTimeout = 800
            try {
                $tcp.Connect($t, $p)
                if ($tcp.Connected) { return $p }
            } catch {}
            $tcp.Close()
            return $null
        }).AddArgument($target).AddArgument($port)
        $jobs += [PSCustomObject]@{ PS = $ps; Handle = $ps.BeginInvoke() }
    }
}

foreach ($job in $jobs) {
    $result = $job.PS.EndInvoke($job.Handle)
    if ($result -and $result[0]) {
        $openPorts += $result[0]
        Write-Host "[+] OPEN: $($result[0])" -ForegroundColor Green
    }
    $job.PS.Dispose()
}

$runspacePool.Close()
$runspacePool.Dispose()

$elapsed = (Get-Date) - $startTime
Write-Host ""
Write-Host "Scan done! Time: $($elapsed.TotalSeconds) sec"
Write-Host "Open ports: $($openPorts -join ', ')"

if ($openPorts.Count -eq 0) {
    Write-Host ""
    Write-Host "[!] No open ports found in common ranges. Full scan..."
    $runspacePool2 = [RunspaceFactory]::CreateRunspacePool(1, 200)
    $runspacePool2.Open()
    $batchJobs = @()
    
    for ($p = 1; $p -le 65535; $p++) {
        $ps = [PowerShell]::Create()
        $ps.RunspacePool = $runspacePool2
        $null = $ps.AddScript({
            param($t, $p)
            $tcp = New-Object System.Net.Sockets.TCPClient
            $tcp.ReceiveTimeout = 400
            try {
                $tcp.Connect($t, $p)
                if ($tcp.Connected) { return $p }
            } catch {}
            $tcp.Close()
            return $null
        }).AddArgument($target).AddArgument($p)
        $batchJobs += [PSCustomObject]@{ PS = $ps; Handle = $ps.BeginInvoke() }
        
        if ($batchJobs.Count -ge 200) {
            foreach ($job in $batchJobs) {
                $result = $job.PS.EndInvoke($job.Handle)
                if ($result -and $result[0]) {
                    $openPorts += $result[0]
                    Write-Host "[+] OPEN: $($result[0])" -ForegroundColor Green
                }
                $job.PS.Dispose()
            }
            $batchJobs = @()
            if ($p % 2000 -eq 0) { Write-Host "  Scanned up to port $p ..." }
        }
    }
    
    foreach ($job in $batchJobs) {
        $result = $job.PS.EndInvoke($job.Handle)
        if ($result -and $result[0]) {
            $openPorts += $result[0]
            Write-Host "[+] OPEN: $($result[0])" -ForegroundColor Green
        }
        $job.PS.Dispose()
    }
    
    $runspacePool2.Close()
    $runspacePool2.Dispose()
    Write-Host ""
    Write-Host "Full scan done!"
    Write-Host "Open ports: $($openPorts -join ', ')"
}

$openPorts | Out-File -FilePath "open_ports.txt"
Write-Host "Results saved to open_ports.txt"