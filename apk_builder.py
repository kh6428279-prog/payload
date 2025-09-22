#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
أداة بناء APK حقيقي
Real APK Builder Tool
"""

import os
import sys
import subprocess
import shutil
import zipfile
from pathlib import Path
from utils.logger import Logger

class APKBuilder:
    """كلاس بناء APK حقيقي"""
    
    def __init__(self):
        self.logger = Logger()
        self.android_sdk_path = self.find_android_sdk()
        self.java_home = self.find_java_home()
        
    def find_android_sdk(self):
        """البحث عن Android SDK"""
        possible_paths = [
            os.environ.get('ANDROID_HOME'),
            os.environ.get('ANDROID_SDK_ROOT'),
            os.path.expanduser('~/Android/Sdk'),
            os.path.expanduser('~/Library/Android/sdk'),
            'C:\\Users\\{}\\AppData\\Local\\Android\\Sdk'.format(os.getenv('USERNAME', '')),
            '/opt/android-sdk',
            '/usr/local/android-sdk'
        ]
        
        for path in possible_paths:
            if path and os.path.exists(path):
                if os.path.exists(os.path.join(path, 'build-tools')):
                    self.logger.info(f"تم العثور على Android SDK: {path}")
                    return path
        
        self.logger.warning("لم يتم العثور على Android SDK")
        return None
    
    def find_java_home(self):
        """البحث عن Java Home"""
        java_home = os.environ.get('JAVA_HOME')
        if java_home and os.path.exists(java_home):
            return java_home
        
        # البحث عن Java في المسارات الشائعة
        possible_paths = [
            '/usr/lib/jvm/java-8-openjdk',
            '/usr/lib/jvm/java-11-openjdk',
            '/usr/lib/jvm/java-17-openjdk',
            'C:\\Program Files\\Java\\jdk1.8.0_*',
            'C:\\Program Files\\Java\\jdk-11*',
            'C:\\Program Files\\Java\\jdk-17*'
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        self.logger.warning("لم يتم العثور على Java")
        return None
    
    def check_requirements(self):
        """التحقق من المتطلبات"""
        requirements = {
            'Android SDK': self.android_sdk_path is not None,
            'Java': self.java_home is not None,
            'aapt': self.find_tool('aapt'),
            'dx': self.find_tool('dx'),
            'zipalign': self.find_tool('zipalign'),
            'apksigner': self.find_tool('apksigner')
        }
        
        missing = [tool for tool, available in requirements.items() if not available]
        
        if missing:
            self.logger.error(f"المتطلبات المفقودة: {', '.join(missing)}")
            return False
        
        return True
    
    def find_tool(self, tool_name):
        """البحث عن أداة Android"""
        if not self.android_sdk_path:
            return None
        
        # البحث في build-tools
        build_tools_dirs = [d for d in os.listdir(os.path.join(self.android_sdk_path, 'build-tools')) 
                           if os.path.isdir(os.path.join(self.android_sdk_path, 'build-tools', d))]
        
        if build_tools_dirs:
            # استخدام أحدث إصدار
            latest_version = sorted(build_tools_dirs)[-1]
            tool_path = os.path.join(self.android_sdk_path, 'build-tools', latest_version, tool_name)
            
            if os.path.exists(tool_path):
                return tool_path
        
        return None
    
    def create_apk_from_project(self, project_dir, output_apk):
        """إنشاء APK من مشروع Android"""
        try:
            if not self.check_requirements():
                self.logger.error("المتطلبات غير مكتملة")
                return False
            
            # إنشاء APK يدوياً
            return self.build_apk_manually(project_dir, output_apk)
            
        except Exception as e:
            self.logger.error(f"خطأ في إنشاء APK: {e}")
            return False
    
    def build_apk_manually(self, project_dir, output_apk):
        """بناء APK يدوياً"""
        try:
            # إنشاء مجلدات العمل
            work_dir = Path(project_dir) / "build"
            work_dir.mkdir(exist_ok=True)
            
            # مسارات الأدوات
            aapt = self.find_tool('aapt')
            dx = self.find_tool('dx')
            zipalign = self.find_tool('zipalign')
            apksigner = self.find_tool('apksigner')
            
            # 1. إنشاء R.java
            self.logger.info("إنشاء R.java...")
            r_java_cmd = [
                aapt, 'package', '-f', '-m',
                '-J', str(work_dir / 'gen'),
                '-M', str(project_dir / 'app/src/main/AndroidManifest.xml'),
                '-S', str(project_dir / 'app/src/main/res'),
                '-I', os.path.join(self.android_sdk_path, 'platforms', 'android-34', 'android.jar')
            ]
            
            result = subprocess.run(r_java_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                self.logger.error(f"فشل في إنشاء R.java: {result.stderr}")
                return False
            
            # 2. تجميع Java files
            self.logger.info("تجميع ملفات Java...")
            java_files = list((project_dir / 'app/src/main/java').rglob('*.java'))
            r_java_files = list((work_dir / 'gen').rglob('*.java'))
            all_java_files = java_files + r_java_files
            
            if not all_java_files:
                self.logger.error("لم يتم العثور على ملفات Java")
                return False
            
            # إنشاء classpath
            classpath = [
                os.path.join(self.android_sdk_path, 'platforms', 'android-34', 'android.jar'),
                os.path.join(self.android_sdk_path, 'platforms', 'android-34', 'optional', 'org.apache.http.legacy.jar')
            ]
            
            javac_cmd = [
                'javac', '-cp', ':'.join(classpath),
                '-d', str(work_dir / 'classes'),
                *[str(f) for f in all_java_files]
            ]
            
            result = subprocess.run(javac_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                self.logger.error(f"فشل في تجميع Java: {result.stderr}")
                return False
            
            # 3. تحويل إلى DEX
            self.logger.info("تحويل إلى DEX...")
            dx_cmd = [
                dx, '--dex',
                '--output', str(work_dir / 'classes.dex'),
                str(work_dir / 'classes')
            ]
            
            result = subprocess.run(dx_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                self.logger.error(f"فشل في تحويل DEX: {result.stderr}")
                return False
            
            # 4. إنشاء APK
            self.logger.info("إنشاء APK...")
            apk_path = work_dir / 'app-unsigned.apk'
            
            aapt_package_cmd = [
                aapt, 'package', '-f', '-m',
                '-F', str(apk_path),
                '-M', str(project_dir / 'app/src/main/AndroidManifest.xml'),
                '-S', str(project_dir / 'app/src/main/res'),
                '-A', str(project_dir / 'app/src/main/assets') if (project_dir / 'app/src/main/assets').exists() else None,
                '-I', os.path.join(self.android_sdk_path, 'platforms', 'android-34', 'android.jar')
            ]
            
            # إزالة None values
            aapt_package_cmd = [cmd for cmd in aapt_package_cmd if cmd is not None]
            
            result = subprocess.run(aapt_package_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                self.logger.error(f"فشل في إنشاء APK: {result.stderr}")
                return False
            
            # 5. إضافة DEX إلى APK
            self.logger.info("إضافة DEX إلى APK...")
            with zipfile.ZipFile(apk_path, 'a') as apk_zip:
                apk_zip.write(work_dir / 'classes.dex', 'classes.dex')
            
            # 6. محاذاة APK
            self.logger.info("محاذاة APK...")
            aligned_apk = work_dir / 'app-aligned.apk'
            zipalign_cmd = [
                zipalign, '-f', '4',
                str(apk_path), str(aligned_apk)
            ]
            
            result = subprocess.run(zipalign_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                self.logger.error(f"فشل في محاذاة APK: {result.stderr}")
                return False
            
            # 7. توقيع APK
            self.logger.info("توقيع APK...")
            self.create_debug_keystore(work_dir)
            
            apksigner_cmd = [
                'java', '-jar', apksigner,
                'sign',
                '--ks', str(work_dir / 'debug.keystore'),
                '--ks-key-alias', 'androiddebugkey',
                '--ks-pass', 'pass:android',
                '--key-pass', 'pass:android',
                '--out', str(output_apk),
                str(aligned_apk)
            ]
            
            result = subprocess.run(apksigner_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                self.logger.error(f"فشل في توقيع APK: {result.stderr}")
                return False
            
            self.logger.info(f"تم إنشاء APK بنجاح: {output_apk}")
            return True
            
        except Exception as e:
            self.logger.error(f"خطأ في بناء APK يدوياً: {e}")
            return False
    
    def create_debug_keystore(self, work_dir):
        """إنشاء مفتاح debug للتوقيع"""
        keystore_path = work_dir / 'debug.keystore'
        
        if keystore_path.exists():
            return
        
        try:
            keytool_cmd = [
                'keytool', '-genkey', '-v',
                '-keystore', str(keystore_path),
                '-alias', 'androiddebugkey',
                '-keyalg', 'RSA',
                '-keysize', '2048',
                '-validity', '10000',
                '-storepass', 'android',
                '-keypass', 'android',
                '-dname', 'CN=Android Debug,O=Android,C=US'
            ]
            
            subprocess.run(keytool_cmd, input='\n', text=True, capture_output=True)
            self.logger.info("تم إنشاء مفتاح debug")
            
        except Exception as e:
            self.logger.error(f"خطأ في إنشاء مفتاح debug: {e}")
    
    def create_simple_apk(self, name, config, output_path):
        """إنشاء APK مبسط بدون Android SDK"""
        try:
            # إنشاء APK باستخدام Python فقط
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as apk:
                # AndroidManifest.xml
                manifest = self.create_manifest(name, config)
                apk.writestr('AndroidManifest.xml', manifest)
                
                # ملفات META-INF
                apk.writestr('META-INF/MANIFEST.MF', self.create_manifest_mf())
                apk.writestr('META-INF/CERT.SF', self.create_cert_sf())
                apk.writestr('META-INF/CERT.RSA', b'')  # شهادة فارغة
                
                # ملفات الموارد
                apk.writestr('resources.arsc', self.create_resources_arsc())
                
                # ملف DEX مبسط
                apk.writestr('classes.dex', self.create_simple_dex())
            
            self.logger.info(f"تم إنشاء APK مبسط: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"خطأ في إنشاء APK مبسط: {e}")
            return False
    
    def create_manifest(self, name, config):
        """إنشاء AndroidManifest.xml"""
        return f"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.payload.app"
    android:versionCode="1"
    android:versionName="1.0">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
    <uses-permission android:name="android.permission.CAMERA" />
    <uses-permission android:name="android.permission.RECORD_AUDIO" />
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
    <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
    <uses-permission android:name="android.permission.WAKE_LOCK" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />

    <application
        android:allowBackup="true"
        android:icon="@android:drawable/ic_launcher_foreground"
        android:label="{name}"
        android:theme="@android:style/Theme.Material">
        
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:theme="@android:style/Theme.Material">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
        
        <service
            android:name=".PayloadService"
            android:enabled="true"
            android:exported="false" />
            
    </application>

</manifest>"""
    
    def create_manifest_mf(self):
        """إنشاء MANIFEST.MF"""
        return """Manifest-Version: 1.0
Created-By: Android Payload Tool
"""
    
    def create_cert_sf(self):
        """إنشاء CERT.SF"""
        return """Signature-Version: 1.0
Created-By: Android Payload Tool
"""
    
    def create_resources_arsc(self):
        """إنشاء resources.arsc مبسط"""
        # ملف resources.arsc مبسط
        return b'\x02\x00\x0c\x00\x00\x00\x00\x00\x01\x00\x1c\x00\x00\x00\x00\x00'
    
    def create_simple_dex(self):
        """إنشاء ملف DEX مبسط"""
        # ملف DEX مبسط (header فقط)
        dex_header = bytearray([
            0x64, 0x65, 0x78, 0x0a, 0x30, 0x33, 0x35, 0x00,  # dex magic
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # checksum
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # signature
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # file_size
            0x70, 0x00, 0x00, 0x00, 0x70, 0x00, 0x00, 0x00,  # header_size
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # endian_tag
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # link_size
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # link_off
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # map_off
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # string_ids_size
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # string_ids_off
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # type_ids_size
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # type_ids_off
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # proto_ids_size
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # proto_ids_off
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # field_ids_size
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # field_ids_off
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # method_ids_size
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # method_ids_off
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # class_defs_size
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # class_defs_off
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # data_size
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00   # data_off
        ])
        
        # إضافة padding
        padding = b'\x00' * (112 - len(dex_header))
        return bytes(dex_header) + padding
