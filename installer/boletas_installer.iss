; Boletas V1 - Script de instalador para Inno Setup 6
; Descarga Inno Setup desde: https://jrsoftware.org/isdl.php

#define MyAppName      "Boletas V1"
#define MyAppVersion   "1.1.0"
#define MyAppPublisher "Boletas Software"
#define MyAppExeName   "Boletas.exe"
#define MyAppDir       "..\dist\Boletas"

[Setup]
; Identificador único de la aplicación (no cambiar entre versiones)
AppId={{B0L3T4S-V1-2025-BOLETAS-SISTEMA-PAGOS}

AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL=https://boletas.software
AppSupportURL=https://boletas.software
AppUpdatesURL=https://boletas.software

; Directorio de instalación
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; Sin directorio de datos: la app los crea en AppData del usuario al primer arranque
AllowNoIcons=yes

; Salida del instalador
OutputDir=..\installer_output
OutputBaseFilename=Boletas_V1_Instalador_v{#MyAppVersion}
SetupIconFile=..\boletas.ico

; Compresión
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes

; Estilo moderno
WizardStyle=modern
WizardSizePercent=120

; Privilegios y arquitectura
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64compatible

; Evitar instalar si ya existe una versión más nueva
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName} Installer
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}

; SmartScreen: mostrar nombre del publisher y versión ayuda a la reputación
SignedUninstaller=no

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; \
  Description: "Crear icono en el Escritorio"; \
  GroupDescription: "Accesos directos adicionales:"; \
  Flags: checkedonce

Name: "startupicon"; \
  Description: "Iniciar Boletas V1 con Windows (arranque automático)"; \
  GroupDescription: "Opciones adicionales:"; \
  Flags: unchecked

[Files]
; Copiar toda la carpeta compilada por PyInstaller
Source: "{#MyAppDir}\*"; \
  DestDir: "{app}"; \
  Flags: ignoreversion recursesubdirs createallsubdirs

; Copiar icono suelto (para accesos directos)
Source: "..\boletas.ico"; \
  DestDir: "{app}"; \
  Flags: ignoreversion

[Icons]
; Menú inicio
Name: "{group}\{#MyAppName}"; \
  Filename: "{app}\{#MyAppExeName}"; \
  IconFilename: "{app}\boletas.ico"; \
  Comment: "Sistema de Boletas de Pago"

Name: "{group}\Desinstalar {#MyAppName}"; \
  Filename: "{uninstallexe}"

; Escritorio
Name: "{commondesktop}\{#MyAppName}"; \
  Filename: "{app}\{#MyAppExeName}"; \
  IconFilename: "{app}\boletas.ico"; \
  Tasks: desktopicon; \
  Comment: "Sistema de Boletas de Pago"

; Inicio de Windows (opcional) — se instala por usuario para evitar advertencia
Name: "{userstartup}\{#MyAppName}"; \
  Filename: "{app}\{#MyAppExeName}"; \
  IconFilename: "{app}\boletas.ico"; \
  Tasks: startupicon; \
  Check: not IsAdminInstallMode

[Run]
; Ofrecer abrir la aplicación al terminar la instalación
Filename: "{app}\{#MyAppExeName}"; \
  Description: "Iniciar {#MyAppName} ahora"; \
  Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Limpiar archivos generados en la carpeta de instalación
Type: filesandordirs; Name: "{app}"

[Code]
// Verificar que Windows 10 o superior
function InitializeSetup(): Boolean;
var
  Version: TWindowsVersion;
begin
  GetWindowsVersionEx(Version);
  if Version.Major < 10 then
  begin
    MsgBox(
      'Boletas V1 requiere Windows 10 o superior.' + #13#10 +
      'Su sistema operativo no es compatible.',
      mbError, MB_OK
    );
    Result := False;
  end else
    Result := True;
end;
