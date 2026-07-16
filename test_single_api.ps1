$ProgressPreference = "SilentlyContinue"
$ErrorActionPreference = "Continue"

# Use the exact same format as batch_test3.ps1 which was working before
$api = "SSP-AUTH/queryMenuTreeBySysIdRoleIdWithGuest"
$parts = $api -split '/'
$service = $parts[1]

$body = @{
    Header = @{
        CurrentPageNum = 1
        PageTotalNum = 10
        NoRetCode = $true
        BranchId = "800000"
        LegalRepCode = "10000"
        TranTeller = ""
        TranCode = $api
        TranDate = "20260716"
        TranTime = "004500000"
        ServiceName = $service
        ServiceCode = "D20190130"
        AuthFlag = "0"
        AuthrTellerNo = "1"
        Channel = "39"
        ConsumerId = "1"
        GlobalSeq = "1"
        GlobalSeqNo = "1"
        KeyId = "1"
        LocalLang = "1"
        Mac = "1"
        SourceSysId = "1111"
        TerminalCode = "1121"
        TranSeq = "1"
        TranSeqNo = "1"
        TranTellerNo = "1"
        ExtendContent = "1"
        TotalNum = "0"
    }
} | ConvertTo-Json -Depth 5 -Compress

Write-Host "Body: $body"
Write-Host ""

$tempFile = [System.IO.Path]::GetTempFileName()
[System.IO.File]::WriteAllText($tempFile, $body)

Write-Host "Testing $api ..."
$resp = curl.exe -sk --noproxy "*" --max-time 15 -X POST "https://dl.brcloud.bankofchina.com/dlydjd/sgp/transferRequest" -H "Content-Type: application/json" -H "Authorization: 987654321" --data-binary "@$tempFile" 2>&1
Remove-Item $tempFile -Force

Write-Host "Response: $resp"
Write-Host ""
Write-Host "Response length: $($resp.Length)"
