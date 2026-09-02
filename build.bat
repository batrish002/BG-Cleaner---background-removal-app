@echo off
REM ============================================================
REM  BG Cleaner — Build Standalone .exe (Windows)
REM ============================================================
echo.
echo  [1/2] Installing build dependencies...
pip install pyinstaller --quiet

echo.
echo  [2/2] Building BG Cleaner.exe ...
pyinstaller bg_cleaner.spec --noconfirm

echo.
if exist "dist\BG Cleaner\BG Cleaner.exe" (
    echo  ========================================
    echo   BUILD SUCCESSFUL!
    echo   Output: dist\BG Cleaner\BG Cleaner.exe
    echo   Copy the entire "dist\BG Cleaner" folder
    echo   to share with others.
    echo  ========================================
) else (
    echo  BUILD FAILED — check the output above for errors.
)
echo.
pause
