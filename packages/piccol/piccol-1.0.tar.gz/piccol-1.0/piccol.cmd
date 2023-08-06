@echo off
setlocal ENABLEDELAYEDEXPANSION

set PYPROG=piccol

set PATH=%PATH%;C:\WINDOWS;C:\WINDOWS\SYSTEM32
for /D %%f in ( "C:\PYTHON*" ) do set PATH=!PATH!;%%f
for /D %%f in ( "%USERPROFILE%\AppData\Local\Programs\Python\Python*" ) do set PATH=!PATH!;%%f;%%f\Scripts
for /D %%f in ( "%PROGRAMFILES%\Anaconda3" ) do set PATH=!PATH!;%%f
for /D %%f in ( "%PROGRAMFILES(X86)%\Anaconda3" ) do set PATH=!PATH!;%%f
for /D %%f in ( "%PROGRAMFILES%\Anaconda" ) do set PATH=!PATH!;%%f
for /D %%f in ( "%PROGRAMFILES(X86)%\Anaconda" ) do set PATH=!PATH!;%%f


set PYTHON=pyw
%PYTHON% -h >NUL 2>&1
if %ERRORLEVEL% EQU 0 goto exec_py

set PYTHON=python3
%PYTHON% -h >NUL 2>&1
if %ERRORLEVEL% EQU 0 goto exec_python

set PYTHON=pythonw
%PYTHON% -h >NUL 2>&1
if %ERRORLEVEL% EQU 0 goto exec_python

set PYTHON=py
%PYTHON% -h >NUL 2>&1
if %ERRORLEVEL% EQU 0 goto exec_py

set PYTHON=python
%PYTHON% -h >NUL 2>&1
if %ERRORLEVEL% EQU 0 goto exec_python

echo Did not find Python 3.x in the PATH.
echo Please make sure Python 3.x is installed correctly.
pause
goto end


:exec_py
@echo on
start %PYTHON% -3 -B %PYPROG% %1 %2 %3 %4 %5 %6 %7 %8 %9
@goto end


:exec_python
@echo on
start %PYTHON% -B %PYPROG% %1 %2 %3 %4 %5 %6 %7 %8 %9
@goto end


:end
