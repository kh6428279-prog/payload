#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام السجل المتقدم
Advanced Logging System
"""

import os
import sys
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path

class Logger:
    """كلاس السجل المتقدم"""
    
    def __init__(self, name="AndroidPayloadTool", level=logging.INFO):
        self.name = name
        self.level = level
        self.logger = None
        self.setup_logger()
    
    def setup_logger(self):
        """إعداد نظام السجل"""
        try:
            # إنشاء مجلد السجلات
            logs_dir = Path("logs")
            logs_dir.mkdir(exist_ok=True)
            
            # إنشاء logger
            self.logger = logging.getLogger(self.name)
            self.logger.setLevel(self.level)
            
            # منع تكرار المعالجات
            if self.logger.handlers:
                return
            
            # إنشاء formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            # معالج الملف
            log_file = logs_dir / "app.log"
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=10*1024*1024,  # 10 MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(self.level)
            file_handler.setFormatter(formatter)
            
            # معالج وحدة التحكم
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(formatter)
            
            # إضافة المعالجات
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
            
            # منع انتشار السجلات
            self.logger.propagate = False
            
        except Exception as e:
            print(f"خطأ في إعداد السجل: {e}")
    
    def debug(self, message):
        """تسجيل رسالة debug"""
        if self.logger:
            self.logger.debug(message)
    
    def info(self, message):
        """تسجيل رسالة info"""
        if self.logger:
            self.logger.info(message)
    
    def warning(self, message):
        """تسجيل رسالة warning"""
        if self.logger:
            self.logger.warning(message)
    
    def error(self, message):
        """تسجيل رسالة error"""
        if self.logger:
            self.logger.error(message)
    
    def critical(self, message):
        """تسجيل رسالة critical"""
        if self.logger:
            self.logger.critical(message)
    
    def log_payload_creation(self, payload_name, config):
        """تسجيل إنشاء بايلود"""
        self.info(f"تم إنشاء بايلود جديد: {payload_name}")
        self.debug(f"تكوين البايلود: {config}")
    
    def log_session_connected(self, session_id, ip, port):
        """تسجيل اتصال جلسة"""
        self.info(f"اتصال جلسة جديدة: {session_id} من {ip}:{port}")
    
    def log_session_disconnected(self, session_id):
        """تسجيل انفصال جلسة"""
        self.info(f"انفصال الجلسة: {session_id}")
    
    def log_command_executed(self, session_id, command):
        """تسجيل تنفيذ أمر"""
        self.info(f"تنفيذ أمر في الجلسة {session_id}: {command}")
    
    def log_file_transfer(self, session_id, filename, direction):
        """تسجيل نقل ملف"""
        self.info(f"نقل ملف في الجلسة {session_id}: {filename} ({direction})")
    
    def log_error(self, operation, error):
        """تسجيل خطأ"""
        self.error(f"خطأ في {operation}: {error}")
    
    def log_security_event(self, event_type, details):
        """تسجيل حدث أمني"""
        self.warning(f"حدث أمني - {event_type}: {details}")
    
    def get_log_file_path(self):
        """الحصول على مسار ملف السجل"""
        return str(Path("logs") / "app.log")
    
    def clear_logs(self):
        """مسح السجلات"""
        try:
            log_file = Path("logs") / "app.log"
            if log_file.exists():
                log_file.unlink()
            self.info("تم مسح السجلات")
        except Exception as e:
            self.error(f"خطأ في مسح السجلات: {e}")
    
    def set_level(self, level):
        """تحديد مستوى السجل"""
        try:
            if isinstance(level, str):
                level = getattr(logging, level.upper())
            
            self.level = level
            self.logger.setLevel(level)
            
            # تحديث مستوى معالجات الملف
            for handler in self.logger.handlers:
                if isinstance(handler, logging.handlers.RotatingFileHandler):
                    handler.setLevel(level)
            
        except Exception as e:
            self.error(f"خطأ في تحديد مستوى السجل: {e}")
    
    def get_log_stats(self):
        """الحصول على إحصائيات السجل"""
        try:
            log_file = Path("logs") / "app.log"
            if not log_file.exists():
                return {
                    'file_size': 0,
                    'line_count': 0,
                    'last_modified': None
                }
            
            # حجم الملف
            file_size = log_file.stat().st_size
            
            # عدد الأسطر
            with open(log_file, 'r', encoding='utf-8') as f:
                line_count = sum(1 for line in f)
            
            # آخر تعديل
            last_modified = datetime.fromtimestamp(log_file.stat().st_mtime)
            
            return {
                'file_size': file_size,
                'line_count': line_count,
                'last_modified': last_modified.isoformat()
            }
            
        except Exception as e:
            self.error(f"خطأ في الحصول على إحصائيات السجل: {e}")
            return {
                'file_size': 0,
                'line_count': 0,
                'last_modified': None
            }
    
    def export_logs(self, output_file, start_date=None, end_date=None):
        """تصدير السجلات"""
        try:
            log_file = Path("logs") / "app.log"
            if not log_file.exists():
                return False
            
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # تصفية حسب التاريخ إذا تم تحديده
            if start_date or end_date:
                filtered_lines = []
                for line in lines:
                    try:
                        # استخراج التاريخ من السطر
                        timestamp_str = line.split(' - ')[0]
                        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                        
                        # التحقق من التاريخ
                        if start_date and timestamp < start_date:
                            continue
                        if end_date and timestamp > end_date:
                            continue
                        
                        filtered_lines.append(line)
                    except:
                        # إذا فشل تحليل التاريخ، أضف السطر كما هو
                        filtered_lines.append(line)
                
                lines = filtered_lines
            
            # كتابة السجلات المفلترة
            with open(output_file, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            self.info(f"تم تصدير السجلات إلى: {output_file}")
            return True
            
        except Exception as e:
            self.error(f"خطأ في تصدير السجلات: {e}")
            return False
