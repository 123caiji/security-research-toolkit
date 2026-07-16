$apis = @(
    "SSP-AUTH/queryMenuTreeBySysIdRoleId",
    "SSP-AUTH/queryMenuTreeBySysIdRoleIdWithGuest",
    "SSP-AUTH/queryActionPermissionByMenuIdRoleId",
    "SSP-AUTH/authentication",
    "SSP-AUTH/queryVerificationCode",
    "SSP-AUTH/getNoPwdByPhoneNo",
    "AGRE-AGRE/queryAgreementTemplateList",
    "AGRE-AGRE/queryAgreementTypeList",
    "AGRE-AGRE/getAgreementInfo",
    "AGRE-AGRE/queryAgreementListByProductId",
    "CUST-INFO/myCustDimQryList",
    "CUST-INFO/selectPersonCust",
    "CUST-INFO/queryIdentificationCardInfo",
    "CUST-INFO/getGeoData",
    "EC-IDEN/queryOrderArray",
    "EC-IDEN/queryStatusOptions",
    "EC-IDEN/getFaceParam",
    "EC-FILE-MGR/onlinePreview",
    "EC-FILE-MGR/createNewAgreementFile",
    "CHANNEL/getPlatformBaseInfoList",
    "CHANNEL/getShareInstDetail",
    "CHANNEL/queryQrCodeTellerInfo",
    "CHANNEL/queryShareInstInfoByApplId",
    "CUST-CSER/myCustDimQryList",
    "CUST-CSER/acCreateCommunicationEventResult",
    "CUST-RELA/selectPartyRelationshipBasicInfo",
    "PROD-SOPE/queryInsideProductInfo",
    "PROD-SOPE/catalogManageQueryList",
    "PROD-SOPE/productDetail",
    "SOP-SERV/getSurveyResponseAnswer",
    "SOP-STYY/getSurveyResponseAnswer",
    "TRAD-OPRO/queryLoanApplyData",
    "TRAD-RQUO/queryMenuData",
    "REP-SERV/queryRepaymentAppointment",
    "HOUSE-CREDIT/queryHouseCreditInfo"
)

$results = @()
foreach($api in $apis){
    $parts = $api -split '/'
    $module = $parts[0]
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
    
    $resp = curl.exe -sk --noproxy "*" --max-time 10 -X POST "https://dl.brcloud.bankofchina.com/dlydjd/sgp/transferRequest" -H "Content-Type: application/json" -H "Authorization: 987654321" --data-binary "@$tempFile" -w "|%{http_code}|%{size_download}" 2>&1
    Remove-Item $tempFile -Force
    
    $results += "$api => $resp"
    Write-Output "$api => $resp"
}

$results | Out-File e:\BaiduNetdiskDownload\1\api_results.txt