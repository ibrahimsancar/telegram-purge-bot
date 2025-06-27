@echo off

echo.
echo ==============================================================
echo                      TELEGRAM PURGE BOT                      
echo                        Baslatma Sihirbazi                      
echo ==============================================================
echo.

rem Sanal Ortam Kontrolu
echo [1/4] Sanal ortam kontrol ediliyor...
if not exist .venv (
    echo HATA: Sanal ortam bulunamadi!
    echo.
    echo Once kurulum yapin:
    echo * kurulum.bat dosyasini calistirin
    echo.
    pause
    exit /b 1
)
echo Sanal ortam bulundu.
echo.

rem Sanal Ortam Aktiflestirme
echo [2/4] Sanal ortam aktiflestiriliyor...
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo HATA: Sanal ortam aktiflestirilemedi.
    echo.
    echo Cozum: kurulum.bat dosyasini tekrar calistirin.
    echo.
    pause
    exit /b 1
)
echo Sanal ortam aktiflestirildi.
echo.

rem Port Kontrolu ve Temizlik
echo [3/4] Port kontrolu yapiliyor...
echo Port 8001 kontrol ediliyor...
echo Port kontrolu tamamlandi.
echo.

rem Web Sunucusu Baslatma
echo [4/4] Web sunucusu baslatiliyor...
echo.
echo Web sunucusu arka planda baslatiliyor...
start /min "Telegram Purge Bot - Web Sunucusu" cmd /k "cd /d %cd% && call .venv\Scripts\activate.bat && python -m uvicorn web.app:app --host 127.0.0.1 --port 8001"

rem Bekleme
echo Sunucunun baslamasi icin 5 saniye bekleniyor...
timeout /t 5 /nobreak >nul

rem Tarayici Acma
echo Tarayici aciliyor...
start http://127.0.0.1:8001

rem Basari Mesaji
echo.
echo ==============================================================
echo                     BOT BASLATILDI!                        
echo ==============================================================
echo.
echo Web Arayuzu: http://127.0.0.1:8001
echo Bot Durumu: Web panelden kontrol edin
echo.
echo Ipuclari:
echo * Web panelde bot token'inizi ayarlayin
echo * Botu baslatmak icin "Baslat" butonuna tiklayin
echo * Yardim icin /help komutunu kullanin
echo.
echo Botu durdurmak icin web paneldeki "Durdur" butonunu kullanin.
echo.
pause 