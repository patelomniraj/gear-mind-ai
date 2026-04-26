# ============================================================
# GearMind — Remove Secrets from Git History & Force Push
# Run from: PowerShell (inside project directory)
# ============================================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " GearMind — Git Secret Cleanup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Verify we're in a git repo
if (-not (Test-Path ".git")) {
    Write-Host "[ERROR] Not a Git repository. Run this from the project root." -ForegroundColor Red
    exit 1
}

# Step 2: Check that .env is in .gitignore
$gitignore = Get-Content .gitignore -ErrorAction SilentlyContinue
if ($gitignore -match "^\.env$") {
    Write-Host "[OK] .env is already in .gitignore" -ForegroundColor Green
} else {
    Write-Host "[WARN] Adding .env to .gitignore..." -ForegroundColor Yellow
    Add-Content .gitignore "`n.env"
}

# Step 3: Remove .env from Git tracking (if it was ever staged)
Write-Host ""
Write-Host "[1/5] Removing .env from Git tracking..." -ForegroundColor Yellow
git rm --cached .env 2>$null
git rm --cached api.env 2>$null

# Step 4: Remove the secret files from Git cache
Write-Host "[2/5] Ensuring updated files are staged..." -ForegroundColor Yellow
git add app.py
git add app_final.py
git add gear_api.py
git add spur_app.py
git add .gitignore
git add .env.example

# Step 5: Show what changed
Write-Host ""
Write-Host "[3/5] Changes staged:" -ForegroundColor Yellow
git status --short

# Step 6: Amend the previous commit (rewrites it without the secrets)
Write-Host ""
Write-Host "[4/5] Amending the previous commit to remove secrets..." -ForegroundColor Yellow
git commit --amend --no-edit

# Step 7: Force push to GitHub
Write-Host ""
Write-Host "[5/5] Force pushing to GitHub..." -ForegroundColor Yellow
Write-Host ""
Write-Host ">>> About to run: git push --force-with-lease" -ForegroundColor Red
Write-Host ">>> This will OVERWRITE the remote branch." -ForegroundColor Red
Write-Host ""

$confirm = Read-Host "Type YES to force push, or anything else to skip"
if ($confirm -eq "YES") {
    git push --force-with-lease
    Write-Host ""
    Write-Host "[DONE] Secrets removed and force pushed!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "[SKIPPED] Force push skipped. Run manually:" -ForegroundColor Yellow
    Write-Host "  git push --force-with-lease" -ForegroundColor White
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " IMPORTANT: Rotate your API keys NOW!" -ForegroundColor Red
Write-Host " The old keys were exposed in Git." -ForegroundColor Red
Write-Host " Go to: https://console.groq.com/keys" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
