# Fix PDF Generation Issue

## Problem
The PDF generation was failing with error: `doc.autoTable is not a function`

## Root Cause
- jsPDF version 4.2.1 is incompatible with jspdf-autotable 5.0.7
- The old jsPDF version doesn't support the modern autoTable plugin

## Solution
Updated package.json to use compatible versions:
- jsPDF: 4.2.1 → 2.5.2
- jspdf-autotable: 5.0.7 → 3.8.3

## Steps to Fix

1. **Delete node_modules and package-lock.json:**
   ```bash
   cd dashboard
   rm -rf node_modules package-lock.json
   ```

2. **Install updated packages:**
   ```bash
   npm install
   ```

3. **Restart the development server:**
   ```bash
   npm run dev
   ```

## Verification
After following the steps above, try generating a PDF report again. It should work without errors.

## Alternative: Manual Package Update
If you prefer to update manually:
```bash
cd dashboard
npm uninstall jspdf jspdf-autotable
npm install jspdf@2.5.2 jspdf-autotable@3.8.3
```
