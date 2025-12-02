# Fix Project Script - Hard Reset & Clean Install
# Senior DevOps Implementation for Broken Next.js Environment

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "   SMARTAPD PROJECT REPAIR - HARD RESET      " -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# 0. DIRECTORY CHECK
# Cek apakah script dijalankan di root (ada folder web-dashboard) atau sudah di dalam web-dashboard
if (Test-Path "web-dashboard") {
    Write-Host "`n[0/4] Mendeteksi folder 'web-dashboard'. Masuk ke direktori..." -ForegroundColor Cyan
    Set-Location "web-dashboard"
    Write-Host "Current Directory: $(Get-Location)" -ForegroundColor Gray
} elseif (Test-Path "next.config.js") {
    Write-Host "`n[0/4] Berada di root project Next.js." -ForegroundColor Cyan
} else {
    Write-Host "`n[WARNING] Tidak mendeteksi struktur Next.js standard. Script akan tetap berjalan di direktori saat ini." -ForegroundColor Yellow
}

# 1. KILL PROCESS
Write-Host "`n[1/4] Menghentikan semua proses Node.js..." -ForegroundColor Yellow
Stop-Process -Name "node" -Force -ErrorAction SilentlyContinue
Write-Host "Done." -ForegroundColor Green

# 2. CLEAN UP
Write-Host "`n[2/4] Membersihkan sampah (Force Delete node_modules, .next, lockfile)..." -ForegroundColor Yellow

# Hapus package-lock.json
if (Test-Path "package-lock.json") {
    Remove-Item "package-lock.json" -Force
    Write-Host " - package-lock.json deleted." -ForegroundColor Gray
}

# Hapus .next folder
if (Test-Path ".next") {
    Remove-Item ".next" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host " - .next folder deleted." -ForegroundColor Gray
}

# Hapus node_modules (Menggunakan cmd /c rmdir untuk performa lebih baik di Windows dan menghindari error 'path too long')
if (Test-Path "node_modules") {
    Write-Host " - Deleting node_modules (this might take a moment)..." -ForegroundColor Gray
    cmd /c "rmdir /s /q node_modules"
    if (Test-Path "node_modules") {
        # Fallback jika cmd gagal (jarang terjadi)
        Remove-Item "node_modules" -Recurse -Force -ErrorAction SilentlyContinue
    }
    Write-Host " - node_modules deleted." -ForegroundColor Gray
}

# 3. INSTALL DEPENDENCIES
Write-Host "`n[3/4] Menginstall Dependencies (Fixing ERESOLVE)..." -ForegroundColor Yellow
Write-Host "Command: npm install --legacy-peer-deps" -ForegroundColor Magenta

# Eksekusi npm install
npm install --legacy-peer-deps

# Cek status exit code dari npm
if ($LASTEXITCODE -eq 0) {
    Write-Host "`n[SUCCESS] Installasi berhasil!" -ForegroundColor Green
} else {
    Write-Host "`n[ERROR] Installasi gagal. Silakan cek log error di atas." -ForegroundColor Red
    exit
}

# 4. VERIFIKASI & RUN
Write-Host "`n[4/4] Memverifikasi dan menjalankan server..." -ForegroundColor Yellow

if (Test-Path "node_modules") {
    Write-Host "Folder node_modules terdeteksi. Memulai server development..." -ForegroundColor Green
    Start-Sleep -Seconds 2
    npm run dev
} else {
    Write-Host "FATAL: Folder node_modules tidak ditemukan setelah install." -ForegroundColor Red
}
