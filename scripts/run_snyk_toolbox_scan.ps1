# Scan high-value Python tool manifests in this security toolbox.
# Prerequisite: npx snyk auth  (one-time OAuth in browser)
# Output: data/reports/snyk_toolbox_scan_<timestamp>.json

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$ReportDir = Join-Path $Root "data\reports"
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$OutFile = Join-Path $ReportDir "snyk_toolbox_scan_$Stamp.json"

$Targets = @(
    "tools\gui_scan\dirsearch\requirements.txt",
    "tools\gui_other\hengxiang\impacket-0.11.0\requirements.txt",
    "tools\gui_shouji\oneforall\requirements.txt",
    "tools\gui_scan\webpackscan\requirements.txt",
    "tools\gui_other\vcenterKit\requirements.txt"
)

if (-not (Test-Path $ReportDir)) { New-Item -ItemType Directory -Path $ReportDir | Out-Null }

$results = @()
foreach ($rel in $Targets) {
    $manifest = Join-Path $Root $rel
    if (-not (Test-Path $manifest)) {
        $results += [ordered]@{ target = $rel; ok = $false; error = "manifest not found" }
        continue
    }
    $dir = Split-Path -Parent $manifest
    $file = Split-Path -Leaf $manifest
    Push-Location $dir
    try {
        $json = npx snyk test --file=$file --package-manager=pip --json 2>&1 | Out-String
        $parsed = $json | ConvertFrom-Json
        $results += [ordered]@{
            target = $rel
            ok = $parsed.ok
            vulnerabilityCount = @($parsed.vulnerabilities).Count
            summary = $parsed.summary
            error = $parsed.error
        }
    } catch {
        $results += [ordered]@{ target = $rel; ok = $false; error = $_.Exception.Message }
    } finally {
        Pop-Location
    }
}

$payload = [ordered]@{
    _simulation = $false
    _source = "snyk_cli_toolbox_scan"
    scanned_at = (Get-Date).ToString("o")
    results = $results
}
$payload | ConvertTo-Json -Depth 8 | Set-Content -Encoding utf8 $OutFile
Write-Host "Wrote $OutFile"
