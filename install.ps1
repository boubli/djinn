# DJINN - AI CLI Installer for Windows
Write-Host "🔮 Installing DJINN..." -ForegroundColor Cyan

# Check for Python
if (-not (Get-Command "python" -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Python is not installed. Please install Python 3.8+ first." -ForegroundColor Red
    exit 1
}

# Check for Pip
if (-not (Get-Command "pip" -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Pip is not found. Please ensure pip is in your PATH." -ForegroundColor Red
    exit 1
}

# Install/Update DJINN
Write-Host "📦 Installing/Updating djinn-cli via pip..." -ForegroundColor Yellow
python -m pip install --upgrade djinn-cli

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ DJINN installed successfully!" -ForegroundColor Green
    Write-Host "🚀 Run 'djinn' config to get started." -ForegroundColor Cyan
} else {
    Write-Host "❌ Installation failed." -ForegroundColor Red
    exit 1
}
