@echo off
cd /d C:\_Projetos\Timesheet

echo =========================================
echo Gerando Timesheet Tracker EXE...
echo =========================================

:: Limpa builds antigos
rmdir /s /q build
rmdir /s /q dist

:: Gera novo EXE utilizando o arquivo main.spec
pyinstaller main.spec

echo =========================================
echo ✅ EXE gerado com sucesso em dist\main.exe
echo =========================================
pause
