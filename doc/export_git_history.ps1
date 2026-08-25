# Export AbCS git history to CSV (run before fresh-public-repo if desired)
# Usage: powershell -ExecutionPolicy Bypass -File C:\projects\AbCS\doc\export_git_history.ps1
#
# Output (in doc/):
#   git_history_full.csv      — all commits (Date column = full timestamp with timezone)
#   git_history_major.csv     — substantive features/releases (stricter filter)
#   git_history_bugfixes.csv  — user-facing fixes (stricter filter; excludes git/tooling churn)

$ErrorActionPreference = "Stop"
$OutDir = Join-Path (Split-Path $PSScriptRoot -Parent) "doc"
$FullCsv = Join-Path $OutDir "git_history_full.csv"
$MajorCsv = Join-Path $OutDir "git_history_major.csv"
$BugCsv = Join-Path $OutDir "git_history_bugfixes.csv"

function Get-Category([string]$subject) {
    $s = $subject.ToLowerInvariant()

    # Agent / repo / launch meta work — not user-facing AbCS changes
    if ($s -match 'privacy script|git privacy|filter-branch|fresh.public|export git history|launch plan|launch_open|aurora_about|finish_git|rewrite_identity|co-authored-by: cursor|/\bcursor/|pyside6-6-11-upgrade|pyside6-a11y-code') {
        return "minor"
    }
    if ($s -match '^(run git|add fresh|add public launch|expand launch|export git|fix privacy|fix git|fix script|fix launch|fix csv|fix export|fix filter|fix branch|fix powershell|change build|doc:|readme only|typo|format|lint|chore|wip|test:|pytest|merge branch)') {
        return "minor"
    }

    # User-facing bug fixes
    if ($s -match '\b(bugfix|regression|hotfix|crash|null pointer)\b') {
        return "bugfix"
    }
    if ($s -match '^fix ') {
        if ($s -match 'fix (privacy|git|script|launch|csv|export|plan|filter|branch|powershell|windows branch|repo)') {
            return "minor"
        }
        return "bugfix"
    }
    if ($s -match '\b(broken|ui polish|harden|resolve(d)?|correct(s|ed)?)\b') {
        return "bugfix"
    }

    # Substantive features / releases
    if ($s -match 'version to v|updated version|bump version| v2\.|release v|private hp legacy|linux build|windows installer|\.iss|help doc|help_docs|new window|new dialog|implement |introduced |overhaul|redesign|database|migration|want to read|book ratings|cover image|statistics|import detail|collection manager|accessibility|a11y|screen reader|keyboard nav') {
        return "major"
    }
    if ($s -match '^add ' -and $s -notmatch '^add (fresh|public launch|export git|fix )') {
        return "major"
    }
    if ($s -match '^(complete|merge) ') {
        return "major"
    }

    return "other"
}

function Escape-Csv([string]$value) {
    if ($null -eq $value) { return '""' }
    $v = $value -replace '"', '""'
    return '"' + $v + '"'
}

$branch = git branch --show-current
if (-not $branch) { $branch = "main" }
Write-Host "Reading git log from branch: $branch"
$raw = git log $branch --format="%H|%h|%ai|%an|%ae|%s"
$rows = New-Object System.Collections.Generic.List[object]

foreach ($line in $raw) {
    if (-not $line) { continue }
    $parts = $line -split '\|', 6
    if ($parts.Count -lt 6) { continue }
    $subject = $parts[5]
    $dateRaw = $parts[2]
    $rows.Add([pscustomobject]@{
        Date       = $dateRaw
        DateOnly   = ($dateRaw -replace ' .*', '')
        ShortHash  = $parts[1]
        FullHash   = $parts[0]
        Author     = $parts[3]
        Email      = $parts[4]
        Category   = (Get-Category $subject)
        Subject    = $subject
    })
}

Write-Host "Commits on ${branch}: $($rows.Count)"

function Write-CsvFile($path, $items) {
    $header = "Date,DateOnly,ShortHash,FullHash,Author,Email,Category,Subject"
    $lines = @($header)
    foreach ($r in $items) {
        $lines += (
            (Escape-Csv $r.Date) + "," +
            (Escape-Csv $r.DateOnly) + "," +
            (Escape-Csv $r.ShortHash) + "," +
            (Escape-Csv $r.FullHash) + "," +
            (Escape-Csv $r.Author) + "," +
            (Escape-Csv $r.Email) + "," +
            (Escape-Csv $r.Category) + "," +
            (Escape-Csv $r.Subject)
        )
    }
    [System.IO.File]::WriteAllLines($path, $lines)
    Write-Host "Wrote $($items.Count) rows -> $path"
}

$sorted = $rows | Sort-Object { [datetime]$_.Date } -Descending
Write-CsvFile $FullCsv $sorted
Write-CsvFile $MajorCsv ($sorted | Where-Object { $_.Category -eq "major" })
Write-CsvFile $BugCsv ($sorted | Where-Object { $_.Category -eq "bugfix" })

Write-Host ""
Write-Host "Summary by category ($branch):"
$sorted | Group-Object Category | Sort-Object Name | ForEach-Object { Write-Host "  $($_.Name): $($_.Count)" }
