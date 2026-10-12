@echo off
setlocal EnableExtensions
chcp 65001 >nul
cd /d "%~dp0"
title Crear SPT Go Portable
echo SPT Go Portable - Crear EXE para Windows x64
echo.
set "SPT_PYTHON="
py -3.12 -c "import sys; sys.exit(0 if sys.maxsize > 2**32 else 1)" >nul 2>&1
if not errorlevel 1 set "SPT_PYTHON=py -3.12"
if defined SPT_PYTHON goto python_listo
py -3 -c "import sys; sys.exit(0 if sys.maxsize > 2**32 and (3,11) <= sys.version_info[:2] <= (3,13) else 1)" >nul 2>&1
if not errorlevel 1 set "SPT_PYTHON=py -3"
if defined SPT_PYTHON goto python_listo
python -c "import sys; sys.exit(0 if sys.maxsize > 2**32 and (3,11) <= sys.version_info[:2] <= (3,13) else 1)" >nul 2>&1
if not errorlevel 1 set "SPT_PYTHON=python"
if defined SPT_PYTHON goto python_listo
echo No se encontro Python de 64 bits compatible.
echo Instala Python 3.12 de 64 bits desde https://www.python.org/downloads/windows/
echo Activa "Add python.exe to PATH" durante la instalacion.
echo Luego vuelve a abrir este archivo.
pause
exit /b 1

:python_listo
echo [1/4] Preparando el entorno de compilacion...
if exist ".venv_spt_go\Scripts\python.exe" goto entorno_listo
%SPT_PYTHON% -m venv ".venv_spt_go"
if errorlevel 1 goto error

:entorno_listo
echo [2/4] Instalando dependencias. Necesitas internet solo para crear el EXE.
".venv_spt_go\Scripts\python.exe" -m pip install --upgrade pip > "Compilacion.log" 2>&1
if errorlevel 1 goto error
".venv_spt_go\Scripts\python.exe" -m pip install --only-binary=:all: -e . -r scripts\requirements-build.txt >> "Compilacion.log" 2>&1
if errorlevel 1 goto error
echo [3/4] Verificando y empaquetando. Esto puede tardar varios minutos.
".venv_spt_go\Scripts\python.exe" scripts\build_windows.py >> "Compilacion.log" 2>&1
if errorlevel 1 goto error
echo [4/4] Listo.
echo.
echo EXE: dist\SPT_Go-Portable.exe
echo Paquete: dist\SPT_Go_Portable_Windows_x64.zip
echo Verificacion: dist\SHA256SUMS
echo Los asistentes no necesitan instalar Python ni las dependencias.
start "" "%~dp0dist"
pause
exit /b 0

:error
echo.
echo No se completo la creacion del EXE.
echo Consulta Compilacion.log para ver el motivo.
echo Si no existe ese archivo, revisa la instalacion de Python.
echo No se genero ni se certifico un EXE funcional.
pause
exit /b 1
