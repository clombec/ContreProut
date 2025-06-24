set PYTHONOPTIMIZE=0
venv\Scripts\activate && pyinstaller contreprout.py --clean --noconfirm --onefile && rmdir /S /Q build 
pause
