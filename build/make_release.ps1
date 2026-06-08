param(
    [string]$Python = "E:\software\ADeepLearning\Anaconda\envs\ultralytics\python.exe"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Dist = Join-Path $Root "dist"
$Exe = Join-Path $Dist "YoloInstaller.exe"
$Sha = Join-Path $Dist "YoloInstaller.exe.sha256"

Set-Location $Root

if (Test-Path -LiteralPath $Dist) {
    Remove-Item -LiteralPath $Dist -Recurse -Force
}

& $Python -m PyInstaller (Join-Path $Root "build\build.spec") --noconfirm --clean

if (-not (Test-Path -LiteralPath $Exe)) {
    throw "Release build did not produce $Exe"
}

$Hash = (Get-FileHash -LiteralPath $Exe -Algorithm SHA256).Hash.ToLowerInvariant()
"$Hash  YoloInstaller.exe" | Set-Content -LiteralPath $Sha -Encoding ASCII

Write-Host "Release artifact: $Exe"
Write-Host "Checksum file: $Sha"

