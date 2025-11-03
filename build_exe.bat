@echo off
chcp 65001 >nul 2>&1
title Ebebek EXE Olusturucu

echo ========================================
echo   EBEBEK EXE OLUSTURUCU
echo ========================================
echo.

REM Python kontrolu
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [HATA] Python bulunamadi!
    echo Lutfen Python'u yukleyin: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python bulundu
echo.

REM PyInstaller kontrolu
python -m pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo [BILGI] PyInstaller yukleniyor...
    python -m pip install pyinstaller
    if %errorlevel% neq 0 (
        echo [HATA] PyInstaller yuklenemedi!
        pause
        exit /b 1
    )
)

echo [OK] PyInstaller hazir
echo.

REM .env dosyasi kontrolu
if not exist .env (
    echo [UYARI] .env dosyasi bulunamadi!
    if exist env.example.txt (
        echo [BILGI] env.example.txt'den .env dosyasi olusturuluyor...
        copy env.example.txt .env >nul
        echo [OK] .env dosyasi olusturuldu
        echo.
        echo [UYARI] Lutfen .env dosyasini duzenleyip SHEET_ID ve diger ayarlari yapin!
        echo.
    )
)

echo [BILGI] EXE dosyasi olusturuluyor...
echo Bu islem birkac dakika surebilir...
echo.

REM Icon olustur
if not exist icon.ico (
    echo [BILGI] Icon olusturuluyor...
    python create_icon.py
    if %errorlevel% neq 0 (
        echo [UYARI] Icon olusturulamadi, icon olmadan devam ediliyor...
        set ICON_PARAM=
    ) else (
        set ICON_PARAM=--icon=icon.ico
    )
) else (
    echo [OK] Icon dosyasi bulundu
    set ICON_PARAM=--icon=icon.ico
)

REM PyInstaller ile EXE olustur
python -m PyInstaller --onefile --windowed ^
    --name "EbebekBarkodTakip" ^
    %ICON_PARAM% ^
    --add-data "templates;templates" ^
    --add-data ".env;." ^
    --hidden-import=flask ^
    --hidden-import=werkzeug ^
    --hidden-import=jinja2 ^
    --hidden-import=dotenv ^
    --hidden-import=ebebek ^
    --hidden-import=openpyxl ^
    --hidden-import=pandas ^
    --hidden-import=requests ^
    --hidden-import=webbrowser ^
    --hidden-import=threading ^
    --hidden-import=ctypes ^
    --collect-all flask ^
    gui.py

if %errorlevel% neq 0 (
    echo.
    echo [HATA] EXE olusturulurken hata olustu!
    pause
    exit /b 1
)

echo.
echo ========================================
echo   EXE BASARIYLA OLUSTURULDU!
echo ========================================
echo.
echo EXE dosyasi: dist\EbebekBarkodTakip.exe
echo.
echo [UYARI] EXE dosyasini calistirmadan once .env dosyasini kontrol edin!
echo.
pause
