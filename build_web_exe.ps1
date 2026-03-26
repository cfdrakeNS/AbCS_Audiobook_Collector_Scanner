#!/usr/bin/env pwsh
# PowerShell wrapper for build_web_exe.bat
# This allows running ./build_web_exe.bat from within Windsurf/PowerShell

# Get the directory of this script
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Run the batch file using cmd.exe
cmd /c "cd /d `"$ScriptDir`" && build_web_exe.bat"

# Exit with the same code as the batch file
exit $LASTEXITCODE
