# Finish Launch Prep: Git History Privacy Fix (rewrite all commits)
# Run in Windows PowerShell (NOT via Cursor Run button):
#   powershell -ExecutionPolicy Bypass -File C:\projects\AbCS\doc\finish_git_privacy_fix.ps1
#
# If this keeps failing, use fresh_public_repo.ps1 instead (simpler, drops old history).

$ErrorActionPreference = "Stop"
$NewName  = "Aurora Accessibility"
$NewEmail = "18517493+cfdrakeNS@users.noreply.github.com"
$OldEmail = "cfrancisdrake@hotmail.com"
$Abcs     = "C:\projects\AbCS"
$Pyside   = "C:\projects\pyside6-accessible-ui-reference"

function Write-Step($msg) {
    Write-Host ""
    Write-Host "==== $msg ====" -ForegroundColor Cyan
}

function Get-GitSh {
    $candidates = @(
        (Join-Path $env:ProgramFiles "Git\bin\sh.exe"),
        (Join-Path ${env:ProgramFiles(x86)} "Git\bin\sh.exe")
    )
    foreach ($c in $candidates) {
        if (Test-Path $c) { return $c }
    }
    throw "Git sh.exe not found. Install Git for Windows, or use doc/fresh_public_repo.ps1 instead."
}

function Remove-RefsOriginal {
    $refs = git for-each-ref --format="%(refname)" refs/original
    if (-not $refs) {
        Write-Host "No refs/original backups found."
        return
    }
    foreach ($ref in $refs) {
        if ($ref) {
            Write-Host "Deleting $ref"
            git update-ref -d $ref
        }
    }
}

function Assert-NoHotmail($repo) {
    Push-Location $repo
    try {
        $hits = git log --all --format="%ae`n%ce" 2>$null | Select-String -Pattern "hotmail" -SimpleMatch
        if ($hits) {
            throw "Hotmail still present in $repo ($($hits.Count) line hits). Aborting."
        }
        Write-Host "OK: no hotmail in $repo"
        git log --all --format="%an <%ae>" | Sort-Object -Unique | Select-Object -First 10
    } finally {
        Pop-Location
    }
}

function Finish-Repo($repo) {
    Push-Location $repo
    try {
        Write-Host "Running filter-branch (may take several minutes)..."
        $env:FILTER_BRANCH_SQUELCH_WARNING = "1"
        $filterFile = Join-Path $repo "_rewrite_identity.sh"
        @"
#!/bin/sh
OLD_EMAIL="$OldEmail"
NEW_NAME="$NewName"
NEW_EMAIL="$NewEmail"
if [ "`$GIT_AUTHOR_EMAIL" = "`$OLD_EMAIL" ]; then
    export GIT_AUTHOR_NAME="`$NEW_NAME"
    export GIT_AUTHOR_EMAIL="`$NEW_EMAIL"
fi
if [ "`$GIT_COMMITTER_EMAIL" = "`$OLD_EMAIL" ]; then
    export GIT_COMMITTER_NAME="`$NEW_NAME"
    export GIT_COMMITTER_EMAIL="`$NEW_EMAIL"
fi
"@ | Set-Content -Path $filterFile -Encoding ascii -NoNewline
        Add-Content -Path $filterFile -Value "`n" -Encoding ascii

        $sh = Get-GitSh
        $repoPosix = ($repo -replace '\\', '/')
        & $sh -lc "cd '$repoPosix' && git filter-branch -f --env-filter '$(cat _rewrite_identity.sh)' --tag-name-filter cat -- --branches --tags"

        if (Test-Path $filterFile) { Remove-Item $filterFile -Force }
        Remove-RefsOriginal
        git reflog expire --expire=now --all
        git gc --prune=now
        Assert-NoHotmail $repo
        Write-Host "Force-pushing all branches and tags..."
        git push --force --all origin
        git push --force --tags origin
        Write-Host "Force-push done for $repo"
    } finally {
        Pop-Location
    }
}

Write-Step "Update git config (global + both repos)"
git config --global user.name $NewName
git config --global user.email $NewEmail
git -C $Abcs config user.name $NewName
git -C $Abcs config user.email $NewEmail
if (Test-Path $Pyside) {
    git -C $Pyside config user.name $NewName
    git -C $Pyside config user.email $NewEmail
}
Write-Host "Global: $(git config --global user.name) <$(git config --global user.email)>"

Write-Step "AbCS: rewrite history, cleanup, force-push"
Finish-Repo $Abcs

Write-Step "pyside6: rewrite history, cleanup, force-push"
if (Test-Path $Pyside) {
    Finish-Repo $Pyside
} else {
    Write-Host "Skip: $Pyside not found"
}

Write-Step "DONE"
Write-Host "Backups (if needed): C:\projects\_git_backups\"
