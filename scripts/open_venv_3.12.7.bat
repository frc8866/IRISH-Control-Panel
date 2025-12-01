@echo off
REM Launch a new PowerShell window with the venv activated (Windows)
SETLOCAL
SET SCRIPTDIR=%~dp0
PUSHD %SCRIPTDIR%..
SET VENV_DIR=%SCRIPTDIR%..\.venv-3.12.7
IF NOT EXIST "%VENV_DIR%\Scripts\Activate.ps1" (
    ECHO Virtual environment not found at %VENV_DIR%.
    ECHO Please run "%~dp0create_venv_3.12.7.bat" first to create it.
    PAUSE >nul
    POPD
    EXIT /B 1
)

ECHO Opening PowerShell with venv activated...
powershell -NoExit -ExecutionPolicy Bypass -Command "& '%VENV_DIR%\Scripts\Activate.ps1'"
POPD
ENDLOCAL
