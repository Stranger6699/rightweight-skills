: << 'CMDBLOCK'
@echo off
if "%~1"=="" exit /b 1
set "HOOK_DIR=%~dp0"
if exist "C:\Program Files\Git\bin\bash.exe" "C:\Program Files\Git\bin\bash.exe" "%HOOK_DIR%%~1" %2 %3 %4 %5 %6 %7 %8 %9
if %ERRORLEVEL% equ 0 exit /b 0
if exist "C:\Program Files (x86)\Git\bin\bash.exe" "C:\Program Files (x86)\Git\bin\bash.exe" "%HOOK_DIR%%~1" %2 %3 %4 %5 %6 %7 %8 %9
if %ERRORLEVEL% equ 0 exit /b 0
for /f "delims=" %%G in ('git --exec-path 2^>nul') do set "GIT_EXEC=%%G"
if defined GIT_EXEC for %%B in ("%GIT_EXEC%\..\..\bin\bash.exe") do if exist "%%~fB" "%%~fB" "%HOOK_DIR%%~1" %2 %3 %4 %5 %6 %7 %8 %9
if %ERRORLEVEL% equ 0 exit /b 0
where bash >nul 2>nul
if %ERRORLEVEL% equ 0 bash "%HOOK_DIR%%~1" %2 %3 %4 %5 %6 %7 %8 %9
exit /b %ERRORLEVEL%
CMDBLOCK
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPT_NAME="$1"
shift
exec bash "${SCRIPT_DIR}/${SCRIPT_NAME}" "$@"
