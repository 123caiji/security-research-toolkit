$ports = @(8080, 8081, 8090, 30000, 30001, 30002, 40000, 50000, 59000, 59001, 59002)
Write-Host "Scanning local ports..."
foreach ($port in $ports) {
    $tcp = New-Object System.Net.Sockets.TCPClient
    $tcp.ReceiveTimeout = 1000
    $tcp.SendTimeout = 1000
    try {
        $tcp.Connect('127.0.0.1', $port)
        if ($tcp.Connected) {
            Write-Host "Port $port is OPEN"
        } else {
            Write-Host "Port $port is closed"
        }
    } catch {
        Write-Host "Port $port is closed"
    }
    $tcp.Close()
}

Write-Host "`nScanning VM ports (192.168.233.129)..."
foreach ($port in $ports) {
    $tcp = New-Object System.Net.Sockets.TCPClient
    $tcp.ReceiveTimeout = 1000
    $tcp.SendTimeout = 1000
    try {
        $tcp.Connect('192.168.233.129', $port)
        if ($tcp.Connected) {
            Write-Host "Port $port is OPEN"
        } else {
            Write-Host "Port $port is closed"
        }
    } catch {
        Write-Host "Port $port is closed"
    }
    $tcp.Close()
}