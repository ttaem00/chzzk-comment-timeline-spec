#requires -Version 7.0
param([string]$Root, [int]$MaxTotalSeconds = 600, [int]$ChildTimeoutSeconds = 90, [int]$MainSyncTrackingIssue, [switch]$RemoteMergeRefValidation, [string]$RemoteMergeRefExpectedHead, [string]$RemoteMergeRefBaselineRoot, [string]$RemoteMergeRefBaselineHead)
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path $PSScriptRoot -Parent
if ($Root) { $repoRoot = (Resolve-Path -LiteralPath $Root).Path }; Push-Location $repoRoot
try {
    & node scripts/validate.cjs
    if ($LASTEXITCODE -ne 0) { throw 'Documentation checks failed' }
    & git diff --check
    if ($LASTEXITCODE -ne 0) { throw 'Diff whitespace check failed' }
    Write-Output 'RESULT: PASS'
} finally { Pop-Location }
