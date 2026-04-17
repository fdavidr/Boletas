@echo off
chcp 65001 >nul
title Construir Instalador - Boletas V1
color 0A

echo.
echo  ╔══════════════════════════════════════════════════╗
echo  ║       BOLETAS V1 — Construcción del Instalador   ║
echo  ╚══════════════════════════════════════════════════╝
echo.

:: ── Ir al directorio del script ────────────────────────────────────────────
cd /d "%~dp0"

:: ── 1. Verificar Python ────────────────────────────────────────────────────
echo [1/6] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  ERROR: Python no encontrado.
    echo  Descarga Python 3.11 desde https://python.org/downloads
    echo  Asegurate de marcar "Add Python to PATH" durante la instalacion.
    echo.
    pause & exit /b 1
)
python --version
echo.

:: ── 2. Instalar/actualizar dependencias ────────────────────────────────────
echo [2/6] Instalando dependencias del proyecto...
pip install -r requirements.txt -q
if %errorlevel% neq 0 (
    echo  ERROR: Fallo al instalar dependencias.
    pause & exit /b 1
)

echo [2/6] Instalando PyInstaller...
pip install pyinstaller>=6.0 -q
if %errorlevel% neq 0 (
    echo  ERROR: Fallo al instalar PyInstaller.
    pause & exit /b 1
)
echo  Dependencias OK.
echo.

:: ── 3. Crear icono ─────────────────────────────────────────────────────────
echo [3/6] Generando icono...
if not exist "boletas.ico" (
    python crear_icono.py
    if %errorlevel% neq 0 (
        echo  AVISO: No se pudo crear el icono. Se usara el icono por defecto.
    )
) else (
    echo  Icono ya existe, omitiendo.
)
echo.

:: ── 4. Limpiar compilaciones anteriores ────────────────────────────────────
echo [4/6] Limpiando builds anteriores...
if exist "build"  rmdir /s /q "build"
if exist "dist"   rmdir /s /q "dist"
echo  Limpieza OK.
echo.

:: ── 5. Compilar con PyInstaller ────────────────────────────────────────────
echo [5/6] Compilando con PyInstaller (puede tardar 2-5 minutos)...
echo.
pyinstaller boletas.spec --noconfirm

if %errorlevel% neq 0 (
    echo.
    echo  ═══════════════════════════════════════════════
    echo  ERROR: Fallo la compilacion con PyInstaller.
    echo  Revisa los mensajes de error arriba.
    echo  ═══════════════════════════════════════════════
    pause & exit /b 1
)

echo.
echo  Compilacion exitosa. Aplicacion en: dist\Boletas\
echo.

:: ── 6. Crear instalador con Inno Setup ─────────────────────────────────────
echo [6/6] Buscando Inno Setup...

set "ISCC="
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set "ISCC=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
)
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set "ISCC=C:\Program Files\Inno Setup 6\ISCC.exe"
)
if exist "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" (
    set "ISCC=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
)

if defined ISCC (
    echo  Inno Setup encontrado. Creando instalador...
    if not exist "installer_output" mkdir "installer_output"
    "%ISCC%" installer\boletas_installer.iss

    if %errorlevel% neq 0 (
        echo.
        echo  ERROR: Fallo la creacion del instalador Inno Setup.
        pause & exit /b 1
    )

    echo.
    echo  ╔══════════════════════════════════════════════════════╗
    echo  ║  LISTO! Instalador creado exitosamente.              ║
    echo  ║  Ubicacion: installer_output\Boletas_V1_Instalador_* ║
    echo  ╚══════════════════════════════════════════════════════╝
) else (
    echo.
    echo  ┌──────────────────────────────────────────────────────┐
    echo  │  AVISO: Inno Setup no encontrado.                    │
    echo  │                                                      │
    echo  │  Para crear el instalador .exe:                      │
    echo  │  1. Descarga Inno Setup 6 desde:                    │
    echo  │     https://jrsoftware.org/isdl.php                 │
    echo  │  2. Instala y ejecuta de nuevo este script, O:      │
    echo  │  3. Abre Inno Setup y compila manualmente:          │
    echo  │     installer\boletas_installer.iss                 │
    echo  │                                                      │
    echo  │  La aplicacion compilada ya esta disponible en:     │
    echo  │     dist\Boletas\                                   │
    echo  │  Puedes distribuir esa carpeta directamente.        │
    echo  └──────────────────────────────────────────────────────┘
)

echo.
pause
