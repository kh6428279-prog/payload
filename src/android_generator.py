"""
مولد تطبيق Android
Android App Generator
"""

import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from .config import ANDROID_CONFIG, GRADLE_CONFIG, ANDROID_SDK_PATHS
from .utils import find_android_sdk, get_latest_build_tools, test_connection, open_folder


class AndroidAppGenerator:
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()
        
    def setup_ui(self):
        # إطار العنوان
        title_frame = ttk.Frame(self.parent)
        title_frame.pack(pady=10)
        
        title_label = ttk.Label(title_frame, text="مولد تطبيق Android", 
                               font=("Arial", 16, "bold"))
        title_label.pack()
        
        # إطار الإدخال
        input_frame = ttk.LabelFrame(self.parent, text="إعدادات الخادم", padding=10)
        input_frame.pack(pady=10, padx=20, fill="x")
        
        # حقل IP
        ttk.Label(input_frame, text="عنوان IP:").grid(row=0, column=0, sticky="w", pady=5)
        self.ip_entry = ttk.Entry(input_frame, width=20)
        self.ip_entry.grid(row=0, column=1, pady=5, padx=(10, 0))
        self.ip_entry.insert(0, "192.168.1.100")
        
        # حقل Port
        ttk.Label(input_frame, text="المنفذ (Port):").grid(row=1, column=0, sticky="w", pady=5)
        self.port_entry = ttk.Entry(input_frame, width=20)
        self.port_entry.grid(row=1, column=1, pady=5, padx=(10, 0))
        self.port_entry.insert(0, "4444")
        
        # أزرار التحكم
        button_frame = ttk.Frame(self.parent)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="إنشاء تطبيق Android", 
                  command=self.generate_android_app).pack(side="left", padx=5)
        ttk.Button(button_frame, text="اختبار الاتصال", 
                  command=self.test_connection).pack(side="left", padx=5)
        ttk.Button(button_frame, text="فتح مجلد APK", 
                  command=self.open_apk_folder).pack(side="left", padx=5)
        
        # منطقة النتائج
        result_frame = ttk.LabelFrame(self.parent, text="النتائج", padding=10)
        result_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        self.result_text = tk.Text(result_frame, height=10, wrap="word")
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        self.result_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def log_message(self, message: str):
        """إضافة رسالة إلى منطقة النتائج"""
        self.result_text.insert(tk.END, f"{message}\n")
        self.result_text.see(tk.END)
        self.parent.update()
        
    def test_connection(self):
        """اختبار الاتصال بالخادم"""
        try:
            ip = self.ip_entry.get().strip()
            port = int(self.port_entry.get().strip())
            
            self.log_message(f"اختبار الاتصال بـ {ip}:{port}...")
            
            if test_connection(ip, port):
                self.log_message("✅ الاتصال ناجح!")
            else:
                self.log_message("❌ فشل الاتصال - تأكد من أن الخادم يعمل")
                
        except ValueError:
            self.log_message("❌ خطأ: تأكد من إدخال رقم صحيح للمنفذ")
        except Exception as e:
            self.log_message(f"❌ خطأ في الاتصال: {str(e)}")
            
    def generate_android_app(self):
        """إنشاء تطبيق Android وبناء APK"""
        try:
            ip = self.ip_entry.get().strip()
            port = int(self.port_entry.get().strip())
            
            if not ip or not port:
                messagebox.showerror("خطأ", "يرجى إدخال IP والمنفذ")
                return
                
            self.log_message("بدء إنشاء تطبيق Android...")
            
            # إنشاء مجلد المشروع
            project_dir = "android_app"
            if not os.path.exists(project_dir):
                os.makedirs(project_dir)
                
            # إنشاء جميع الملفات المطلوبة
            self._create_project_files(project_dir, ip, port)
            
            self.log_message("✅ تم إنشاء ملفات المشروع")
            self.log_message("🔨 بدء بناء ملف APK...")
            
            # بناء APK
            apk_path = self._build_apk(project_dir)
            
            if apk_path:
                self.log_message("✅ تم إنشاء ملف APK بنجاح!")
                self.log_message(f"📱 موقع ملف APK: {apk_path}")
                self.log_message("📲 يمكنك الآن تثبيت التطبيق على جهاز Android")
            else:
                self.log_message("❌ فشل في بناء ملف APK")
                self.log_message("📁 تم إنشاء ملفات المشروع في: " + os.path.abspath(project_dir))
                self.log_message("💡 يمكنك فتح المشروع في Android Studio لبناء APK يدوياً")
            
        except ValueError:
            self.log_message("❌ خطأ: تأكد من إدخال رقم صحيح للمنفذ")
        except Exception as e:
            self.log_message(f"❌ خطأ في إنشاء التطبيق: {str(e)}")
            
    def _create_project_files(self, project_dir: str, ip: str, port: int):
        """إنشاء جميع ملفات المشروع"""
        self._create_main_activity(project_dir, ip, port)
        self._create_manifest(project_dir)
        self._create_strings_xml(project_dir)
        self._create_layout_xml(project_dir)
        self._create_gradle_wrapper(project_dir)
        self._create_settings_gradle(project_dir)
        self._create_gradle_properties(project_dir)
        self._create_root_build_gradle(project_dir)
        self._create_app_build_gradle(project_dir)
        
    def _create_main_activity(self, project_dir: str, ip: str, port: int):
        """إنشاء ملف MainActivity.java"""
        java_dir = os.path.join(project_dir, "app", "src", "main", "java", "com", "example", "clientapp")
        os.makedirs(java_dir, exist_ok=True)
        
        java_content = f'''package com.example.clientapp;

import android.app.Activity;
import android.os.Bundle;
import android.os.AsyncTask;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;
import android.content.Context;
import android.telephony.TelephonyManager;
import android.os.Build;
import android.provider.Settings;
import android.content.pm.PackageManager;
import android.Manifest;
import android.content.Intent;
import android.net.Uri;
import android.media.MediaPlayer;
import android.media.AudioManager;
import android.os.Vibrator;
import android.app.NotificationManager;
import android.app.NotificationChannel;
import android.app.Notification;
import android.graphics.Color;
import java.io.*;
import java.net.*;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

public class MainActivity extends Activity {{
    private EditText messageEditText;
    private TextView responseTextView;
    private Button sendButton;
    private TextView deviceInfoTextView;
    private static final String SERVER_IP = "{ip}";
    private static final int SERVER_PORT = {port};
    private Socket clientSocket;
    private PrintWriter out;
    private BufferedReader in;
    private ScheduledExecutorService executor;
    private boolean isConnected = false;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {{
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        
        messageEditText = findViewById(R.id.messageEditText);
        responseTextView = findViewById(R.id.responseTextView);
        sendButton = findViewById(R.id.sendButton);
        deviceInfoTextView = findViewById(R.id.deviceInfoTextView);
        
        // عرض معلومات الجهاز
        displayDeviceInfo();
        
        // الاتصال التلقائي بالخادم
        connectToServer();
        
        sendButton.setOnClickListener(v -> {{
            String message = messageEditText.getText().toString();
            if (!message.isEmpty()) {{
                new SendMessageTask().execute(message);
            }} else {{
                Toast.makeText(this, "يرجى إدخال رسالة", Toast.LENGTH_SHORT).show();
            }}
        }});
    }}
    
    private void displayDeviceInfo() {{
        TelephonyManager tm = (TelephonyManager) getSystemService(Context.TELEPHONY_SERVICE);
        String deviceInfo = "معلومات الجهاز:\\n";
        deviceInfo += "النموذج: " + Build.MODEL + "\\n";
        deviceInfo += "الشركة: " + Build.MANUFACTURER + "\\n";
        deviceInfo += "إصدار Android: " + Build.VERSION.RELEASE + "\\n";
        deviceInfo += "معرف الجهاز: " + Settings.Secure.getString(getContentResolver(), Settings.Secure.ANDROID_ID);
        
        deviceInfoTextView.setText(deviceInfo);
    }}
    
    private void connectToServer() {{
        new Thread(() -> {{
            try {{
                clientSocket = new Socket(SERVER_IP, SERVER_PORT);
                out = new PrintWriter(clientSocket.getOutputStream(), true);
                in = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));
                isConnected = true;
                
                runOnUiThread(() -> {{
                    responseTextView.setText("✅ متصل بالخادم بنجاح!");
                    Toast.makeText(this, "تم الاتصال بالخادم", Toast.LENGTH_SHORT).show();
                }});
                
                // إرسال معلومات الجهاز عند الاتصال
                sendDeviceInfo();
                
                // بدء الاستماع للأوامر
                listenForCommands();
                
            }} catch (Exception e) {{
                runOnUiThread(() -> {{
                    responseTextView.setText("❌ فشل الاتصال: " + e.getMessage());
                }});
            }}
        }}).start();
    }}
    
    private void sendDeviceInfo() {{
        try {{
            String deviceInfo = "DEVICE_INFO:" + Build.MODEL + "|" + Build.MANUFACTURER + "|" + Build.VERSION.RELEASE;
            out.println(deviceInfo);
        }} catch (Exception e) {{
            e.printStackTrace();
        }}
    }}
    
    private void listenForCommands() {{
        new Thread(() -> {{
            try {{
                String command;
                while (isConnected && (command = in.readLine()) != null) {{
                    processCommand(command);
                }}
            }} catch (Exception e) {{
                runOnUiThread(() -> {{
                    responseTextView.setText("❌ انقطع الاتصال: " + e.getMessage());
                }});
                isConnected = false;
            }}
        }}).start();
    }}
    
    private void processCommand(String command) {{
        runOnUiThread(() -> {{
            try {{
                if (command.startsWith("TOAST:")) {{
                    String message = command.substring(6);
                    Toast.makeText(this, message, Toast.LENGTH_LONG).show();
                    out.println("COMMAND_EXECUTED:TOAST");
                    
                }} else if (command.equals("VIBRATE")) {{
                    Vibrator vibrator = (Vibrator) getSystemService(Context.VIBRATOR_SERVICE);
                    if (vibrator != null) {{
                        vibrator.vibrate(1000);
                    }}
                    out.println("COMMAND_EXECUTED:VIBRATE");
                    
                }} else if (command.equals("RINGTONE")) {{
                    playRingtone();
                    out.println("COMMAND_EXECUTED:RINGTONE");
                    
                }} else if (command.startsWith("OPEN_APP:")) {{
                    String packageName = command.substring(9);
                    openApp(packageName);
                    out.println("COMMAND_EXECUTED:OPEN_APP");
                    
                }} else if (command.startsWith("OPEN_URL:")) {{
                    String url = command.substring(9);
                    openUrl(url);
                    out.println("COMMAND_EXECUTED:OPEN_URL");
                    
                }} else if (command.equals("GET_INFO")) {{
                    sendDeviceInfo();
                    
                }} else if (command.equals("SCREEN_ON")) {{
                    // تشغيل الشاشة
                    out.println("COMMAND_EXECUTED:SCREEN_ON");
                    
                }} else if (command.equals("DISCONNECT")) {{
                    disconnect();
                    
                }} else {{
                    // معالجة الأوامر الأخرى
                    responseTextView.setText("📨 أمر مستلم: " + command);
                    out.println("COMMAND_RECEIVED:" + command);
                }}
            }} catch (Exception e) {{
                out.println("COMMAND_ERROR:" + e.getMessage());
            }}
        }});
    }}
    
    private void playRingtone() {{
        try {{
            MediaPlayer mediaPlayer = MediaPlayer.create(this, Settings.System.DEFAULT_RINGTONE_URI);
            mediaPlayer.start();
            mediaPlayer.setOnCompletionListener(MediaPlayer::release);
        }} catch (Exception e) {{
            e.printStackTrace();
        }}
    }}
    
    private void openApp(String packageName) {{
        try {{
            Intent intent = getPackageManager().getLaunchIntentForPackage(packageName);
            if (intent != null) {{
                startActivity(intent);
            }} else {{
                out.println("APP_NOT_FOUND:" + packageName);
            }}
        }} catch (Exception e) {{
            out.println("APP_ERROR:" + e.getMessage());
        }}
    }}
    
    private void openUrl(String url) {{
        try {{
            Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(url));
            startActivity(intent);
        }} catch (Exception e) {{
            out.println("URL_ERROR:" + e.getMessage());
        }}
    }}
    
    private void disconnect() {{
        isConnected = false;
        try {{
            if (out != null) out.close();
            if (in != null) in.close();
            if (clientSocket != null) clientSocket.close();
        }} catch (Exception e) {{
            e.printStackTrace();
        }}
        runOnUiThread(() -> {{
            responseTextView.setText("🔌 تم قطع الاتصال");
        }});
    }}
    
    private class SendMessageTask extends AsyncTask<String, Void, String> {{
        @Override
        protected String doInBackground(String... params) {{
            try {{
                if (isConnected && out != null) {{
                    out.println("MESSAGE:" + params[0]);
                    return "تم إرسال الرسالة";
                }} else {{
                    return "غير متصل بالخادم";
                }}
            }} catch (Exception e) {{
                return "خطأ: " + e.getMessage();
            }}
        }}
        
        @Override
        protected void onPostExecute(String result) {{
            responseTextView.setText("النتيجة: " + result);
        }}
    }}
    
    @Override
    protected void onDestroy() {{
        super.onDestroy();
        disconnect();
    }}
}}'''
        
        with open(os.path.join(java_dir, "MainActivity.java"), "w", encoding="utf-8") as f:
            f.write(java_content)
            
    def _create_manifest(self, project_dir: str):
        """إنشاء ملف AndroidManifest.xml"""
        manifest_dir = os.path.join(project_dir, "app", "src", "main")
        os.makedirs(manifest_dir, exist_ok=True)
        
        manifest_content = '''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.clientapp">
    
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.VIBRATE" />
    <uses-permission android:name="android.permission.WAKE_LOCK" />
    <uses-permission android:name="android.permission.SYSTEM_ALERT_WINDOW" />
    <uses-permission android:name="android.permission.READ_PHONE_STATE" />
    
    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:theme="@android:style/Theme.Material.Light">
        
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:screenOrientation="portrait">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>'''
        
        with open(os.path.join(manifest_dir, "AndroidManifest.xml"), "w", encoding="utf-8") as f:
            f.write(manifest_content)
            
    def _create_strings_xml(self, project_dir: str):
        """إنشاء ملف strings.xml"""
        res_dir = os.path.join(project_dir, "app", "src", "main", "res", "values")
        os.makedirs(res_dir, exist_ok=True)
        
        strings_content = '''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">Remote Control</string>
    <string name="message_hint">أدخل رسالتك هنا</string>
    <string name="send_button">إرسال</string>
</resources>'''
        
        with open(os.path.join(res_dir, "strings.xml"), "w", encoding="utf-8") as f:
            f.write(strings_content)
            
    def _create_layout_xml(self, project_dir: str):
        """إنشاء ملف activity_main.xml"""
        layout_dir = os.path.join(project_dir, "app", "src", "main", "res", "layout")
        os.makedirs(layout_dir, exist_ok=True)
        
        layout_content = '''<?xml version="1.0" encoding="utf-8"?>
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent">
    
    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:padding="16dp">
        
        <TextView
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:text="Remote Control App"
            android:textSize="24sp"
            android:textStyle="bold"
            android:gravity="center"
            android:layout_marginBottom="20dp"
            android:textColor="#2196F3" />
        
        <TextView
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:text="معلومات الجهاز:"
            android:textSize="16sp"
            android:textStyle="bold"
            android:layout_marginBottom="5dp" />
        
        <TextView
            android:id="@+id/deviceInfoTextView"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:background="#e3f2fd"
            android:padding="10dp"
            android:textSize="12sp"
            android:layout_marginBottom="20dp" />
        
        <TextView
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:text="إرسال رسالة:"
            android:textSize="16sp"
            android:textStyle="bold"
            android:layout_marginBottom="5dp" />
        
        <EditText
            android:id="@+id/messageEditText"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:hint="@string/message_hint"
            android:layout_marginBottom="10dp" />
        
        <Button
            android:id="@+id/sendButton"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:text="@string/send_button"
            android:layout_marginBottom="20dp"
            android:background="#4CAF50"
            android:textColor="#FFFFFF" />
        
        <TextView
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:text="حالة الاتصال:"
            android:textSize="16sp"
            android:textStyle="bold"
            android:layout_marginBottom="5dp" />
        
        <TextView
            android:id="@+id/responseTextView"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:background="#f0f0f0"
            android:padding="10dp"
            android:text="جاري الاتصال بالخادم..."
            android:textSize="14sp"
            android:minHeight="100dp" />
        
    </LinearLayout>
    
</ScrollView>'''
        
        with open(os.path.join(layout_dir, "activity_main.xml"), "w", encoding="utf-8") as f:
            f.write(layout_content)
            
    def _create_gradle_wrapper(self, project_dir: str):
        """إنشاء Gradle Wrapper"""
        wrapper_dir = os.path.join(project_dir, "gradle", "wrapper")
        os.makedirs(wrapper_dir, exist_ok=True)
        
        # gradle-wrapper.properties
        wrapper_props = f'''distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\\://services.gradle.org/distributions/gradle-{GRADLE_CONFIG['GRADLE_VERSION']}-bin.zip
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists'''
        
        with open(os.path.join(wrapper_dir, "gradle-wrapper.properties"), "w") as f:
            f.write(wrapper_props)
            
        # gradle-wrapper.jar (نص فارغ - سيتم إنشاؤه بواسطة Gradle)
        with open(os.path.join(wrapper_dir, "gradle-wrapper.jar"), "w") as f:
            f.write("")
            
        # gradlew (لينكس/ماك)
        gradlew_content = '''#!/bin/sh
# Gradle wrapper script'''
        
        with open(os.path.join(project_dir, "gradlew"), "w") as f:
            f.write(gradlew_content)
            
        # gradlew.bat (ويندوز)
        gradlew_bat = '''@rem Gradle wrapper batch file'''
        
        with open(os.path.join(project_dir, "gradlew.bat"), "w") as f:
            f.write(gradlew_bat)
            
    def _create_settings_gradle(self, project_dir: str):
        """إنشاء ملف settings.gradle"""
        settings_content = '''rootProject.name = 'ClientApp'
include ':app'''
        
        with open(os.path.join(project_dir, "settings.gradle"), "w") as f:
            f.write(settings_content)
            
    def _create_gradle_properties(self, project_dir: str):
        """إنشاء ملف gradle.properties"""
        properties_content = '''# Project-wide Gradle settings.
org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
android.enableJetifier=true'''
        
        with open(os.path.join(project_dir, "gradle.properties"), "w") as f:
            f.write(properties_content)
            
    def _create_root_build_gradle(self, project_dir: str):
        """إنشاء ملف build.gradle على مستوى المشروع"""
        root_gradle_content = f'''// Top-level build file where you can add configuration options common to all sub-projects/modules.
buildscript {{
    repositories {{
        google()
        mavenCentral()
    }}
    dependencies {{
        classpath 'com.android.tools.build:gradle:{GRADLE_CONFIG['ANDROID_GRADLE_PLUGIN']}'
    }}
}}

allprojects {{
    repositories {{
        google()
        mavenCentral()
    }}
}}

task clean(type: Delete) {{
    delete rootProject.buildDir
}}'''
        
        with open(os.path.join(project_dir, "build.gradle"), "w") as f:
            f.write(root_gradle_content)
            
    def _create_app_build_gradle(self, project_dir: str):
        """إنشاء ملف build.gradle للتطبيق"""
        app_gradle_content = f'''apply plugin: 'com.android.application'

android {{
    compileSdkVersion {ANDROID_CONFIG['COMPILE_SDK_VERSION']}
    buildToolsVersion "{GRADLE_CONFIG['BUILD_TOOLS_VERSION']}"
    
    defaultConfig {{
        applicationId "{ANDROID_CONFIG['PACKAGE_NAME']}"
        minSdkVersion {ANDROID_CONFIG['MIN_SDK_VERSION']}
        targetSdkVersion {ANDROID_CONFIG['TARGET_SDK_VERSION']}
        versionCode {ANDROID_CONFIG['VERSION_CODE']}
        versionName "{ANDROID_CONFIG['VERSION_NAME']}"
    }}
    
    buildTypes {{
        release {{
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android.txt'), 'proguard-rules.pro'
        }}
    }}
    
    compileOptions {{
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }}
}}

dependencies {{
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.8.0'
}}'''
        
        with open(os.path.join(project_dir, "app", "build.gradle"), "w") as f:
            f.write(app_gradle_content)
            
    def _build_apk(self, project_dir: str) -> Optional[str]:
        """بناء ملف APK"""
        try:
            self.log_message("🔍 البحث عن Android SDK...")
            
            sdk_path = find_android_sdk()
            if not sdk_path:
                self.log_message("❌ لم يتم العثور على Android SDK")
                self.log_message("💡 يرجى تثبيت Android Studio أو Android SDK")
                return None
                
            self.log_message(f"✅ تم العثور على Android SDK في: {sdk_path}")
            
            # البحث عن build-tools
            latest_version = get_latest_build_tools(sdk_path)
            if not latest_version:
                self.log_message("❌ لم يتم العثور على build-tools")
                return None
                
            self.log_message(f"📦 استخدام build-tools version: {latest_version}")
            
            # تحديث build.gradle مع مسار SDK
            self._update_app_build_gradle_with_sdk(project_dir, sdk_path, latest_version)
            
            # محاولة بناء APK باستخدام Gradle
            return self._run_gradle_build(project_dir)
            
        except Exception as e:
            self.log_message(f"❌ خطأ في بناء APK: {str(e)}")
            return None
            
    def _update_app_build_gradle_with_sdk(self, project_dir: str, sdk_path: str, build_tools_version: str):
        """تحديث build.gradle للتطبيق مع مسار SDK"""
        gradle_content = f'''apply plugin: 'com.android.application'

android {{
    compileSdkVersion {ANDROID_CONFIG['COMPILE_SDK_VERSION']}
    buildToolsVersion "{build_tools_version}"
    
    defaultConfig {{
        applicationId "{ANDROID_CONFIG['PACKAGE_NAME']}"
        minSdkVersion {ANDROID_CONFIG['MIN_SDK_VERSION']}
        targetSdkVersion {ANDROID_CONFIG['TARGET_SDK_VERSION']}
        versionCode {ANDROID_CONFIG['VERSION_CODE']}
        versionName "{ANDROID_CONFIG['VERSION_NAME']}"
    }}
    
    buildTypes {{
        release {{
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android.txt'), 'proguard-rules.pro'
        }}
    }}
    
    compileOptions {{
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }}
}}

dependencies {{
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.8.0'
}}'''
        
        with open(os.path.join(project_dir, "app", "build.gradle"), "w") as f:
            f.write(gradle_content)
            
    def _run_gradle_build(self, project_dir: str) -> Optional[str]:
        """تشغيل Gradle لبناء APK"""
        try:
            self.log_message("🚀 بدء عملية البناء...")
            
            # تغيير المجلد إلى مجلد المشروع
            original_dir = os.getcwd()
            os.chdir(project_dir)
            
            try:
                # محاولة استخدام gradlew أولاً، ثم gradle
                gradle_commands = ["./gradlew", "gradlew.bat", "gradle"]
                result = None
                
                for cmd in gradle_commands:
                    try:
                        if cmd in ["./gradlew", "gradlew.bat"] and not os.path.exists(cmd):
                            continue
                            
                        self.log_message(f"🔨 تشغيل: {cmd} assembleDebug")
                        result = subprocess.run(
                            [cmd, "assembleDebug"],
                            capture_output=True,
                            text=True,
                            timeout=300  # 5 دقائق timeout
                        )
                        break
                    except FileNotFoundError:
                        continue
                        
                if result is None:
                    self.log_message("❌ لم يتم العثور على Gradle أو gradlew")
                    return None
                
                if result.returncode == 0:
                    # البحث عن ملف APK
                    apk_path = os.path.join(project_dir, "app", "build", "outputs", "apk", "debug", "app-debug.apk")
                    if os.path.exists(apk_path):
                        return apk_path
                    else:
                        self.log_message("❌ لم يتم العثور على ملف APK في المسار المتوقع")
                        return None
                else:
                    self.log_message(f"❌ فشل في بناء APK: {result.stderr}")
                    return None
                    
            finally:
                os.chdir(original_dir)
                
        except subprocess.TimeoutExpired:
            self.log_message("⏰ انتهت مهلة البناء (5 دقائق)")
            return None
        except FileNotFoundError:
            self.log_message("❌ لم يتم العثور على Gradle")
            self.log_message("💡 يرجى تثبيت Gradle أو استخدام Android Studio")
            return None
        except Exception as e:
            self.log_message(f"❌ خطأ في تشغيل Gradle: {str(e)}")
            return None
            
    def open_apk_folder(self):
        """فتح مجلد APK"""
        try:
            apk_path = os.path.join("android_app", "app", "build", "outputs", "apk", "debug")
            if os.path.exists(apk_path):
                if open_folder(apk_path):
                    self.log_message(f"📁 تم فتح مجلد APK: {apk_path}")
                else:
                    self.log_message("❌ فشل في فتح المجلد")
            else:
                self.log_message("❌ لم يتم العثور على مجلد APK")
                self.log_message("💡 يرجى إنشاء تطبيق Android أولاً")
        except Exception as e:
            self.log_message(f"❌ خطأ في فتح المجلد: {str(e)}")
