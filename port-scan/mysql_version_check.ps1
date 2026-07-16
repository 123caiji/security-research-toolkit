$ip = "58.220.24.217"
$port = 26603

try {
    $tcp = New-Object System.Net.Sockets.TcpClient
    $tcp.ReceiveTimeout = 5000
    $tcp.SendTimeout = 5000
    $tcp.Connect($ip, $port)
    
    $stream = $tcp.GetStream()
    $buffer = New-Object byte[] 4096
    $bytesRead = $stream.Read($buffer, 0, $buffer.Length)
    
    Write-Host "Bytes received: $bytesRead"
    
    if ($bytesRead -gt 4) {
        $packetLen = $buffer[0] -bor ($buffer[1] -shl 8) -bor ($buffer[2] -shl 16)
        $packetNum = $buffer[3]
        Write-Host "Packet length: $packetLen"
        Write-Host "Packet number: $packetNum"
        
        $payloadOffset = 4
        $protocolVersion = $buffer[$payloadOffset]
        Write-Host "Protocol version: $protocolVersion"
        
        $versionEnd = $payloadOffset + 1
        while ($versionEnd -lt $bytesRead -and $buffer[$versionEnd] -ne 0) {
            $versionEnd++
        }
        $versionBytes = $buffer[($payloadOffset + 1)..($versionEnd - 1)]
        $version = [System.Text.Encoding]::ASCII.GetString($versionBytes)
        Write-Host "MySQL Version: $version"
        
        $threadIdOffset = $versionEnd + 1
        if ($threadIdOffset + 4 -le $bytesRead) {
            $threadId = [BitConverter]::ToUInt32($buffer, $threadIdOffset)
            Write-Host "Thread ID: $threadId"
        }
    }
    
    $tcp.Close()
} catch {
    Write-Host "Error: $($_.Exception.Message)"
}
