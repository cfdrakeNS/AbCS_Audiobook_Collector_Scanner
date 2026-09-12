# Publish AbCS: flip repo public + GitHub Release with Windows/Linux zip installers.
# Run in PowerShell (outside Cursor if gh auth is needed):
#   powershell -ExecutionPolicy Bypass -File C:\projects\AbCS\scripts\publish_github_release.ps1
#
# Auth (pick one):
#   A) GitHub CLI:  winget install GitHub.cli  then  gh auth login
#   B) Fine-grained PAT with Contents + Administration on this repo:
#      $env:GITHUB_TOKEN = "github_pat_..."
#
# Does NOT remove collaborators. Confirm Dominic still has access after going public.

$ErrorActionPreference = "Stop"
$Abcs = "C:\projects\AbCS"
$Owner = "cfdrakeNS"
$Repo = "AbCS_Audiobook_Collector_Scanner"
$Version = "2.12"
$Tag = "v$Version"
$ReleaseName = "AbCS v$Version"
$WinZip = "AbCS-Setup-v$Version.zip"
$LinuxZip = "abcs_linux_v$Version.zip"  # Linux build always lowercase
$LinuxZipLegacy = "AbCS_Linux_v$Version.zip"  # rejected; do not upload this name

function Write-Step($msg) {
    Write-Host ""
    Write-Host "==== $msg ====" -ForegroundColor Cyan
}

function Invoke-Git {
    param([string[]]$GitArgs)
    $prev = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        & git @GitArgs 2>&1 | Out-Null
    }
    finally {
        $ErrorActionPreference = $prev
    }
    if ($LASTEXITCODE -ne 0) {
        throw "git failed: git $($GitArgs -join ' ')"
    }
}

function Get-GhExe {
    $cmd = Get-Command gh -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    $paths = @(
        "${env:ProgramFiles}\GitHub CLI\gh.exe",
        "${env:LocalAppData}\Programs\GitHub CLI\gh.exe"
    )
    foreach ($p in $paths) {
        if (Test-Path $p) { return $p }
    }
    return $null
}

function Get-GitHubHeaders {
    if ($env:GITHUB_TOKEN) {
        return @{
            Authorization = "Bearer $env:GITHUB_TOKEN"
            Accept        = "application/vnd.github+json"
            "X-GitHub-Api-Version" = "2022-11-28"
        }
    }
    throw "Set GITHUB_TOKEN or install and log in with gh (gh auth login)."
}

function Invoke-Gh {
    param([string[]]$GhArgs)
    $gh = Get-GhExe
    if (-not $gh) { throw "gh not found. Install GitHub CLI or set GITHUB_TOKEN." }
    & $gh @GhArgs
    if ($LASTEXITCODE -ne 0) { throw "gh failed: gh $($GhArgs -join ' ')" }
}

function Set-RepoPublic {
    param($Headers)
    $uri = "https://api.github.com/repos/$Owner/$Repo"
    $body = '{"private":false}' | ConvertFrom-Json | ConvertTo-Json -Compress
    Invoke-RestMethod -Uri $uri -Method PATCH -Headers $Headers -Body $body -ContentType "application/json" | Out-Null
    Write-Host "Repo is now public: https://github.com/$Owner/$Repo"
}

function Get-OrCreateRelease {
    param($Headers, [string]$Notes)
    $uri = "https://api.github.com/repos/$Owner/$Repo/releases/tags/$Tag"
    try {
        return Invoke-RestMethod -Uri $uri -Headers $Headers
    }
    catch {
        if ($_.Exception.Response.StatusCode.value__ -ne 404) { throw }
    }
    $createUri = "https://api.github.com/repos/$Owner/$Repo/releases"
    $payload = @{
        tag_name   = $Tag
        name       = $ReleaseName
        body       = $Notes
        draft      = $false
        prerelease = $false
    } | ConvertTo-Json
    return Invoke-RestMethod -Uri $createUri -Method POST -Headers $Headers -Body $payload -ContentType "application/json"
}

function Upload-ReleaseAsset {
    param($Headers, $Release, [string]$FilePath)
    $name = [System.IO.Path]::GetFileName($FilePath)
    $uploadBase = $Release.upload_url -replace '\{.*$', ""
    $uploadUri = "${uploadBase}?name=$name"
    $uploadHeaders = @{
        Authorization = $Headers.Authorization
        Accept        = "application/vnd.github+json"
        "X-GitHub-Api-Version" = "2022-11-28"
    }
    Write-Host "Uploading $name ..."
    Invoke-RestMethod -Uri $uploadUri -Method POST -Headers $uploadHeaders `
        -ContentType "application/zip" -InFile $FilePath | Out-Null
    Write-Host "  OK"
}

Set-Location $Abcs

Write-Step "Verify installer zips exist"
$winPath = Join-Path $Abcs "releases\$WinZip"
$linuxPath = Join-Path $Abcs "releases\$LinuxZip"
$linuxLegacyPath = Join-Path $Abcs "releases\$LinuxZipLegacy"
if (-not (Test-Path -LiteralPath $linuxPath)) {
    if (Test-Path -LiteralPath $linuxLegacyPath) {
        throw (
            "Linux zip must be lowercase '$LinuxZip'. " +
            "Found legacy/mixed-case '$LinuxZipLegacy' - rename it to lowercase and re-run."
        )
    }
    throw "Missing Linux installer: $linuxPath (expected lowercase build output)"
}
if (Test-Path -LiteralPath $linuxLegacyPath) {
    Write-Host (
        "  WARNING: also found legacy '$LinuxZipLegacy' - upload uses lowercase '$LinuxZip' only."
    ) -ForegroundColor Yellow
}
foreach ($p in @($winPath, $linuxPath)) {
    if (-not (Test-Path -LiteralPath $p)) { throw "Missing installer: $p" }
    $mb = [math]::Round((Get-Item -LiteralPath $p).Length / 1MB, 1)
    Write-Host "  $(Split-Path $p -Leaf) ($mb MB)"
}

Write-Step "Verify git tag $Tag on main (create/push if missing)"
Invoke-Git @("fetch", "origin", "main")
$localTag = git tag -l $Tag
if (-not $localTag) {
    Invoke-Git @("tag", "-a", $Tag, "-m", $ReleaseName)
}
Invoke-Git @("push", "origin", $Tag)

$releaseNotes = @"
AbCS $Version

**What's new**
- Import duplicate detection strips series numbers on both sides and uses the number as a tiebreaker (``01`` vs ``02`` no longer collide; bare titles still match).
- Folder import keeps the duplicate index live during a scan so same-pass duplicates are caught.
- Find (Ctrl+F) opens with an empty search box each time.
- Book List Import shows Import Progress with live counters; Escape cancels and keeps books already added.

**Downloads**
- **Windows:** ``$WinZip`` - extract and run ``AbCS-Setup.exe`` (SmartScreen may warn; see README).
- **Linux:** ``$LinuxZip`` - extract and run the install script inside the archive.

**License:** Free and source-available (custom non-commercial license). See ``AbCS_License.txt``.
"@

$gh = Get-GhExe
if ($gh -and -not $env:GITHUB_TOKEN) {
    Write-Step "Using GitHub CLI"
    $authOk = $false
    $prev = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    gh auth status 2>&1 | Out-Null
    $ErrorActionPreference = $prev
    if ($LASTEXITCODE -eq 0) { $authOk = $true }
    if (-not $authOk) {
        throw @"
GitHub CLI is installed but not logged in.
Run in PowerShell:
  gh auth login
Then re-run:
  powershell -ExecutionPolicy Bypass -File C:\projects\AbCS\scripts\publish_github_release.ps1
"@
    }
    Write-Host "Ensuring repo is public ..."
    $prevVis = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    & $gh repo edit "$Owner/$Repo" --visibility public --accept-visibility-change-consequences 2>&1 | Out-Null
    $ErrorActionPreference = $prevVis
    # Ignore failure if already public
    Write-Host "Creating release $Tag ..."
    $prevRel = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $null = & $gh release view $Tag --repo "$Owner/$Repo" 2>$null
    $releaseExists = ($LASTEXITCODE -eq 0)
    $ErrorActionPreference = $prevRel
    if (-not $releaseExists) {
        Invoke-Gh @(
            "release", "create", $Tag,
            "--repo", "$Owner/$Repo",
            "--title", $ReleaseName,
            "--notes", $releaseNotes,
            $winPath, $linuxPath
        )
    }
    else {
        Write-Host "Release $Tag already exists; uploading assets if missing ..."
        Invoke-Gh @("release", "upload", $Tag, $winPath, $linuxPath, "--repo", "$Owner/$Repo", "--clobber")
    }
}
else {
    Write-Step "Using GitHub REST API (GITHUB_TOKEN)"
    $headers = Get-GitHubHeaders
    Set-RepoPublic -Headers $headers
    $release = Get-OrCreateRelease -Headers $headers -Notes $releaseNotes
    Upload-ReleaseAsset -Headers $headers -Release $release -FilePath $winPath
    Upload-ReleaseAsset -Headers $headers -Release $release -FilePath $linuxPath
}

Write-Step "DONE"
Write-Host "Release URL: https://github.com/$Owner/$Repo/releases/tag/$Tag"
Write-Host ""
Write-Host "Manual checks:"
Write-Host "  - Settings -> Collaborators -> Dominic still has access"
Write-Host "  - Wire AbCS Carrd download buttons to the release asset URLs"
