; Ink2TeX Installer Script for Inno Setup
; Creates a professional Windows installer with uninstaller

#define MyAppName "Ink2TeX"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Ink2TeX Project"
#define MyAppURL "https://github.com/Mihai-Solescu/ink2tex"
#define MyAppExeName "Ink2TeX.exe"
#define MyAppDescription "Handwritten Math to LaTeX Converter"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
AppId={{B8F8F8F8-1234-5678-9ABC-123456789ABC}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={localappdata}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=..\dist\installer
OutputBaseFilename=Ink2TeX_Setup_v{#MyAppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1
Name: "autostart"; Description: "Start {#MyAppName} automatically when Windows starts"; GroupDescription: "Startup Options"; Flags: unchecked

[Files]
Source: "..\dist\portable\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; Don't copy the .api file - it will be created during installation with user's key
Source: "..\.config"; DestDir: "{localappdata}\Ink2TeX"; Flags: ignoreversion onlyifdoesntexist; AfterInstall: UpdateConfigFile  
Source: "..\prompt.txt"; DestDir: "{localappdata}\Ink2TeX"; Flags: ignoreversion onlyifdoesntexist
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\NOTICE"; DestDir: "{app}"; Flags: ignoreversion
; Include modular source structure for runtime module imports
Source: "..\src\ink2tex\*"; DestDir: "{app}\src\ink2tex"; Flags: ignoreversion recursesubdirs createallsubdirs

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
Type: filesandordirs; Name: "{localappdata}\Ink2TeX"

[Code]
var
  ApiKeyPage: TInputQueryWizardPage;
  UserApiKey: string;

procedure InitializeWizard;
begin
  // Create a custom page for API key input
  ApiKeyPage := CreateInputQueryPage(wpSelectTasks,
    'Google Gemini API Key', 'Configure your AI service',
    'Ink2TeX uses Google''s Gemini AI to convert handwritten math to LaTeX. ' +
    'You need a free API key to use this service.' + #13#10 + #13#10 +
    'Get your free API key at: https://makersuite.google.com/app/apikey' + #13#10 + #13#10 +
    'You can enter your API key now or configure it later through the application settings.' + #13#10 +
    'The installer will create a template configuration file in your user profile.');
    
  // Add API key input field
  ApiKeyPage.Add('Google Gemini API Key (optional):', False);
  ApiKeyPage.Values[0] := '';
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  
  if CurPageID = ApiKeyPage.ID then
  begin
    UserApiKey := Trim(ApiKeyPage.Values[0]);
    
    // Basic validation - Gemini keys start with "AIza" and are about 39 characters
    if (UserApiKey <> '') and 
       ((Length(UserApiKey) < 35) or (Copy(UserApiKey, 1, 4) <> 'AIza')) then
    begin
      MsgBox('The API key format appears to be invalid. ' +
             'Google Gemini API keys typically start with "AIza" and are about 39 characters long.' + #13#10 + #13#10 +
             'You can continue without an API key and configure it later through Settings.',
             mbInformation, MB_OK);
    end;
  end;
end;

procedure CreateLicenseFile;
var
  LicenseContent: string;
begin
  LicenseContent := 
    'Apache License' + #13#10 +
    'Version 2.0, January 2004' + #13#10 +
    'http://www.apache.org/licenses/' + #13#10 + #13#10 +
    'Copyright July 2025 Mihai Solescu' + #13#10 + #13#10 +
    'Licensed under the Apache License, Version 2.0 (the "License");' + #13#10 +
    'you may not use this file except in compliance with the License.' + #13#10 +
    'You may obtain a copy of the License at' + #13#10 + #13#10 +
    '    http://www.apache.org/licenses/LICENSE-2.0' + #13#10 + #13#10 +
    'Unless required by applicable law or agreed to in writing, software' + #13#10 +
    'distributed under the License is distributed on an "AS IS" BASIS,' + #13#10 +
    'WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.' + #13#10 +
    'See the License for the specific language governing permissions and' + #13#10 +
    'limitations under the License.' + #13#10;
    
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
    '1. The application is installed in your user profile' + #13#10 +
    '2. If you didn''t enter an API key during installation, get one at:' + #13#10 +
    '   https://makersuite.google.com/app/apikey' + #13#10 +
    '3. Right-click the app tray icon and go to Settings to configure your API key' + #13#10 +
    '4. Launch Ink2TeX and press Ctrl+Shift+I to start drawing!' + #13#10 + #13#10 +
    'USAGE:' + #13#10 +
    '• Press Ctrl+Shift+I anywhere to open the drawing overlay' + #13#10 +
    '• Draw your math equations with mouse or stylus' + #13#10 +
    '• Press Enter to convert to LaTeX' + #13#10 +
    '• Press Esc to close the overlay' + #13#10 +
    '• Right-click the system tray icon for options' + #13#10 + #13#10 +
    'CONFIGURATION:' + #13#10 +
    '• Config files are stored in: %LOCALAPPDATA%\Ink2TeX\' + #13#10 +
    '• .api file: Contains your Google API key' + #13#10 +
    '• .config file: Contains application settings' + #13#10 +
    '• prompt.txt: Contains the AI conversion prompt' + #13#10 +
    '• Use the Settings menu (right-click tray icon) to configure' + #13#10 + #13#10 +
    'TROUBLESHOOTING:' + #13#10 +
    '• Make sure your API key is valid and has Gemini access' + #13#10 +
    '• Check your internet connection for API calls' + #13#10 +
    '• No administrator rights required - runs in user mode' + #13#10 + #13#10 +
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
  ConfigPath := ExpandConstant('{localappdata}\Ink2TeX\.config');
  
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

procedure CurStepChanged(CurStep: TSetupStep);
var
  ApiFileContent: string;
  ApiFilePath: string;
begin
  if CurStep = ssPostInstall then
  begin
    // Ensure config directory exists
    ForceDirectories(ExpandConstant('{localappdata}\Ink2TeX'));
    
    // Create .api file with user's key or template
    ApiFilePath := ExpandConstant('{localappdata}\Ink2TeX\.api');
    
    if UserApiKey <> '' then
    begin
      // User provided an API key
      ApiFileContent := 
        '# Google Gemini API Key Configuration for Ink2TeX' + #13#10 +
        '# Get your free API key from: https://makersuite.google.com/app/apikey' + #13#10 + #13#10 +
        'GOOGLE_API_KEY=' + UserApiKey + #13#10;
    end
    else
    begin
      // Create template file
      ApiFileContent := 
        '# Google Gemini API Key Configuration for Ink2TeX' + #13#10 +
        '# Get your free API key from: https://makersuite.google.com/app/apikey' + #13#10 +
        '# Replace ''your_api_key_here'' with your actual API key' + #13#10 + #13#10 +
        'GOOGLE_API_KEY=your_api_key_here' + #13#10;
    end;
    
    SaveStringToFile(ApiFilePath, ApiFileContent, False);
    
    CreateLicenseFile;
    CreateInstallNotes;
  end;
end;
