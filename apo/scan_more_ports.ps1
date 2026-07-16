Write-Host "Scanning more local ports..."
$portRanges = @(
    @(1..1024),
    @(8000..8100),
    @(10000..10100),
    @(15000..15100),
    @(20000..20100),
    @(25000..25100),
    @(30000..30100),
    @(50000..50100)
)

foreach ($range in $portRanges) {
    foreach ($port in $range) {
        $tcp = New-Object System.Net.Sockets.TCPClient
        $tcp.ReceiveTimeout = 500
        $tcp.SendTimeout = 500
        try {
            $tcp.Connect('127.0.0.1', $port)
            if ($tcp.Connected) {
                Write-Host "OPEN: $port"
            }
        } catch {}
        $tcp.Close()
    }
}

Write-Host "`nDone!"