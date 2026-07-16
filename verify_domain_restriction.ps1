# Domain access restriction vulnerability verification script
[System.Net.ServicePointManager]::ServerCertificateValidationCallback = {$true}
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12 -bor [System.Net.SecurityProtocolType]::Tls11 -bor [System.Net.SecurityProtocolType]::Tls

function Get-DetailedResponse {
    param($url, $hostHeader = $null)
    
    try {
        $request = [System.Net.HttpWebRequest]::Create($url)
        $request.Timeout = 15000
        $request.AllowAutoRedirect = $false
        if ($hostHeader) {
            $request.Host = $hostHeader
        }
        
        $response = $request.GetResponse()
        $statusCode = [int]$response.StatusCode
        $statusDesc = $response.StatusDescription
        $server = $response.Server
        
        $headers = @{}
        foreach ($key in $response.Headers.AllKeys) {
            $headers[$key] = $response.Headers[$key]
        }
        
        $stream = $response.GetResponseStream()
        $reader = New-Object System.IO.StreamReader($stream)
        $content = $reader.ReadToEnd()
        $response.Close()
        
        return [PSCustomObject]@{
            Success = $true
            StatusCode = $statusCode
            StatusDescription = $statusDesc
            Server = $server
            Headers = $headers
            Content = $content
            ContentLength = $content.Length
        }
    } catch {
        $statusCode = $null
        $headers = @{}
        $content = $null
        $server = $null
        
        if ($_.Exception.Response) {
            $resp = $_.Exception.Response
            $statusCode = [int]$resp.StatusCode
            $statusDesc = $resp.StatusDescription
            $server = $resp.Server
            foreach ($key in $resp.Headers.AllKeys) {
                $headers[$key] = $resp.Headers[$key]
            }
            
            try {
                $stream = $resp.GetResponseStream()
                $reader = New-Object System.IO.StreamReader($stream)
                $content = $reader.ReadToEnd()
            } catch {}
        }
        
        return [PSCustomObject]@{
            Success = $false
            StatusCode = $statusCode
            StatusDescription = $statusDesc
            Server = $server
            Headers = $headers
            Content = $content
            ContentLength = if ($content) { $content.Length } else { 0 }
            ErrorMessage = $_.Exception.Message
        }
    }
}

Write-Host "====== Test 1: HTTP IP access (http://219.152.85.68/) ======"
$r1 = Get-DetailedResponse "http://219.152.85.68/"
Write-Host "Status: $($r1.StatusCode) $($r1.StatusDescription)"
Write-Host "Server: $($r1.Server)"
Write-Host "Content-Length: $($r1.ContentLength)"
Write-Host "Headers:"
$r1.Headers.GetEnumerator() | ForEach-Object { Write-Host "  $($_.Key): $($_.Value)" }
Write-Host "Content (first 500 chars):"
if ($r1.Content) { Write-Host $r1.Content.Substring(0, [Math]::Min(500, $r1.ContentLength)) }

Write-Host ""
Write-Host "====== Test 2: HTTP IP + Host=service.cqsqxj.com ======"
$r2 = Get-DetailedResponse "http://219.152.85.68/" -hostHeader "service.cqsqxj.com"
Write-Host "Status: $($r2.StatusCode) $($r2.StatusDescription)"
Write-Host "Server: $($r2.Server)"
Write-Host "Content-Length: $($r2.ContentLength)"
Write-Host "Headers:"
$r2.Headers.GetEnumerator() | ForEach-Object { Write-Host "  $($_.Key): $($_.Value)" }
Write-Host "Content (first 500 chars):"
if ($r2.Content) { Write-Host $r2.Content.Substring(0, [Math]::Min(500, $r2.ContentLength)) }

Write-Host ""
Write-Host "====== Test 3: HTTP IP + Host=evil.com (Host header injection) ======"
$r3 = Get-DetailedResponse "http://219.152.85.68/" -hostHeader "evil.com"
Write-Host "Status: $($r3.StatusCode) $($r3.StatusDescription)"
Write-Host "Server: $($r3.Server)"
Write-Host "Content-Length: $($r3.ContentLength)"
Write-Host "Headers:"
$r3.Headers.GetEnumerator() | ForEach-Object { Write-Host "  $($_.Key): $($_.Value)" }
Write-Host "Content (first 500 chars):"
if ($r3.Content) { Write-Host $r3.Content.Substring(0, [Math]::Min(500, $r3.ContentLength)) }

Write-Host ""
Write-Host "====== Test 4: HTTP domain access (http://service.cqsqxj.com/) ======"
$r4 = Get-DetailedResponse "http://service.cqsqxj.com/"
Write-Host "Status: $($r4.StatusCode) $($r4.StatusDescription)"
Write-Host "Server: $($r4.Server)"
Write-Host "Content-Length: $($r4.ContentLength)"
Write-Host "Headers:"
$r4.Headers.GetEnumerator() | ForEach-Object { Write-Host "  $($_.Key): $($_.Value)" }
Write-Host "Content (first 500 chars):"
if ($r4.Content) { Write-Host $r4.Content.Substring(0, [Math]::Min(500, $r4.ContentLength)) }

Write-Host ""
Write-Host "====== Summary ======"
Write-Host "IP access (no Host):    $($r1.StatusCode) - Content-Length: $($r1.ContentLength)"
Write-Host "IP access (Host=domain): $($r2.StatusCode) - Content-Length: $($r2.ContentLength)"
Write-Host "IP access (Host=evil): $($r3.StatusCode) - Content-Length: $($r3.ContentLength)"
Write-Host "Domain access (HTTP):  $($r4.StatusCode) - Content-Length: $($r4.ContentLength)"

$sameContent = ($r1.ContentLength -eq $r2.ContentLength -and $r2.ContentLength -eq $r3.ContentLength -and $r3.ContentLength -eq $r4.ContentLength)
Write-Host ""
Write-Host "All responses have same content length: $sameContent"
if ($sameContent) {
    Write-Host "=> [VULNERABILITY EXISTS] Server does not restrict domain access. IP access and arbitrary Host headers both reach the same content."
} else {
    Write-Host "=> Responses differ. Further analysis needed."
}
