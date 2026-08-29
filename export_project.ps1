$ProjectRoot = (Get-Location).Path

$OutputDir = Join-Path $ProjectRoot "_project_export"

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

$MasterFile = Join-Path $OutputDir "NEXUS-TWIN_FULL.txt"
$JsonlFile  = Join-Path $OutputDir "NEXUS-TWIN_DATABASE.jsonl"
$Manifest   = Join-Path $OutputDir "NEXUS-TWIN_MANIFEST.txt"

# ------------------------------------------------------------
# Directories that should NOT be included
# ------------------------------------------------------------

$ExcludedDirectories = @(
    ".git",
    ".vs",
    ".idea",
    ".vscode",
    ".pytest_cache",
    "__pycache__",
    "node_modules",
    "bin",
    "obj",
    "build",
    "Build",
    "Library",
    "Temp",
    "Logs",
    "UserSettings",
    "Packages",
    "graphify-out",
    "_project_export"
)

# ------------------------------------------------------------
# File extensions considered text/source files
# ------------------------------------------------------------

$TextExtensions = @(
    ".cs",
    ".csproj",
    ".sln",
    ".asmdef",
    ".asmref",

    ".py",
    ".pyw",

    ".ps1",
    ".psm1",
    ".psd1",

    ".js",
    ".jsx",
    ".ts",
    ".tsx",

    ".cpp",
    ".cc",
    ".cxx",
    ".c",
    ".h",
    ".hpp",

    ".shader",
    ".compute",
    ".cginc",
    ".hlsl",
    ".glsl",

    ".json",
    ".jsonl",
    ".yaml",
    ".yml",
    ".xml",
    ".toml",
    ".ini",
    ".cfg",
    ".conf",
    ".env",
    ".properties",

    ".md",
    ".markdown",
    ".txt",
    ".rst",

    ".html",
    ".htm",
    ".css",
    ".scss",

    ".bat",
    ".cmd",
    ".sh",

    ".sql",

    ".proto",
    ".graphql",

    ".gitignore",
    ".dockerignore",

    ".unity",
    ".prefab",
    ".asset",
    ".mat",
    ".controller",
    ".anim",
    ".overrideController",
    ".asmdef",

    ".csv"
)

# ------------------------------------------------------------
# Files to explicitly exclude
# ------------------------------------------------------------

$ExcludedFileNames = @(
    "NEXUS-TWIN_FULL.txt",
    "NEXUS-TWIN_DATABASE.jsonl",
    "NEXUS-TWIN_MANIFEST.txt"
)

# ------------------------------------------------------------
# Helper: determine whether path contains excluded directory
# ------------------------------------------------------------

function Test-ExcludedPath {
    param(
        [string]$FullPath
    )

    $relative = $FullPath.Substring($ProjectRoot.Length).TrimStart('\')

    $parts = $relative -split '[\\/]'

    foreach ($part in $parts) {
        if ($ExcludedDirectories -contains $part) {
            return $true
        }
    }

    return $false
}

# ------------------------------------------------------------
# Helper: safely read text
# ------------------------------------------------------------

function Read-TextFile {
    param(
        [string]$Path
    )

    try {
        return [System.IO.File]::ReadAllText(
            $Path,
            [System.Text.Encoding]::UTF8
        )
    }
    catch {
        try {
            return Get-Content -LiteralPath $Path -Raw -ErrorAction Stop
        }
        catch {
            return "[ERROR READING FILE: $($_.Exception.Message)]"
        }
    }
}

# ------------------------------------------------------------
# Find source/document/config files
# ------------------------------------------------------------

Write-Host ""
Write-Host "Scanning project..." -ForegroundColor Cyan
Write-Host "Root: $ProjectRoot"
Write-Host ""

$Files = Get-ChildItem `
    -LiteralPath $ProjectRoot `
    -File `
    -Recurse `
    -ErrorAction SilentlyContinue |
    Where-Object {

        $_.Name -notin $ExcludedFileNames -and
        -not (Test-ExcludedPath $_.FullName) -and
        (
            $TextExtensions -contains $_.Extension.ToLower() -or
            $_.Name -in @(
                "Dockerfile",
                "Makefile",
                "Jenkinsfile",
                "README",
                "README.md",
                ".gitignore",
                ".graphifyignore"
            )
        )
    } |
    Sort-Object FullName

Write-Host "Files selected: $($Files.Count)" -ForegroundColor Green

# ------------------------------------------------------------
# Initialize output files
# ------------------------------------------------------------

Set-Content `
    -LiteralPath $MasterFile `
    -Value "" `
    -Encoding UTF8

Set-Content `
    -LiteralPath $JsonlFile `
    -Value "" `
    -Encoding UTF8

Set-Content `
    -LiteralPath $Manifest `
    -Value "" `
    -Encoding UTF8

# ------------------------------------------------------------
# Project header
# ------------------------------------------------------------

$Header = @"
================================================================================
NEXUS-TWIN - COMPLETE SOURCE DATABASE
================================================================================

PROJECT ROOT:
$ProjectRoot

GENERATED:
$(Get-Date -Format "yyyy-MM-dd HH:mm:ss zzz")

TOTAL TEXT FILES:
$($Files.Count)

This file contains source code, configuration, documentation, scripts,
game-development assets represented as text, AI integration code,
simulation code, backend code, tests, and project metadata.

Binary files and generated/build/cache directories are intentionally excluded.

================================================================================

"@

Add-Content `
    -LiteralPath $MasterFile `
    -Value $Header `
    -Encoding UTF8

# ------------------------------------------------------------
# Process files
# ------------------------------------------------------------

$Index = 0

foreach ($File in $Files) {

    $Index++

    $RelativePath = $File.FullName.Substring(
        $ProjectRoot.Length
    ).TrimStart('\')

    $Extension = $File.Extension.ToLower()

    $Content = Read-TextFile -Path $File.FullName

    $Separator = "=" * 100

    # --------------------------------------------------------
    # MASTER TEXT DATABASE ENTRY
    # --------------------------------------------------------

    $Entry = @"

$Separator
FILE $Index / $($Files.Count)
$Separator

FILE NAME:
$($File.Name)

RELATIVE PATH:
$RelativePath

FULL PATH:
$($File.FullName)

EXTENSION:
$Extension

SIZE BYTES:
$($File.Length)

LAST MODIFIED:
$($File.LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss"))

--------------------------------------------------------------------------------
BEGIN FILE CONTENT
--------------------------------------------------------------------------------

$Content

--------------------------------------------------------------------------------
END FILE CONTENT
--------------------------------------------------------------------------------

"@

    Add-Content `
        -LiteralPath $MasterFile `
        -Value $Entry `
        -Encoding UTF8

    # --------------------------------------------------------
    # MANIFEST
    # --------------------------------------------------------

    $ManifestEntry = "{0}`t{1}`t{2}`t{3}" -f `
        $Index,
        $RelativePath,
        $File.Length,
        $Extension

    Add-Content `
        -LiteralPath $Manifest `
        -Value $ManifestEntry `
        -Encoding UTF8

    # --------------------------------------------------------
    # JSONL DATABASE ENTRY
    # --------------------------------------------------------

    $Record = [ordered]@{
        id            = $Index
        file_name     = $File.Name
        relative_path = $RelativePath
        extension     = $Extension
        size_bytes    = $File.Length
        last_modified = $File.LastWriteTime.ToString("o")
        content       = $Content
    }

    $Json = $Record | ConvertTo-Json -Depth 10 -Compress

    Add-Content `
        -LiteralPath $JsonlFile `
        -Value $Json `
        -Encoding UTF8

    Write-Progress `
        -Activity "Building NEXUS-TWIN project database" `
        -Status "$Index / $($Files.Count): $RelativePath" `
        -PercentComplete (($Index / $Files.Count) * 100)
}

# ------------------------------------------------------------
# Final statistics
# ------------------------------------------------------------

$TotalBytes = ($Files | Measure-Object -Property Length -Sum).Sum

$Summary = @"

================================================================================
EXPORT COMPLETE
================================================================================

Project:
$ProjectRoot

Files:
$($Files.Count)

Total source/document bytes:
$TotalBytes

Master text database:
$MasterFile

JSONL database:
$JsonlFile

Manifest:
$Manifest

================================================================================
"@

Add-Content `
    -LiteralPath $MasterFile `
    -Value $Summary `
    -Encoding UTF8

Add-Content `
    -LiteralPath $Manifest `
    -Value $Summary `
    -Encoding UTF8

Write-Progress `
    -Activity "Building NEXUS-TWIN project database" `
    -Completed

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "EXPORT COMPLETE" -ForegroundColor Green
Write-Host "============================================================"
Write-Host ""
Write-Host "Master:"
Write-Host "  $MasterFile"
Write-Host ""
Write-Host "JSONL:"
Write-Host "  $JsonlFile"
Write-Host ""
Write-Host "Manifest:"
Write-Host "  $Manifest"
Write-Host ""
Write-Host "Files: $($Files.Count)"
Write-Host "Bytes: $TotalBytes"
Write-Host ""
