@echo off
title Android Payload Tool
echo.
echo ========================================
echo    Android Payload Tool v1.0.0
echo ========================================
echo.

REM التحقق من وجود Python
python --version >nul 2>&1
if errorlevel 1 (
    echo خطأ: Python غير مثبت أو غير موجود في PATH
    echo يرجى تثبيت Python 3.8 أو أحدث
    pause
    exit /b 1
)

REM التحقق من وجود الملفات المطلوبة
if not exist "main.py" (
    echo خطأ: ملف main.py غير موجود
    pause
    exit /b 1
)

if not exist "requirements.txt" (
    echo خطأ: ملف requirements.txt غير موجود
    pause
    exit /b 1
)

REM إنشاء المجلدات المطلوبة
if not exist "output" mkdir output
if not exist "sessions" mkdir sessions
if not exist "keys" mkdir keys
if not exist "logs" mkdir logs
if not exist "templates" mkdir templates
if not exist "backups" mkdir backups

REM تثبيت المتطلبات
echo تثبيت المتطلبات...
pip install -r requirements.txt

if errorlevel 1 (
    echo خطأ في تثبيت المتطلبات
    pause
    exit /b 1
)

REM تشغيل الأداة
echo.
echo بدء تشغيل الأداة...
echo.

REM التحقق من وجود وسيطة GUI
if "%1"=="--gui" (
    python main.py --gui
) else if "%1"=="--test" (
    echo تشغيل اختبارات النظام...
    python test_apk.py
) else if "%1"=="--install-sdk" (
    echo تثبيت Android SDK...
    python -c "from tools.sdk_installer import SDKInstaller; SDKInstaller().setup_complete_environment()"
) else (
    python main.py
)

pause
