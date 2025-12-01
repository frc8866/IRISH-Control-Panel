@echo off
REM Create venv using Python 3.12 if available, otherwise attempt python.exe check
SETLOCAL EnableDelayedExpansion

:: Determine script directory (project root)
SET SCRIPTDIR=%~dp0
PUSHD %SCRIPTDIR%..

:: A name for the virtualenv dir
SET VENV_DIR=.venv-3.12.7

ECHO Checking for Python 3.12...
SET PY_CMD=py -3.12

:: Try py -3.12 first; check if it exists and is correct version
py -3.12 -c "import sys, json; print(''.join(map(str,sys.version_info[:])) )" >nul 2>&1
IF %ERRORLEVEL%==0 (
    ECHO Found Python 3.12 with py launcher; creating venv in %VENV_DIR%...
    py -3.12 -m venv %VENV_DIR%
    GOTO AFTER_CREATE
)

:: Fallback to python in PATH: check if python is 3.12.7
python -c "import sys; print(sys.version)" >nul 2>&1
IF %ERRORLEVEL%==0 (
    FOR /F "tokens=1-2 delims=. " %%a IN ('python -c "import sys;print(sys.version_info[0], sys.version_info[1])"') DO (
        IF %%a==3 IF %%b==12 (
            ECHO Found Python 3.12 in PATH; creating venv in %VENV_DIR%...
            python -m venv %VENV_DIR%
            GOTO AFTER_CREATE
        )
    )
)

:: If still not found, instruct user how to install Python 3.12.7
ECHO.
ECHO Python 3.12 is not found on your system.
ECHO Please install Python 3.12.7 from https://www.python.org/downloads/release/python-3127/ and ensure the "py" launcher or "python" are available on PATH.
ECHO Press any key to exit.
PAUSE >nul
POPD
EXIT /B 1

:AFTER_CREATE
ECHO Upgrading pip in the venv and installing dependencies...
%VENV_DIR%\Scripts\python.exe -m pip install --upgrade pip setuptools wheel || ECHO Failed to upgrade pip (continuing)
IF EXIST requirements.txt (
    %VENV_DIR%\Scripts\pip.exe install -r requirements.txt
) ELSE (
    ECHO No requirements.txt found in repository root. Skipping installation of dependencies.
)

ECHO Creation and installation steps finished.
ECHO To activate the venv, run "%~dp0open_venv_3.12.7.bat" (double-click or run it from File Explorer).
PAUSE >nul
POPD
ENDLOCAL
EXIT /B 0
