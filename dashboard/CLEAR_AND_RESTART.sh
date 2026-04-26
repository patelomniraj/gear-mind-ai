#!/bin/bash

echo "========================================"
echo "Clearing All Caches and Restarting"
echo "========================================"
echo ""

echo "[1/5] Stopping any running processes..."
pkill -f "vite" 2>/dev/null || true
sleep 2

echo "[2/5] Clearing Vite cache..."
rm -rf node_modules/.vite
echo "Vite cache cleared."

echo "[3/5] Clearing dist folder..."
rm -rf dist
echo "Dist folder cleared."

echo "[4/5] Clearing browser cache instructions..."
echo ""
echo "IMPORTANT: After the dev server starts, you MUST:"
echo "  1. Press Ctrl + Shift + R in your browser (hard refresh)"
echo "  2. Or press Ctrl + F5 (Windows) / Cmd + Shift + R (Mac)"
echo "  3. This clears the browser cache"
echo ""
read -p "Press Enter to continue..."

echo "[5/5] Starting dev server..."
echo ""
npm run dev
