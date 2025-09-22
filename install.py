#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مثبت أداة بايلودات الأندرويد
Android Payload Tool Installer
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_banner():
    """طباعة شعار الأداة"""
    print("=" * 60)
    print("🔧 مثبت أداة بايلودات الأندرويد المتقدمة")
    print("=" * 60)
    print()

def check_python_version():
    """التحقق من إصدار Python"""
    print("🔍 التحقق من إصدار Python...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ خطأ: يتطلب Python 3.8 أو أحدث")
        print(f"   الإصدار الحالي: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - متوافق")
    return True

def check_dependencies():
    """التحقق من المتطلبات"""
    print("\n📦 التحقق من المتطلبات...")
    
    required_packages = [
        'flask', 'cryptography', 'requests', 
        'colorama', 'rich', 'psutil'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - مثبت")
        except ImportError:
            print(f"❌ {package} - غير مثبت")
            missing_packages.append(package)
    
    # التحقق من Android SDK
    print("\n🔧 التحقق من Android SDK...")
    try:
        from tools.sdk_installer import SDKInstaller
        sdk_installer = SDKInstaller()
        
        if sdk_installer.check_java_installation():
            print("✅ Java - مثبت")
        else:
            print("❌ Java - غير مثبت")
            missing_packages.append('java')
        
        # التحقق من Android SDK
        android_home = os.environ.get('ANDROID_HOME') or os.environ.get('ANDROID_SDK_ROOT')
        if android_home and os.path.exists(android_home):
            print("✅ Android SDK - مثبت")
        else:
            print("❌ Android SDK - غير مثبت")
            missing_packages.append('android-sdk')
            
    except Exception as e:
        print(f"⚠️ خطأ في التحقق من Android SDK: {e}")
        missing_packages.append('android-sdk')
    
    return missing_packages

def install_requirements():
    """تثبيت المتطلبات"""
    print("\n📥 تثبيت المتطلبات...")
    
    try:
        # تحديث pip
        print("تحديث pip...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                      check=True, capture_output=True)
        
        # تثبيت المتطلبات
        print("تثبيت المتطلبات من requirements.txt...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True)
        
        print("✅ تم تثبيت المتطلبات بنجاح")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ خطأ في تثبيت المتطلبات: {e}")
        return False

def install_android_sdk():
    """تثبيت Android SDK"""
    print("\n🔧 تثبيت Android SDK...")
    
    try:
        from tools.sdk_installer import SDKInstaller
        sdk_installer = SDKInstaller()
        
        if sdk_installer.setup_complete_environment():
            print("✅ تم تثبيت Android SDK بنجاح")
            return True
        else:
            print("❌ فشل في تثبيت Android SDK")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في تثبيت Android SDK: {e}")
        return False

def create_directories():
    """إنشاء المجلدات المطلوبة"""
    print("\n📁 إنشاء المجلدات...")
    
    directories = [
        'output', 'sessions', 'keys', 'logs', 
        'templates', 'backups'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ {directory}/")
    
    return True

def create_desktop_shortcut():
    """إنشاء اختصار على سطح المكتب"""
    print("\n🔗 إنشاء اختصار على سطح المكتب...")
    
    try:
        system = platform.system()
        
        if system == "Windows":
            create_windows_shortcut()
        elif system == "Darwin":  # macOS
            create_macos_shortcut()
        elif system == "Linux":
            create_linux_shortcut()
        else:
            print("⚠️ نظام التشغيل غير مدعوم لإنشاء الاختصار")
            
    except Exception as e:
        print(f"⚠️ خطأ في إنشاء الاختصار: {e}")

def create_windows_shortcut():
    """إنشاء اختصار Windows"""
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        path = os.path.join(desktop, "Android Payload Tool.lnk")
        target = os.path.join(os.getcwd(), "run.bat")
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = target
        shortcut.WorkingDirectory = os.getcwd()
        shortcut.IconLocation = target
        shortcut.save()
        
        print("✅ تم إنشاء الاختصار على سطح المكتب")
        
    except ImportError:
        print("⚠️ مكتبة winshell غير متوفرة - تم تخطي إنشاء الاختصار")

def create_macos_shortcut():
    """إنشاء اختصار macOS"""
    try:
        # إنشاء ملف .command
        script_content = f"""#!/bin/bash
cd "{os.getcwd()}"
python3 main.py --gui
"""
        
        script_path = os.path.expanduser("~/Desktop/Android Payload Tool.command")
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        os.chmod(script_path, 0o755)
        print("✅ تم إنشاء الاختصار على سطح المكتب")
        
    except Exception as e:
        print(f"⚠️ خطأ في إنشاء الاختصار: {e}")

def create_linux_shortcut():
    """إنشاء اختصار Linux"""
    try:
        desktop_file = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=Android Payload Tool
Comment=أداة بايلودات الأندرويد المتقدمة
Exec=python3 {os.path.join(os.getcwd(), 'main.py')} --gui
Icon=terminal
Terminal=false
Categories=Development;Security;
"""
        
        desktop_path = os.path.expanduser("~/Desktop/android-payload-tool.desktop")
        with open(desktop_path, 'w') as f:
            f.write(desktop_file)
        
        os.chmod(desktop_path, 0o755)
        print("✅ تم إنشاء الاختصار على سطح المكتب")
        
    except Exception as e:
        print(f"⚠️ خطأ في إنشاء الاختصار: {e}")

def run_tests():
    """تشغيل اختبارات أساسية"""
    print("\n🧪 تشغيل الاختبارات الأساسية...")
    
    try:
        # اختبار استيراد الوحدات
        from core.payload_generator import PayloadGenerator
        from core.listener import Listener
        from core.session_manager import SessionManager
        from core.encryption import EncryptionManager
        from utils.helpers import get_local_ip
        from utils.logger import Logger
        
        print("✅ جميع الوحدات تعمل بشكل صحيح")
        
        # اختبار إنشاء كائنات
        logger = Logger()
        payload_gen = PayloadGenerator()
        session_mgr = SessionManager()
        encryption_mgr = EncryptionManager()
        
        print("✅ تم إنشاء الكائنات بنجاح")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في الاختبارات: {e}")
        return False

def main():
    """الدالة الرئيسية للمثبت"""
    print_banner()
    
    # التحقق من إصدار Python
    if not check_python_version():
        input("اضغط Enter للخروج...")
        return
    
    # التحقق من المتطلبات
    missing = check_dependencies()
    
    # تثبيت المتطلبات إذا لزم الأمر
    if missing:
        print(f"\n📦 المتطلبات المفقودة: {', '.join(missing)}")
        
        # تثبيت Python packages
        python_packages = [pkg for pkg in missing if pkg not in ['java', 'android-sdk']]
        if python_packages:
            if not install_requirements():
                input("اضغط Enter للخروج...")
                return
        
        # تثبيت Java و Android SDK
        if 'java' in missing or 'android-sdk' in missing:
            if not install_android_sdk():
                print("⚠️ فشل في تثبيت Android SDK - يمكنك تثبيته يدوياً لاحقاً")
                choice = input("هل تريد المتابعة بدون Android SDK؟ (y/n): ").lower()
                if choice not in ['y', 'yes', 'نعم']:
                    input("اضغط Enter للخروج...")
                    return
    
    # إنشاء المجلدات
    create_directories()
    
    # تشغيل الاختبارات
    if not run_tests():
        print("⚠️ فشل في بعض الاختبارات - قد تحتاج إلى إعادة التثبيت")
    
    # إنشاء الاختصار
    create_desktop_shortcut()
    
    print("\n" + "=" * 60)
    print("🎉 تم تثبيت الأداة بنجاح!")
    print("=" * 60)
    print()
    print("📋 الخطوات التالية:")
    print("1. تشغيل الأداة: python main.py --gui")
    print("2. أو استخدم ملف run.bat (Windows) أو run.sh (Linux/macOS)")
    print("3. اقرأ ملف README.md للحصول على دليل الاستخدام")
    print()
    print("⚠️ تذكر: استخدم هذه الأداة بمسؤولية وأخلاقية!")
    print()
    
    # سؤال المستخدم
    choice = input("هل تريد تشغيل الأداة الآن؟ (y/n): ").lower()
    if choice in ['y', 'yes', 'نعم']:
        print("\n🚀 تشغيل الأداة...")
        try:
            subprocess.run([sys.executable, 'main.py', '--gui'])
        except KeyboardInterrupt:
            print("\n👋 تم إغلاق الأداة")
        except Exception as e:
            print(f"\n❌ خطأ في تشغيل الأداة: {e}")
    
    input("\nاضغط Enter للخروج...")

if __name__ == "__main__":
    main()
