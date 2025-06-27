@echo off

echo.
echo ==============================================================
echo                      TELEGRAM PURGE BOT                      
echo                         Kurulum Sihirbazi                      
echo ==============================================================
echo.

rem Python Kontrolu
echo [1/4] Python kontrol ediliyor...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo HATA: Python kurulu degil!
    echo.
    echo Python'u su adresten indirin: https://python.org
    echo Kurulum sirasinda "Add Python to PATH" secenegini isaretleyin.
    echo.
    pause
    exit /b 1
)
echo Python kurulu:
python --version
echo.

rem Sanal Ortam Olusturma
echo [2/4] Sanal ortam olusturuluyor...
if exist .venv (
    echo Sanal ortam zaten mevcut, guncelleniyor...
    rmdir /s /q .venv
)
python -m venv .venv
if %errorlevel% neq 0 (
    echo HATA: Sanal ortam olusturulamadi.
    pause
    exit /b 1
)
echo Sanal ortam olusturuldu.
echo.

rem Sanal Ortam Aktiflestirme
echo [3/4] Sanal ortam aktiflestiriliyor...
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo HATA: Sanal ortam aktiflestirilemedi.
    pause
    exit /b 1
)
echo Sanal ortam aktiflestirildi.
echo.

rem Paket Yukleme
echo [4/4] Gerekli paketler yukleniyor...
echo.
pip install --upgrade pip >nul 2>&1
echo requirements.txt paketleri yukleniyor...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo HATA: Gerekli paketler yuklenemedi.
    echo.
    echo Cozum onerileri:
    echo * Internet baglantinizi kontrol edin
    echo * Antivirus programinizi gecici olarak devre disi birakin
    echo * Yonetici olarak calistirmayi deneyin
    echo.
    pause
    exit /b 1
)
echo Tum paketler basariyla yuklendi.
echo.

rem Basari Mesaji
echo.
echo ==============================================================
echo                     KURULUM TAMAMLANDI!                    
echo ==============================================================
echo.
echo Sonraki adimlar:
echo 1. settings.json dosyasinda bot token'inizi ayarlayin
echo 2. baslat.bat dosyasini calistirarak botu baslatin
echo.
echo Yardim icin README.md dosyasini inceleyin.
echo.
pause 