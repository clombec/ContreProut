@echo off
echo Suppression des fichiers temporaires...

del /S /Q *.pyc 2>nul
for /d /r %%d in (__pycache__) do @if exist "%%d" rmdir /S /Q "%%d"
rmdir /S /Q build 2>nul
rmdir /S /Q dist 2>nul
rmdir /S /Q venv 2>nul

echo Recreation de l'environnement virtuel...
py -m venv venv

echo Activation de l'environnement et installation des dependances...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt

echo Termine.
pause
