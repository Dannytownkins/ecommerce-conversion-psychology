[CmdletBinding()]
param(
    [string]$SourceRoot = "",
    [string]$TargetRoot = (Join-Path $env:USERPROFILE ".codex\\skills\\ecommerce-conversion-psychology")
)

$ErrorActionPreference = "Stop"

function Invoke-RobocopyMirror {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Source,
        [Parameter(Mandatory = $true)]
        [string]$Target
    )

    if (-not (Test-Path $Source -PathType Container)) {
        throw "Missing source directory: $Source"
    }

    New-Item -ItemType Directory -Force -Path $Target | Out-Null

    $robocopyArgs = @(
        $Source,
        $Target,
        "/MIR",
        "/FFT",
        "/R:2",
        "/W:1",
        "/NFL",
        "/NDL",
        "/NJH",
        "/NJS",
        "/NP",
        "/XD",
        "__pycache__",
        ".git"
    )

    & robocopy @robocopyArgs | Out-Null
    if ($LASTEXITCODE -ge 8) {
        throw "robocopy failed for '$Source' -> '$Target' with exit code $LASTEXITCODE"
    }
}

if ([string]::IsNullOrWhiteSpace($SourceRoot)) {
    $SourceRoot = Split-Path -Parent $PSScriptRoot
}

$SourceRoot = (Resolve-Path $SourceRoot).Path
$TargetRoot = [System.IO.Path]::GetFullPath($TargetRoot)

$managedDirectories = @(
    "agents",
    "citations",
    "platforms",
    "references",
    "scripts",
    "skills",
    "templates",
    "workflows"
)

$managedFiles = @(
    ".gitattributes",
    ".gitignore",
    "CHANGELOG.md",
    "CODEX_CONVERSION.md",
    "LICENSE",
    "README.md",
    "SKILL.md"
)

Write-Host "Syncing Codex skill install..." -ForegroundColor Cyan
Write-Host "  Source: $SourceRoot"
Write-Host "  Target: $TargetRoot"

New-Item -ItemType Directory -Force -Path $TargetRoot | Out-Null

foreach ($directory in $managedDirectories) {
    $sourcePath = Join-Path $SourceRoot $directory
    $targetPath = Join-Path $TargetRoot $directory
    Invoke-RobocopyMirror -Source $sourcePath -Target $targetPath
}

foreach ($file in $managedFiles) {
    $sourcePath = Join-Path $SourceRoot $file
    if (-not (Test-Path $sourcePath -PathType Leaf)) {
        throw "Missing source file: $sourcePath"
    }

    $targetPath = Join-Path $TargetRoot $file
    Copy-Item -Path $sourcePath -Destination $targetPath -Force
}

Write-Host "Codex install updated successfully." -ForegroundColor Green
