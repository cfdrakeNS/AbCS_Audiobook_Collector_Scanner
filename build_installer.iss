; AbCS - Audio Book Collector Scanner
; Inno Setup 6 Installer Script
;
; To compile: run build_installer.bat
;
; or open this file in Inno Setup IDE and press F9
;
; Version source of truth is src/build_config.py APP_VERSION.
;
; build_installer.bat passes MyAppVersion from APP_VERSION via /D.
; The fallback below is used when compiling this .iss directly in ISCC IDE.
#define MyAppName      "AbCS"
#define MyAppFullName  "AbCS - Audio Book Collector Scanner"
#ifndef MyAppVersion
    #define MyAppVersion "1.9.73"
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

; Output: releases\AbCS-Setup-{version}.exe (version from APP_VERSION)
OutputDir=releases
OutputBaseFilename=AbCS-Setup-{#MyAppVersion}

; ── Installer branding ────────────────────────────────────────────
; Icon embedded into Setup.exe itself and shown in taskbar/title bar
SetupIconFile=graphics\abcs_icon_256x256.ico

; Icon shown in Windows Add/Remove Programs after install
UninstallDisplayIcon={app}\abcs_icon_256x256.ico

; Large portrait image: left sidebar on Welcome and Finish pages
WizardImageFile=installer_graphics\abcs_wizard_164x314.png

; Small square image: top-right corner on all inner wizard pages
WizardSmallImageFile=installer_graphics\abcs_small_55x55.png

LicenseFile=AbCS_License.txt

Compression=lzma2
SolidCompression=yes
WizardStyle=modern
WizardResizable=yes

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
; Source: the build output from PyInstaller
; DestDir: where they go on the user's machine
; ──────────────────────────────────────────────────────────────────
[Files]
; Main Executable
Source: "dist\AbCS\AbCS.exe"; DestDir: "{app}"; Flags: ignoreversion

; Optional libraries/files (onedir mode)
Source: "dist\AbCS\*.dll"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "dist\AbCS\*.pyd"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "dist\AbCS\*.txt"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

; Internal PyInstaller folder (onedir mode)
Source: "dist\AbCS\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist

; Copy only the schema file, not the whole data folder
Source: "data\abcdDB_def.sql"; DestDir: "{app}\data"; Flags: ignoreversion skipifsourcedoesntexist

; Graphics sourced from _internal (onedir mode)
Source: "dist\AbCS\_internal\Graphics\*"; DestDir: "{app}\Graphics"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist

; Local project graphics
Source: "graphics\abcs_icon_256x256.ico"; DestDir: "{app}"; Flags: ignoreversion

; Installer-only graphics (not copied to app folder)
Source: "installer_graphics\abcs_wizard_164x314.png"; DestDir: "{tmp}"; Flags: dontcopy
Source: "installer_graphics\abcs_small_55x55.png";    DestDir: "{tmp}"; Flags: dontcopy

Source: "AbCS_License.txt"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

; User help documentation
Source: "help_docs\*"; DestDir: "{app}\help_docs"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist

; ──────────────────────────────────────────────────────────────────
; [Icons] - Shortcuts created by the installer
; ──────────────────────────────────────────────────────────────────
[Icons]
; Start Menu
Name: "{group}\{#MyAppName}";                       Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\abcs_icon_256x256.ico"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; Uninstall shortcut in install folder for testers
Name: "{app}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"

; Desktop (only if user chose that task above)
Name: "{commondesktop}\{#MyAppName}"; \
    Filename: "{app}\{#MyAppExeName}"; \
    IconFilename: "{app}\abcs_icon_256x256.ico"; \
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
; [UninstallDelete] - Extra cleanup the uninstaller must force-remove
; ──────────────────────────────────────────────────────────────────
[UninstallDelete]
; Cleanup extra folders that Inno Setup might leave behind
Type: filesandordirs; Name: "{app}\_internal"
Type: filesandordirs; Name: "{app}\data"
Type: filesandordirs; Name: "{app}\Graphics"

; Remove {app} itself if empty after all other cleanup is done
Type: dirifempty;     Name: "{app}"

; ──────────────────────────────────────────────────────────────────
; [Code] - Custom Logic and Splash/Features Screen
; ──────────────────────────────────────────────────────────────────
[Code]
var
  FeaturesPage: TOutputMsgMemoWizardPage;

procedure InitializeWizard;
var
  FeaturesText: String;
begin
  { Construct the Features and Accessibility text }
  FeaturesText :=
    'FEATURES -' + #13#10 +
    '• Audio Book Management with full metadata.' + #13#10 +
    '• ID3 Tag Import from Most Audio Format Files.' + #13#10 +
    '• Web import & Updated Metadata.' + #13#10 +
    '• Advanced Search and Filtering.' + #13#10 +
    '• Complete Keyboard Navigation.' + #13#10 +
    '• Screen Reader Support.' + #13#10 +
    '• Scalable UI (50%-200%+).' + #13#10 +
    '• High Contrast Themes.' + #13#10 + #13#10 +
    'ACCESSIBILITY.' + #13#10 +
    '• Designed for users with low vision and screen readers.' + #13#10 +
    '• All features include keyboard shortcuts.';

  { Create a custom page right after the Welcome page }
  FeaturesPage := CreateOutputMsgMemoPage(wpWelcome,
    'AbCS Features & Accessibility',
    'Review what AbCS can do for you.',
    'Here are the key features and accessibility tools included in this release:',
    FeaturesText);
end;