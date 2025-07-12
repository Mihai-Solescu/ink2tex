; Ink2TeX Installer Script for Inno Setup
; Creates a professional Windows installer with uninstaller

#define MyAppName "Ink2TeX"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Ink2TeX Project"
#define MyAppURL "https://github.com/ink2tex/ink2tex"
#define MyAppExeName "Ink2TeX.exe"
#define MyAppDescription "Handwritten Math to LaTeX Converter"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
AppId={B8F8F8F8-1234-5678-9ABC-123456789ABC}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=LICENSE.txt
InfoBeforeFile=INSTALL_NOTES.txt
OutputDir=installer
OutputBaseFilename=Ink2TeX_Setup_v{#MyAppVersion}
SetupIconFile=assets\icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1
Name: "autostart"; Description: "Start {#MyAppName} automatically when Windows starts"; GroupDescription: "Startup Options"; Flags: unchecked

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\.api"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\.config"; DestDir: "{app}"; Flags: ignoreversion; AfterInstall: UpdateConfigFile  
Source: "dist\prompt.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion; AfterInstall: CreateLicenseFile
Source: "INSTALL_NOTES.txt"; DestDir: "{app}"; Flags: ignoreversion; AfterInstall: CreateInstallNotes

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Registry]
; Add to startup if user selected the option
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "{#MyAppName}"; ValueData: "{app}\{#MyAppExeName}"; Flags: uninsdeletevalue; Tasks: autostart

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
procedure CreateLicenseFile;
var
  LicenseContent: string;
begin
  LicenseContent := 
    'MIT License' + #13#10 + #13#10 +
    'Copyright (c) 2025 Ink2TeX Project' + #13#10 + #13#10 +
    'Permission is hereby granted, free of charge, to any person obtaining a copy' + #13#10 +
    'of this software and associated documentation files (the "Software"), to deal' + #13#10 +
    'in the Software without restriction, including without limitation the rights' + #13#10 +
    'to use, copy, modify, merge, publish, distribute, sublicense, and/or sell' + #13#10 +
    'copies of the Software, and to permit persons to whom the Software is' + #13#10 +
    'furnished to do so, subject to the following conditions:' + #13#10 + #13#10 +
    'The above copyright notice and this permission notice shall be included in all' + #13#10 +
    'copies or substantial portions of the Software.' + #13#10 + #13#10 +
    'THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR' + #13#10 +
    'IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,' + #13#10 +
    'FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE' + #13#10 +
    'AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER' + #13#10 +
    'LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,' + #13#10 +
    'OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE' + #13#10 +
    'SOFTWARE.';
    
  SaveStringToFile(ExpandConstant('{app}\LICENSE.txt'), LicenseContent, False);
end;

procedure CreateInstallNotes;
var
  NotesContent: string;
begin
  NotesContent := 
    'Ink2TeX - Installation Notes' + #13#10 +
    '================================' + #13#10 + #13#10 +
    '🎉 Thank you for installing Ink2TeX!' + #13#10 + #13#10 +
    'GETTING STARTED:' + #13#10 +
    '1. You need a Google Gemini API key to use this application' + #13#10 +
    '2. Get your free API key at: https://makersuite.google.com/app/apikey' + #13#10 +
    '3. Edit the .api file in the installation folder and add your key' + #13#10 +
    '4. Launch Ink2TeX and press Ctrl+Shift+I to start drawing!' + #13#10 + #13#10 +
    'USAGE:' + #13#10 +
    '• Press Ctrl+Shift+I anywhere to open the drawing overlay' + #13#10 +
    '• Draw your math equations with mouse or stylus' + #13#10 +
    '• Press Enter to convert to LaTeX' + #13#10 +
    '• Press Esc to close the overlay' + #13#10 +
    '• Right-click the system tray icon for options' + #13#10 + #13#10 +
    'CONFIGURATION:' + #13#10 +
    '• .api file: Contains your Google API key' + #13#10 +
    '• .config file: Contains application settings' + #13#10 +
    '• prompt.txt: Contains the AI conversion prompt' + #13#10 + #13#10 +
    'TROUBLESHOOTING:' + #13#10 +
    '• Make sure your API key is valid and has Gemini access' + #13#10 +
    '• Check your internet connection for API calls' + #13#10 +
    '• Try running as administrator if hotkeys don''t work' + #13#10 + #13#10 +
    'For support, visit: https://github.com/ink2tex/ink2tex';
    
  SaveStringToFile(ExpandConstant('{app}\INSTALL_NOTES.txt'), NotesContent, False);
end;

procedure UpdateConfigFile;
var
  ConfigPath: string;
  ConfigLines: TArrayOfString;
  ConfigContent: string;
  I: Integer;
  Updated: Boolean;
  AutoStartValue: string;
begin
  ConfigPath := ExpandConstant('{app}\.config');
  
  // Determine auto-start value based on task selection
  if IsTaskSelected('autostart') then
    AutoStartValue := 'true'
  else
    AutoStartValue := 'false';
  
  // Load existing config file
  if LoadStringsFromFile(ConfigPath, ConfigLines) then
  begin
    Updated := False;
    
    // Update existing AUTO_START_WITH_WINDOWS line
    for I := 0 to GetArrayLength(ConfigLines) - 1 do
    begin
      if Pos('AUTO_START_WITH_WINDOWS=', Uppercase(ConfigLines[I])) = 1 then
      begin
        ConfigLines[I] := 'AUTO_START_WITH_WINDOWS=' + AutoStartValue;
        Updated := True;
        Break;
      end;
    end;
    
    // Add line if not found
    if not Updated then
    begin
      SetArrayLength(ConfigLines, GetArrayLength(ConfigLines) + 1);
      ConfigLines[GetArrayLength(ConfigLines) - 1] := 'AUTO_START_WITH_WINDOWS=' + AutoStartValue;
    end;
    
    // Save back to file
    SaveStringsToFile(ConfigPath, ConfigLines, False);
  end;
end;
