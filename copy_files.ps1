$source = "E:\BaiduNetdiskDownload\1"
$dest = "E:\BaiduNetdiskDownload\3"

# 创建目标目录结构
$dirs = @(
    "scripts",
    "skills/api-sec",
    "skills/auth-sec", 
    "skills/hack",
    "skills/osint",
    "hack-skills",
    "apo",
    "config",
    "core",
    "data",
    "exports",
    "reports"
)

foreach ($dir in $dirs) {
    $path = Join-Path $dest $dir
    if (-not (Test-Path $path)) {
        New-Item -ItemType Directory -Path $path -Force | Out-Null
        Write-Host "Created: $path"
    }
}

# 复制scripts目录
Write-Host "`nCopying scripts..."
Copy-Item "$source\scripts\*" "$dest\scripts\" -Recurse -Force

# 复制skills目录
Write-Host "`nCopying skills..."
Copy-Item "$source\.trae\skills\api-sec\SKILL.md" "$dest\skills\api-sec\" -Force
Copy-Item "$source\.trae\skills\auth-sec\SKILL.md" "$dest\skills\auth-sec\" -Force
Copy-Item "$source\.trae\skills\hack\SKILL.md" "$dest\skills\hack\" -Force
Copy-Item "$source\.trae\skills\osint\SKILL.md" "$dest\skills\osint\" -Force

# 复制hack-skills目录
Write-Host "`nCopying hack-skills..."
Copy-Item "$source\hack-skills\*" "$dest\hack-skills\" -Recurse -Force

# 复制apo目录（只复制脚本文件）
Write-Host "`nCopying apo scripts..."
Get-ChildItem "$source\apo\" -Filter "*.py" | Copy-Item -Destination "$dest\apo\" -Force
Get-ChildItem "$source\apo\" -Filter "*.js" | Copy-Item -Destination "$dest\apo\" -Force
Get-ChildItem "$source\apo\" -Filter "*.ps1" | Copy-Item -Destination "$dest\apo\" -Force
Get-ChildItem "$source\apo\" -Filter "*.txt" | Copy-Item -Destination "$dest\apo\" -Force
Copy-Item "$source\apo\SECURITY_AUDIT_REPORT.md" "$dest\apo\" -Force

# 复制config目录
Write-Host "`nCopying config..."
Copy-Item "$source\config\*" "$dest\config\" -Recurse -Force

# 复制core目录
Write-Host "`nCopying core..."
Copy-Item "$source\core\*" "$dest\core\" -Recurse -Force

# 复制data目录
Write-Host "`nCopying data..."
Copy-Item "$source\data\*" "$dest\data\" -Recurse -Force

# 复制exports目录
Write-Host "`nCopying exports..."
Copy-Item "$source\exports\*" "$dest\exports\" -Recurse -Force

# 复制根目录下的安全脚本（排除二进制和大文件）
Write-Host "`nCopying root scripts..."
Get-ChildItem "$source\" -Filter "*.py" | Copy-Item -Destination "$dest\" -Force
Get-ChildItem "$source\" -Filter "*.js" | Copy-Item -Destination "$dest\" -Force
Get-ChildItem "$source\" -Filter "*.ps1" | Copy-Item -Destination "$dest\" -Force
Get-ChildItem "$source\" -Filter "*.md" | Copy-Item -Destination "$dest\" -Force
Get-ChildItem "$source\" -Filter "*.json" | Copy-Item -Destination "$dest\" -Force
Get-ChildItem "$source\" -Filter "*.txt" | Copy-Item -Destination "$dest\" -Force
Get-ChildItem "$source\" -Filter "*.html" | Copy-Item -Destination "$dest\" -Force

# 复制报告文件
Write-Host "`nCopying reports..."
Copy-Item "$source\安全验证报告_青岛市人民检察院.md" "$dest\reports\" -Force
Copy-Item "$source\sdqb_availability_report.*" "$dest\reports\" -Force
Copy-Item "$source\minio告警分析报告.html" "$dest\reports\" -Force

Write-Host "`n=== Copy completed ==="
Get-ChildItem $dest -Recurse | Measure-Object | Select-Object -ExpandProperty Count