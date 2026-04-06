# Test Black Formatter Integration
# Run this AFTER restarting VS Code to validate the formatter is working

Write-Host "=== Black Formatter Diagnostic ===" -ForegroundColor Green
Write-Host ""

# 1. Check Python environment
Write-Host "1. Checking Python environment..." -ForegroundColor Cyan
$pythonCheck = python --version 2>&1
Write-Host "   $pythonCheck"

# 2. Check Black installation
Write-Host ""
Write-Host "2. Checking Black installation..." -ForegroundColor Cyan
$blackCheck = python -m black --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ $blackCheck"
}
else {
    Write-Host "   ✗ Black not found! Run: pip install black" -ForegroundColor Red
    exit 1
}

# 3. Check VS Code settings
Write-Host ""
Write-Host "3. Checking VS Code settings..." -ForegroundColor Cyan
$settingsFile = ".vscode\settings.json"
if (Test-Path $settingsFile) {
    $settings = Get-Content $settingsFile -Raw | ConvertFrom-Json
    
    if ($settings.'[python]'.'editor.defaultFormatter' -eq 'ms-python.black-formatter') {
        Write-Host "   ✓ Black is default formatter for Python"
    }
    else {
        Write-Host "   ✗ Black is NOT default formatter" -ForegroundColor Red
    }
    
    if ($settings.'[python]'.'editor.formatOnSave') {
        Write-Host "   ✓ Format on Save is enabled"
    }
    else {
        Write-Host "   ✗ Format on Save is disabled" -ForegroundColor Red
    }
}
else {
    Write-Host "   ✗ .vscode\settings.json not found" -ForegroundColor Red
    exit 1
}

# 4. Check extensions
Write-Host ""
Write-Host "4. Checking VS Code extensions..." -ForegroundColor Cyan
$codePath = "$env:LOCALAPPDATA\Programs\Microsoft VS Code\bin\code.cmd"

$pythonExt = & $codePath --list-extensions 2>&1 | Select-String 'ms-python.python'
$blackExt = & $codePath --list-extensions 2>&1 | Select-String 'ms-python.black-formatter'

if ($pythonExt) {
    Write-Host "   ✓ ms-python.python installed"
}
else {
    Write-Host "   ✗ ms-python.python NOT installed" -ForegroundColor Red
}

if ($blackExt) {
    Write-Host "   ✓ ms-python.black-formatter installed"
}
else {
    Write-Host "   ✗ ms-python.black-formatter NOT installed" -ForegroundColor Red
}

# 5. Test formatting a sample file
Write-Host ""
Write-Host "5. Testing Black formatter..." -ForegroundColor Cyan
$testFile = "test_format_sample.py"
$testContent = @"
# Test file - intentionally badly formatted
def hello(  ):
    x=1
    y = 2
    return x,y
"@

$testContent | Set-Content $testFile
Write-Host "   Created: $testFile (badly formatted)"

python -m black --check $testFile 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0 -or $LASTEXITCODE -eq 1) {
    # black --check returns 1 when a file needs formatting, which is expected here.
    Write-Host "   ✓ Black check ran successfully (formatter is working)"
    python -m black $testFile 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ File reformatted successfully"
    }
    else {
        Write-Host "   ✗ Black ran but could not reformat test file" -ForegroundColor Red
    }
}
else {
    Write-Host "   ✗ Black check command failed unexpectedly" -ForegroundColor Red
}

# Clean up
Remove-Item $testFile -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "=== Next Steps ===" -ForegroundColor Yellow
Write-Host "1. Close ALL VS Code windows completely"
Write-Host "2. Reopen VS Code"
Write-Host "3. Open a Python file (.py)"
Write-Host "4. Press Ctrl+Shift+I to format (or right-click > Format Document)"
Write-Host "5. If still no formatter, run:"
Write-Host "   - Developer: Reload Window (Ctrl+Shift+P)"
Write-Host "   - Then try formatting again"
Write-Host ""
Write-Host "For manual verification in VS Code:"
Write-Host "- Open Command Palette (Ctrl+Shift+P)"
Write-Host "- Run: Format Document With..."
Write-Host "- Select: Black Formatter"
Write-Host ""
