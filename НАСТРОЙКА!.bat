@echo off
chcp 65001 > nul

set "program_folder=%~dp0"
"%program_folder%\Python\python.exe" "%program_folder%\settings.py"
pause