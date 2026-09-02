#!/usr/bin/env bash
# ============================================================
#  BG Cleaner — Build Standalone Executable (macOS / Linux)
# ============================================================
set -e

echo ""
echo "  [1/2] Installing build dependencies..."
pip install pyinstaller --quiet

echo ""
echo "  [2/2] Building BG Cleaner..."
pyinstaller bg_cleaner.spec --noconfirm

EXE="dist/BG Cleaner/BG Cleaner"
if [ -f "$EXE" ] || [ -f "dist/BG Cleaner/BG Cleaner.exe" ]; then
    echo ""
    echo "  ========================================"
    echo "   BUILD SUCCESSFUL!"
    echo "   Output: dist/BG Cleaner/"
    echo "   Copy the entire folder to share."
    echo "  ========================================"
else
    echo ""
    echo "  BUILD FAILED — check the output above."
    exit 1
fi
