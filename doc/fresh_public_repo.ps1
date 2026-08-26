# Fresh public repo — AbCS (drops old commit history, one clean commit)
#
# Run in PowerShell OUTSIDE Cursor:
#   powershell -ExecutionPolicy Bypass -File C:\projects\AbCS\doc\fresh_public_repo.ps1

$ErrorActionPreference = "Stop"
$Abcs       = "C:\projects\AbCS"
$NewName    = "Aurora Accessibility"
$NewEmail   = "18517493+cfdrakeNS@users.noreply.github.com"
$Branch     = "main"
$TempBranch = "aurora-public-fresh"

function Write-Step($msg) {
    Write-Host ""
    Write-Host "==== $msg ====" -ForegroundColor Cyan
}

function Require-GitOk($step) {
    if ($LASTEXITCODE -ne 0) {
        throw "Git failed during: $step"
    }
}

Write-Step "Set git identity for new commits"
git config --global user.name "$NewName"
Require-GitOk "global user.name"
git config --global user.email "$NewEmail"
Require-GitOk "global user.email"
git -C "$Abcs" config user.name "$NewName"
Require-GitOk "local user.name"
git -C "$Abcs" config user.email "$NewEmail"
Require-GitOk "local user.email"

Set-Location $Abcs

Write-Step "Remove temp files that must not ship"
Remove-Item (Join-Path $Abcs "_rewrite_identity.sh") -Force -ErrorAction SilentlyContinue
Remove-Item (Join-Path $Abcs "doc/Update launch_plan.md") -Force -ErrorAction SilentlyContinue

Write-Step "Create orphan branch (temporary name avoids main already exists error)"
$current = git branch --show-current
if ($current -ne $TempBranch) {
    git checkout --orphan $TempBranch
    Require-GitOk "checkout --orphan"
} else {
    Write-Host "Already on $TempBranch - continuing."
}

Write-Step "Clear index and stage all project files"
git rm -rf --cached . 2>$null | Out-Null
git add -A
Require-GitOk "git add"

$status = git status --porcelain
if (-not $status) {
    throw "Nothing to commit - working tree empty."
}

git commit -m "Initial public release of AbCS (Audiobook Collector Scanner)."
Require-GitOk "git commit"
git log -1 --format='Author: %an <%ae>'

Write-Step "Delete all old local branches"
$toDelete = git branch --format='%(refname:short)' | Where-Object { $_ -ne $TempBranch }
foreach ($b in $toDelete) {
    Write-Host "Deleting local branch $b"
    git branch -D $b
    Require-GitOk "delete branch $b"
}

Write-Step "Rename orphan branch to main"
git branch -m $Branch
Require-GitOk "rename branch to main"

Write-Step "Purge unreachable old history"
git reflog expire --expire=now --all
git gc --prune=now --aggressive

Write-Step "Verify no hotmail in new history"
$hits = git log --format='%ae%n%ce' | Select-String -Pattern 'hotmail' -SimpleMatch
if ($hits) {
    $count = @($hits).Count
    throw "Hotmail still found after fresh start ($count matches). Stop and investigate."
}
$commitCount = git rev-list --count HEAD
Write-Host "OK: clean history - $commitCount commit(s)"

Write-Step "Force-push to GitHub (replaces remote main history)"
git push --force origin "${Branch}:${Branch}"
Require-GitOk "git push"

Write-Step "DONE - AbCS"
Write-Host ""
Write-Host 'Local backup of old history: C:\projects\_git_backups\AbCS.git'
Write-Host 'On GitHub: delete old remote branches named cursor/... if they remain.'
Write-Host 'Enable GitHub email privacy: Settings, Emails, Keep my email addresses private'
