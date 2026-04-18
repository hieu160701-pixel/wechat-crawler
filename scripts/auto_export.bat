@echo off
chcp 65001 >nul
cd /d "%~dp0.."

echo ====================================
echo WXCRAWL - Auto Export All
echo ====================================
echo.

echo [1/3] Getting key...
python scripts\get_key.py
echo.

echo [2/3] Decrypting databases...
python scripts\decrypt_db.py
echo.

echo [3/3] Exporting messages...
python scripts\export_messages.py
echo.

echo ====================================
echo DONE!
echo ====================================
pause
