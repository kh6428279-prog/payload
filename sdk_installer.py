#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
أداة تثبيت Android SDK
Android SDK Installer
"""

import os
import sys
import subprocess
import zipfile
import urllib.request
import tempfile
import shutil
from pathlib import Path
from utils.logger import Logger

class SDKInstaller:
    """كلاس تثبيت Android SDK"""
    
    def __init__(self):
        self.logger = Logger()
        self.sdk_urls = {
            'windows': 'https://dl.google.com/android/repository/commandlinetools-win-9477386_latest.zip',
            'linux': 'https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip',
            'macos': 'https://dl.google.com/android/repository/commandlinetools-mac-9477386_latest.zip'
        }
        
    def detect_platform(self):
        """كشف نظام التشغيل"""
        if sys.platform.startswith('win'):
            return 'windows'
        elif sys.platform.startswith('linux'):
            return 'linux'
        elif sys.platform.startswith('darwin'):
            return 'macos'
        else:
            return 'linux'  # افتراضي
    
    def install_sdk(self, install_path=None):
        """تثبيت Android SDK"""
        try:
            if not install_path:
                install_path = self.get_default_sdk_path()
            
            install_path = Path(install_path)
            install_path.mkdir(parents=True, exist_ok=True)
            
            self.logger.info(f"تثبيت Android SDK في: {install_path}")
            
            # تحميل Command Line Tools
            if not self.download_commandline_tools(install_path):
                return False
            
            # إعداد متغيرات البيئة
            self.setup_environment(install_path)
            
            # تثبيت المكونات المطلوبة
            if not self.install_components(install_path):
                return False
            
            self.logger.info("تم تثبيت Android SDK بنجاح")
            return True
            
        except Exception as e:
            self.logger.error(f"خطأ في تثبيت Android SDK: {e}")
            return False
    
    def get_default_sdk_path(self):
        """الحصول على مسار SDK الافتراضي"""
        platform = self.detect_platform()
        
        if platform == 'windows':
            return Path.home() / 'AppData' / 'Local' / 'Android' / 'Sdk'
        elif platform == 'macos':
            return Path.home() / 'Library' / 'Android' / 'sdk'
        else:  # linux
            return Path.home() / 'Android' / 'Sdk'
    
    def download_commandline_tools(self, install_path):
        """تحميل Command Line Tools"""
        try:
            platform = self.detect_platform()
            url = self.sdk_urls[platform]
            
            self.logger.info(f"تحميل Command Line Tools من: {url}")
            
            # تحميل الملف
            with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_file:
                urllib.request.urlretrieve(url, temp_file.name)
                zip_path = temp_file.name
            
            # استخراج الملف
            tools_dir = install_path / 'cmdline-tools'
            tools_dir.mkdir(exist_ok=True)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(tools_dir)
            
            # تنظيف الملف المؤقت
            os.unlink(zip_path)
            
            self.logger.info("تم تحميل Command Line Tools بنجاح")
            return True
            
        except Exception as e:
            self.logger.error(f"خطأ في تحميل Command Line Tools: {e}")
            return False
    
    def setup_environment(self, sdk_path):
        """إعداد متغيرات البيئة"""
        try:
            # إعداد ANDROID_HOME
            os.environ['ANDROID_HOME'] = str(sdk_path)
            os.environ['ANDROID_SDK_ROOT'] = str(sdk_path)
            
            # إضافة أدوات SDK إلى PATH
            tools_path = sdk_path / 'cmdline-tools' / 'latest' / 'bin'
            if tools_path.exists():
                current_path = os.environ.get('PATH', '')
                if str(tools_path) not in current_path:
                    os.environ['PATH'] = f"{tools_path}{os.pathsep}{current_path}"
            
            # إضافة build-tools إلى PATH
            build_tools_dirs = list((sdk_path / 'build-tools').glob('*'))
            if build_tools_dirs:
                latest_build_tools = sorted(build_tools_dirs)[-1]
                current_path = os.environ.get('PATH', '')
                if str(latest_build_tools) not in current_path:
                    os.environ['PATH'] = f"{latest_build_tools}{os.pathsep}{current_path}"
            
            self.logger.info("تم إعداد متغيرات البيئة")
            
        except Exception as e:
            self.logger.error(f"خطأ في إعداد متغيرات البيئة: {e}")
    
    def install_components(self, sdk_path):
        """تثبيت المكونات المطلوبة"""
        try:
            sdkmanager = sdk_path / 'cmdline-tools' / 'latest' / 'bin' / 'sdkmanager'
            
            if not sdkmanager.exists():
                # البحث عن sdkmanager في المجلدات الفرعية
                for root, dirs, files in os.walk(sdk_path / 'cmdline-tools'):
                    if 'sdkmanager' in files:
                        sdkmanager = Path(root) / 'sdkmanager'
                        break
                else:
                    self.logger.error("لم يتم العثور على sdkmanager")
                    return False
            
            # المكونات المطلوبة
            components = [
                'platform-tools',
                'platforms;android-34',
                'build-tools;34.0.0',
                'platforms;android-33',
                'build-tools;33.0.2',
                'platforms;android-32',
                'build-tools;32.0.0'
            ]
            
            for component in components:
                self.logger.info(f"تثبيت {component}...")
                
                cmd = [str(sdkmanager), 'install', component, '--no_https']
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                
                if result.returncode != 0:
                    self.logger.warning(f"فشل في تثبيت {component}: {result.stderr}")
                else:
                    self.logger.info(f"تم تثبيت {component} بنجاح")
            
            return True
            
        except Exception as e:
            self.logger.error(f"خطأ في تثبيت المكونات: {e}")
            return False
    
    def check_java_installation(self):
        """التحقق من تثبيت Java"""
        try:
            result = subprocess.run(['java', '-version'], capture_output=True, text=True)
            if result.returncode == 0:
                self.logger.info("Java مثبت")
                return True
            else:
                self.logger.warning("Java غير مثبت")
                return False
        except FileNotFoundError:
            self.logger.warning("Java غير مثبت")
            return False
    
    def install_java(self):
        """تثبيت Java"""
        try:
            platform = self.detect_platform()
            
            if platform == 'windows':
                return self.install_java_windows()
            elif platform == 'macos':
                return self.install_java_macos()
            else:  # linux
                return self.install_java_linux()
                
        except Exception as e:
            self.logger.error(f"خطأ في تثبيت Java: {e}")
            return False
    
    def install_java_windows(self):
        """تثبيت Java على Windows"""
        self.logger.info("يرجى تثبيت Java يدوياً من: https://adoptium.net/")
        return False
    
    def install_java_macos(self):
        """تثبيت Java على macOS"""
        try:
            # محاولة تثبيت باستخدام Homebrew
            if shutil.which('brew'):
                result = subprocess.run(['brew', 'install', 'openjdk@11'], capture_output=True, text=True)
                if result.returncode == 0:
                    self.logger.info("تم تثبيت Java باستخدام Homebrew")
                    return True
            
            self.logger.info("يرجى تثبيت Java يدوياً من: https://adoptium.net/")
            return False
            
        except Exception as e:
            self.logger.error(f"خطأ في تثبيت Java على macOS: {e}")
            return False
    
    def install_java_linux(self):
        """تثبيت Java على Linux"""
        try:
            # محاولة تثبيت باستخدام apt
            if shutil.which('apt'):
                result = subprocess.run(['sudo', 'apt', 'update'], capture_output=True, text=True)
                result = subprocess.run(['sudo', 'apt', 'install', '-y', 'openjdk-11-jdk'], capture_output=True, text=True)
                if result.returncode == 0:
                    self.logger.info("تم تثبيت Java باستخدام apt")
                    return True
            
            # محاولة تثبيت باستخدام yum
            elif shutil.which('yum'):
                result = subprocess.run(['sudo', 'yum', 'install', '-y', 'java-11-openjdk-devel'], capture_output=True, text=True)
                if result.returncode == 0:
                    self.logger.info("تم تثبيت Java باستخدام yum")
                    return True
            
            # محاولة تثبيت باستخدام dnf
            elif shutil.which('dnf'):
                result = subprocess.run(['sudo', 'dnf', 'install', '-y', 'java-11-openjdk-devel'], capture_output=True, text=True)
                if result.returncode == 0:
                    self.logger.info("تم تثبيت Java باستخدام dnf")
                    return True
            
            self.logger.info("يرجى تثبيت Java يدوياً")
            return False
            
        except Exception as e:
            self.logger.error(f"خطأ في تثبيت Java على Linux: {e}")
            return False
    
    def setup_complete_environment(self):
        """إعداد البيئة الكاملة"""
        try:
            self.logger.info("بدء إعداد البيئة الكاملة...")
            
            # التحقق من Java
            if not self.check_java_installation():
                self.logger.info("تثبيت Java...")
                if not self.install_java():
                    self.logger.error("فشل في تثبيت Java")
                    return False
            
            # تثبيت Android SDK
            self.logger.info("تثبيت Android SDK...")
            if not self.install_sdk():
                self.logger.error("فشل في تثبيت Android SDK")
                return False
            
            self.logger.info("تم إعداد البيئة بنجاح!")
            return True
            
        except Exception as e:
            self.logger.error(f"خطأ في إعداد البيئة: {e}")
            return False
