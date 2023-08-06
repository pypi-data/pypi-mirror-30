@ECHO OFF
REM Diamond-Patterns (c) Ian Dennis Miller
REM This is a Windows batch file for launching diamond-patterns
REM The script assumes you are using a python virtualenv.

IF NOT DEFINED VIRTUAL_ENV (
    for /f "delims=" %%A in ('where diamond.cmd') do set "DIAMOND_PATH=%%A"
    python.exe "%DIAMOND_PATH:~,-4%" %*
) ELSE (
    %VIRTUAL_ENV%\scripts\python.exe %VIRTUAL_ENV%\scripts\diamond %*
)
