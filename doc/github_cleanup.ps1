# GitHub cleanup for AbCS after fresh_public_repo.ps1
# Run in PowerShell:
#   powershell -ExecutionPolicy Bypass -File C:\projects\AbCS\doc\github_cleanup.ps1
#
# Removes stale remote branches and tags that still point at old history.
# Does NOT change repo visibility or collaborator access.

$ErrorActionPreference = "Stop"
$Abcs = "C:\projects\AbCS"

function Write-Step($msg) {
    Write-Host ""
    Write-Host "==== $msg ====" -ForegroundColor Cyan
}

function Require-GitOk($step) {
    if ($LASTEXITCODE -ne 0) {
        throw "Git failed during: $step"
    }
}

Set-Location $Abcs

Write-Step "Current GitHub refs (before cleanup)"
git ls-remote origin

Write-Step "Delete stale remote branches (old cursor work)"
$branches = @(
    "cursor/pyside6-6-11-upgrade-6705",
    "cursor/pyside6-a11y-code-changes-6705"
)
foreach ($b in $branches) {
    Write-Host "Deleting remote branch $b"
    git push origin --delete $b
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  (skipped or already gone)"
    }
}

Write-Step "Delete old remote tags (pre-fresh-start history)"
$tags = @("AudioBook", "ScreenReader")
foreach ($t in $tags) {
    Write-Host "Deleting remote tag $t"
    git push origin --delete $t
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  (skipped or already gone)"
    }
    git tag -d $t 2>$null | Out-Null
}

Write-Step "Prune stale remote-tracking refs locally"
git fetch --prune origin
Require-GitOk "fetch --prune"
git remote prune origin

Write-Step "GitHub refs after cleanup"
git ls-remote origin

Write-Step "DONE - AbCS remote cleanup"
Write-Host ""
Write-Host "Manual steps in GitHub web UI (if not done yet):"
Write-Host "  1. Settings -> Emails -> Keep my email addresses private"
Write-Host "  2. Settings -> Emails -> Block command line pushes that expose my email"
Write-Host "  3. Pull requests -> close any old open PRs from deleted cursor branches"
Write-Host "  4. Settings -> General -> verify repo visibility (private until launch, or public)"
Write-Host "  5. Settings -> Collaborators -> confirm Dominic still has read access"
Write-Host ""
Write-Host "pyside6 repo: already shows a single main commit on GitHub - no branch cleanup needed."
