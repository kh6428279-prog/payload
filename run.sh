#!/bin/bash

# Android Payload Tool Launcher
# Linux/macOS version

echo ""
echo "========================================"
echo "    Android Payload Tool v1.0.0"
echo "========================================"
echo ""

# التحقق من وجود Python
if ! command -v python3 &> /dev/null; then
    echo "خطأ: Python3 غير مثبت أو غير موجود في PATH"
    echo "يرجى تثبيت Python 3.8 أو أحدث"
    exit 1
fi

# التحقق من وجود الملفات المطلوبة
if [ ! -f "main.py" ]; then
    echo "خطأ: ملف main.py غير موجود"
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo "خطأ: ملف requirements.txt غير موجود"
    exit 1
fi

# إنشاء المجلدات المطلوبة
mkdir -p output sessions keys logs templates backups

# تثبيت المتطلبات
echo "تثبيت المتطلبات..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "خطأ في تثبيت المتطلبات"
    exit 1
fi

# تشغيل الأداة
echo ""
echo "بدء تشغيل الأداة..."
echo ""

# التحقق من وجود وسيطة GUI
if [ "$1" = "--gui" ]; then
    python3 main.py --gui
elif [ "$1" = "--test" ]; then
    echo "تشغيل اختبارات النظام..."
    python3 test_apk.py
elif [ "$1" = "--install-sdk" ]; then
    echo "تثبيت Android SDK..."
    python3 -c "from tools.sdk_installer import SDKInstaller; SDKInstaller().setup_complete_environment()"
else
    python3 main.py
fi
