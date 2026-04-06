# AbCS Extension Cleanup Script
# Removes unused extensions to declutter VS Code and improve startup performance
# Run: .\cleanup_extensions.ps1

$codePath = "$env:LOCALAPPDATA\Programs\Microsoft VS Code\bin\code.cmd"

Write-Host "=== AbCS Extension Cleanup ===" -ForegroundColor Green
Write-Host "This will uninstall unused extensions for your Python project."
Write-Host ""

# Extensions to remove (safe for Python/PySide6 development)
$removeExtensions = @(
    "redhat.java",
    "vscjava.vscode-gradle",
    "vscjava.vscode-java-debug",
    "vscjava.vscode-java-dependency",
    "vscjava.vscode-java-pack",
    "vscjava.vscode-java-test",
    "vscjava.vscode-maven",
    "atkivisolutioninstadotnetmodelgenerator.winforms-designer",
    "ms-vscode.azure-repos",
    "github.codespaces",
    "github.remotehub",
    "ms-vscode-remote.remote-containers",
    "deque-systems.vscode-axe-linter",
    "free-sqlite.free-sqlite",
    "ganeshpawar.sqlite-studio",
    "rohit-chouhan.sqlite-snippet",
    "chrischinchilla.vscode-pandoc",
    "anticultist.ms-access-dump-format",
    "ms-vscode.vscode-speech"
)

# Extensions to KEEP (essential for AbCS)
$keepExtensions = @(
    "ms-python.python",
    "ms-python.black-formatter",
    "ms-python.vscode-pylance",
    "ms-python.debugpy",
    "ms-python.vscode-python-envs",
    "github.copilot-chat",
    "github.vscode-pull-request-github",
    "ms-vscode.powershell",
    "mtxr.sqltools",
    "mtxr.sqltools-driver-sqlite",
    "donjayamanne.githistory",
    "vscjava.vscode-gradle",
    "mechatroner.rainbow-csv",
    "yy0931.vscode-sqlite3-editor"
)

Write-Host "Extensions to REMOVE ($($removeExtensions.Count) total):" -ForegroundColor Yellow
$removeExtensions | ForEach-Object { Write-Host "  ❌ $_" }

Write-Host ""
Write-Host "Extensions to KEEP ($($keepExtensions.Count) essential):" -ForegroundColor Cyan
$keepExtensions | ForEach-Object { Write-Host "  ✓ $_" }

Write-Host ""
$response = Read-Host "Proceed with removal? (y/n)"

if ($response -eq 'y' -or $response -eq 'yes') {
    Write-Host ""
    Write-Host "Uninstalling extensions..." -ForegroundColor Yellow
    
    $successCount = 0
    $failCount = 0
    
    foreach ($ext in $removeExtensions) {
        try {
            & $codePath --uninstall-extension $ext --force 2>&1 | Out-Null
            Write-Host "  ✓ Removed: $ext"
            $successCount++
        }
        catch {
            Write-Host "  ✗ Failed: $ext" -ForegroundColor Red
            $failCount++
        }
    }
    
    Write-Host ""
    Write-Host "=== Cleanup Complete ===" -ForegroundColor Green
    Write-Host "Removed: $successCount extensions"
    Write-Host "Failed: $failCount extensions"
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Close VS Code completely"
    Write-Host "2. Run: Developer: Reload Window (Ctrl+Shift+P)"
    Write-Host "3. Open a Python file and test: Format Document (Ctrl+Shift+I)"
    Write-Host ""
}
else {
    Write-Host "Cleanup cancelled." -ForegroundColor Yellow
    exit 0
}
