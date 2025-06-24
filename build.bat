set PYTHONOPTIMIZE=0
rmdir /S /Q build 2>nul
rmdir /S /Q dist 2>nul
venv\Scripts\activate && pyinstaller contreprout.py --clean --noconfirm --onefile --noconsole && rmdir /S /Q build  && copy /Y "icon.png" "dist\\icon.png"
pause
