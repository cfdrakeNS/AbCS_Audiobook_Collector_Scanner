; AbCS - Audio Book Collector Scanner
; Inno Setup 6 Installer Script
;
; To compile: run build_installer.bat
;             or open this file in Inno Setup IDE and press F9
;
; Version source of truth is src/main.py APP_VERSION.
; build_installer.bat passes MyAppVersion from APP_VERSION via /D.
; The fallback below is used when compiling this .iss directly in ISCC IDE.

#define MyAppName      "AbCS"
#define MyAppFullName  "AbCS - Audio Book Collector Scanner"
#ifndef MyAppVersion
    #define MyAppVersion "1.9.6"
#endif
#define MyAppPublisher "AbCS Project"
#define MyAppURL       "https://github.com/cfdrakeNS/redevelop-AbCS-project"
#define MyAppExeName   "AbCS.exe"

; ──────────────────────────────────────────────────────────────────
; [Setup] - Global installer settings
; ──────────────────────────────────────────────────────────────────
[Setup]
; AppId is a permanent GUID that identifies this app in Add/Remove Programs.
; DO NOT change this after first release or Windows will treat it as a new app.
AppId={{B3F5E8A2-7D4C-4F1E-9C2B-6A8D0E3F5C7B}

AppName={#MyAppFullName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppFullName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Install to C:\Program Files\AbCS\ by default
DefaultDirName={autopf}\{#MyAppName}

; Start Menu folder name
DefaultGroupName={#MyAppName}
AllowNoIcons=yes

; Output: releases\AbCS-Setup-1.9.6.exe
OutputDir=releases
OutputBaseFilename=AbCS-Setup-{#MyAppVersion}

; Installer branding
SetupIconFile=data\Graphics\AbCS.ico
UninstallDisplayIcon={app}\AbCS.ico
LicenseFile=AbCS_License.MD
WizardImageFile=data\Graphics\abcs_installer_splash.png

Compression=lzma2
SolidCompression=yes
WizardStyle=modern dynamic

; Require Windows 10 or later
MinVersion=10.0

; Require admin rights (needed to install to Program Files)
PrivilegesRequired=admin

; 64-bit install
ArchitecturesInstallIn64BitMode=x64compatible

; ──────────────────────────────────────────────────────────────────
; [Languages]
; ──────────────────────────────────────────────────────────────────
[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

; ──────────────────────────────────────────────────────────────────
; [Messages] - Override installer window title text
; ──────────────────────────────────────────────────────────────────
[Messages]
SetupWindowTitle=Setup - {#MyAppFullName} {#MyAppVersion}

; ──────────────────────────────────────────────────────────────────
; [Tasks] - Optional install choices shown to the user
; ──────────────────────────────────────────────────────────────────
[Tasks]
; Desktop shortcut is optional (unchecked by default)
Name: "desktopicon"; \
    Description: "{cm:CreateDesktopIcon}"; \
    GroupDescription: "{cm:AdditionalIcons}"; \
    Flags: unchecked

; ──────────────────────────────────────────────────────────────────
; [Files] - Files to install
; Source: the build output from PyInstaller (onedir mode)
; DestDir: where they go on the user's machine
; ──────────────────────────────────────────────────────────────────
[Files]
Source: "dist\AbCS\*"; \
    DestDir: "{app}"; \
    Flags: ignoreversion recursesubdirs createallsubdirs
Source: "data\Graphics\AbCS.ico"; \
    DestDir: "{app}"; \
    Flags: ignoreversion
Source: "AbCS_License.MD"; \
    DestDir: "{app}"; \
    Flags: ignoreversion
Source: "data\Graphics\abcs_splash.png"; \
    DestDir: "{tmp}"; \
    Flags: dontcopy

; ──────────────────────────────────────────────────────────────────
; [Icons] - Shortcuts created by the installer
; ──────────────────────────────────────────────────────────────────
[Icons]
; Start Menu
Name: "{group}\{#MyAppName}";                       Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\abCS_icon_install.ico"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; Uninstall shortcut in install folder for testers
Name: "{app}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"

; Desktop (only if user chose that task above)
Name: "{commondesktop}\{#MyAppName}"; \
    Filename: "{app}\{#MyAppExeName}"; \
    IconFilename: "{app}\AbCS.ico"; \
    Tasks: desktopicon

; ──────────────────────────────────────────────────────────────────
; [Run] - Actions run at the end of setup
; ──────────────────────────────────────────────────────────────────
[Run]
; Offer to launch AbCS after install completes
Filename: "{app}\{#MyAppExeName}"; \
    Description: "{cm:LaunchProgram,{#MyAppName}}"; \
    Flags: nowait postinstall skipifsilent

; ──────────────────────────────────────────────────────────────────
; [CustomMessages] - must come after [Setup] and [Languages]
; ──────────────────────────────────────────────────────────────────
[CustomMessages]
WelcomeTitle=Welcome to AbCS Setup
WelcomeLine1=AbCS - Audio Book Collector Scanner
WelcomeLine2=A cross-platform audiobook collection manager with full accessibility support.

; ──────────────────────────────────────────────────────────────────
; [Code] - Pascal script, must always be the last section
; ──────────────────────────────────────────────────────────────────
[Code]
var
    WelcomePage: TWizardPage;

procedure InitializeWizard;
begin
    WelcomePage := CreateCustomPage(wpWelcome,
        ExpandConstant('{cm:WelcomeTitle}'),
        ExpandConstant('{cm:WelcomeLine1}') + #13#10 +
        ExpandConstant('{cm:WelcomeLine2}')
    );
end;