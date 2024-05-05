@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

rem Путь к программам (текущая папка)
set "program_folder=%~dp0"

rem Получение списка программ
set "counter=0"
for %%A in ("%program_folder%\blitz_cheat_v*.py") do (
    set /a "counter+=1"
    set "program[!counter!]=%%~nxA"
)

rem Вывод списка программ
cls
echo Выберите версию для запуска:
for /l %%i in (1,1,%counter%) do (
    echo [%%i] !program[%%i]!
)

rem Получение выбора пользователя
set /p "choice=Выберите номер версии: "

rem Запуск выбранной программы
if "%choice%" neq "" (
    set "program_to_run=!program[%choice%]!"
    if exist "%program_folder%\!program_to_run!" (
        echo Запускаю программу: !program_to_run!
        %program_folder%\Python\python.exe "%program_folder%\!program_to_run!"
    ) else (
        echo Неверный выбор: "%program_folder%\!program_to_run!"
    )
) else (
    echo Не выбрана версия для запуска.
)

pause
