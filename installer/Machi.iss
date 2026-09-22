; =====================================================================
; MACHI AI Assistant — Inno Setup Script
; Generates Machi_Setup.exe for Windows (per-user, no admin required)
; =====================================================================

#define MyAppName "Machi AI Assistant"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Machi"
#define MyAppURL "https://github.com/machi-assistant"
#define MyAppExeName "Machi.exe"
#define MyAppCopyright "© 2026 Machi"
#define MyAppDescription "Machi AI Desktop Assistant"

[Setup]
AppId={{D37E7A1C-9E4B-4E38-895C-68B744A3D291}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
AppCopyright={#MyAppCopyright}
AppComments={#MyAppDescription}
DefaultDirName={localappdata}\Machi
DisableProgramGroupPage=yes
LicenseFile=..\LICENSE
OutputDir=..\dist
OutputBaseFilename=Machi_Setup
SetupIconFile=..\assets\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ChangesEnvironment=yes
DisableDirPage=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "addtopath"; Description: "Add 'machi' command to Windows User PATH (Recommended)"; GroupDescription: "System Integration:"
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "Additional Shortcuts:"

[Files]
Source: "..\dist\Machi\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\machi.cmd"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\machi.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\assets\icon.ico"; DestDir: "{app}\assets"; Flags: ignoreversion
Source: "..\assets\logo.png"; DestDir: "{app}\assets"; Flags: ignoreversion
Source: "..\.env"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\icon.ico"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\icon.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
Filename: "explorer.exe"; Parameters: """{app}"""; Description: "Open installation folder"; Flags: nowait postinstall unchecked

[Code]
// Helper to broadcast WM_SETTINGCHANGE so new CMD/PowerShell windows see PATH immediately
#ifndef HWND_BROADCAST
  #define HWND_BROADCAST $FFFF
#endif
#ifndef WM_SETTINGCHANGE
  #define WM_SETTINGCHANGE $001A
#endif
#ifndef SMTO_ABORTIFHUNG
  #define SMTO_ABORTIFHUNG $0002
#endif

function SendMessageTimeout(hWnd: Integer; Msg: Cardinal; wParam: LongInt; lParam: String; fuFlags: Cardinal; uTimeout: Cardinal; out lpdwResult: LongInt): LongInt;
external 'SendMessageTimeoutW@user32.dll stdcall';

procedure AddToUserPath(PathToAdd: string);
var
  CurrentPath: string;
  ResultVal: LongInt;
begin
  if not RegQueryStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', CurrentPath) then
    CurrentPath := '';

  if Pos(';' + Uppercase(PathToAdd) + ';', ';' + Uppercase(CurrentPath) + ';') = 0 then
  begin
    if (CurrentPath <> '') and (CurrentPath[Length(CurrentPath)] <> ';') then
      CurrentPath := CurrentPath + ';';
    CurrentPath := CurrentPath + PathToAdd;
    RegWriteStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', CurrentPath);
    // Broadcast setting change
    SendMessageTimeout(HWND_BROADCAST, WM_SETTINGCHANGE, 0, 'Environment', SMTO_ABORTIFHUNG, 5000, ResultVal);
  end;
end;

procedure RemoveFromUserPath(PathToRemove: string);
var
  CurrentPath: string;
  P, Len: Integer;
  ResultVal: LongInt;
begin
  if RegQueryStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', CurrentPath) then
  begin
    P := Pos(Uppercase(PathToRemove), Uppercase(CurrentPath));
    if P > 0 then
    begin
      Len := Length(PathToRemove);
      if (P + Len <= Length(CurrentPath)) and (CurrentPath[P + Len] = ';') then
        Delete(CurrentPath, P, Len + 1)
      else if (P > 1) and (CurrentPath[P - 1] = ';') then
        Delete(CurrentPath, P - 1, Len + 1)
      else
        Delete(CurrentPath, P, Len);

      RegWriteStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', CurrentPath);
      SendMessageTimeout(HWND_BROADCAST, WM_SETTINGCHANGE, 0, 'Environment', SMTO_ABORTIFHUNG, 5000, ResultVal);
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    if WizardIsTaskSelected('addtopath') then
    begin
      AddToUserPath(ExpandConstant('{app}'));
    end;
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
  begin
    RemoveFromUserPath(ExpandConstant('{app}'));
  end;
end;
