@echo off
cd /d C:\_Projetos\Timesheet

echo =========================================
echo Gerando Timesheet Tracker EXE...
echo =========================================

:: Limpa builds antigos
rmdir /s /q build
rmdir /s /q dist
del /q main.spec

:: Gera novo EXE com ícone e sem console
pyinstaller --noconfirm --onefile --windowed --icon=assets\TS.ico main.py

echo =========================================
echo EXE gerado com sucesso em dist\main.exe
echo =========================================
pause
