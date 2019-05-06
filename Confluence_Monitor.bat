@echo off

python --version 2>NUL
if ERRORLEVEL 1 GOTO NOPYTHON
goto :HASPYTHON
goto:eof

:NOPYTHON
echo No Python installation yet found on your system. Installing it now!
.\python\python-3.7.3.exe /quiet InstallAllUsers=0 Include_launcher=0 Include_test=0 Include_pip=1
echo Installing necessary modules...
START python.exe -m pip install atlassian-python-api

:HASPYTHON
echo Checking for necessary modules...
START python.exe -m pip install atlassian-python-api
echo Running Confluence Monitor...
CALL  python main.py
