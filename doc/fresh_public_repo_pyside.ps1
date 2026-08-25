# Fresh public repo — pyside6-accessible-ui-reference (drops old commit history)
#
# Run AFTER AbCS fresh repo, or standalone for the reference repo only:
#   powershell -ExecutionPolicy Bypass -File C:\projects\AbCS\doc\fresh_public_repo_pyside.ps1

$ErrorActionPreference = "Stop"
$Repo     = "C:\projects\pyside6-accessible-ui-reference"
$NewName  = "Aurora Accessibility"
$NewEmail = "18517493+cfdrakeNS@users.noreply.github.com"
$Branch   = "main"

if (-not (Test-Path $Repo)) {
    throw "Repo not found: $Repo"
}

function Write-Step($msg) {
    Write-Host ""
    Write-Host "==== $msg ====" -ForegroundColor Cyan
}

Write-Step "Set git identity"
git config --global user.name $NewName
git config --global user.email $NewEmail
git -C $Repo config user.name $NewName
git -C $Repo config user.email $NewEmail

Set-Location $Repo

Write-Step "Create orphan branch"
git checkout --orphan $Branch
git add -A
git commit -m "Initial public release of PySide6 accessible UI reference."

Write-Step "Remove other local branches"
git branch --format='%(refname:short)' | Where-Object { $_ -ne $Branch } | ForEach-Object {
    git branch -D $_
}

Write-Step "Verify no hotmail"
$hits = git log --all --format='%ae%n%ce' | Select-String -Pattern 'hotmail' -SimpleMatch
if ($hits) { throw 'Hotmail still present.' }
Write-Host 'OK: clean history'

Write-Step "Force-push"
git push --force origin "${Branch}:${Branch}"

Write-Step "DONE - pyside6-accessible-ui-reference"
