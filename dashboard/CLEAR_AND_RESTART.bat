@echo off
echo ========================================
echo Clearing All Caches and Restarting
echo ========================================
echo.

echo [1/5] Stopping any running processes...
taskkill /F /IM node.exe 2>nul
timeout /t 2 /nobreak >nul

echo [2/5] Clearing Vite cache...
if exist node_modules\.vite rmdir /s /q node_modules\.vite
echo Vite cache cleared.

echo [3/5] Clearing dist folder...
if exist dist rmdir /s /q dist
echo Dist folder cleared.

echo [4/5] Clearing browser cache instructions...
echo.
echo IMPORTANT: After the dev server starts, you MUST:
echo   1. Press Ctrl + Shift + R in your browser (hard refresh)
echo   2. Or press Ctrl + F5
echo   3. This clears the browser cache
echo.
pause

echo [5/5] Starting dev server...
echo.
npm run dev
