; RipWave one-click installer (Inno Setup)
;
; Produces RipWave-Setup.exe — a single .exe that installs RipWave to
; %LOCALAPPDATA%\RipWave, bundles yt-dlp.exe and ffmpeg.exe, and creates
; a desktop shortcut. Runs without admin (PrivilegesRequired=lowest), so
; there is no UAC prompt — true one-click install.

#define MyAppName      "RipWave"
#define MyAppPublisher "RipWave"
#define MyAppURL       "https://github.com/toyuvalo/ripwave"
#define MyAppExeName   "RipWave.exe"

#ifndef MyAppVersion
  #define MyAppVersion "0.0.0"
#endif

[Setup]
AppId={{7E4B3A1D-9B5C-4E8A-9F2D-RIPWAVE00001}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName={localappdata}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
DisableDirPage=yes
DisableReadyPage=yes
DisableFinishedPage=no
PrivilegesRequired=lowest
OutputBaseFilename=RipWave-Setup
OutputDir=.
Compression=lzma2/ultra
SolidCompression=yes
WizardStyle=modern
SetupIconFile=..\assets\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
CloseApplications=yes
RestartApplications=no
; Show license / readme pages? — no, one-click means no friction.

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Shortcuts:"; Flags: checkedonce

[Files]
Source: "..\dist\RipWave.exe";  DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist\yt-dlp.exe";   DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist\ffmpeg.exe";   DestDir: "{app}"; Flags: ignoreversion
Source: "..\assets\icon.ico";   DestDir: "{app}\assets"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\icon.ico"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\icon.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
