#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
أدوات مساعدة
Helper Utilities
"""

import os
import sys
import socket
import random
import string
import hashlib
import platform
import subprocess
from datetime import datetime
from pathlib import Path

def get_local_ip():
    """الحصول على عنوان IP المحلي"""
    try:
        # إنشاء socket مؤقت للاتصال
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        try:
            # طريقة بديلة
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            return local_ip
        except Exception:
            return "127.0.0.1"

def get_public_ip():
    """الحصول على عنوان IP العام"""
    try:
        import requests
        response = requests.get("https://api.ipify.org", timeout=5)
        return response.text.strip()
    except Exception:
        return None

def generate_random_string(length=16):
    """توليد نص عشوائي"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def generate_session_id():
    """توليد معرف جلسة فريد"""
    timestamp = int(datetime.now().timestamp())
    random_part = generate_random_string(8)
    return f"{timestamp}_{random_part}"

def calculate_file_hash(file_path, algorithm='sha256'):
    """حساب هاش الملف"""
    try:
        hash_obj = hashlib.new(algorithm)
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except Exception:
        return None

def is_port_available(port, host='localhost'):
    """التحقق من توفر المنفذ"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex((host, port))
            return result != 0
    except Exception:
        return False

def find_available_port(start_port=4444, max_port=65535):
    """البحث عن منفذ متاح"""
    for port in range(start_port, max_port + 1):
        if is_port_available(port):
            return port
    return None

def get_system_info():
    """الحصول على معلومات النظام"""
    try:
        info = {
            'platform': platform.platform(),
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'architecture': platform.architecture()[0]
        }
        return info
    except Exception:
        return {}

def check_adb_available():
    """التحقق من توفر ADB"""
    try:
        result = subprocess.run(['adb', 'version'], 
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except Exception:
        return False

def get_connected_devices():
    """الحصول على الأجهزة المتصلة"""
    try:
        if not check_adb_available():
            return []
        
        result = subprocess.run(['adb', 'devices'], 
                              capture_output=True, text=True, timeout=10)
        
        devices = []
        lines = result.stdout.strip().split('\n')[1:]  # تخطي السطر الأول
        
        for line in lines:
            if line.strip() and '\tdevice' in line:
                device_id = line.split('\t')[0]
                devices.append(device_id)
        
        return devices
    except Exception:
        return []

def format_bytes(bytes_value):
    """تنسيق حجم الملف"""
    try:
        bytes_value = int(bytes_value)
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"
    except Exception:
        return "0 B"

def format_duration(seconds):
    """تنسيق المدة الزمنية"""
    try:
        seconds = int(seconds)
        if seconds < 60:
            return f"{seconds} ثانية"
        elif seconds < 3600:
            minutes = seconds // 60
            remaining_seconds = seconds % 60
            return f"{minutes} دقيقة {remaining_seconds} ثانية"
        else:
            hours = seconds // 3600
            remaining_minutes = (seconds % 3600) // 60
            return f"{hours} ساعة {remaining_minutes} دقيقة"
    except Exception:
        return "0 ثانية"

def create_directory(path):
    """إنشاء مجلد"""
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False

def get_file_size(file_path):
    """الحصول على حجم الملف"""
    try:
        return os.path.getsize(file_path)
    except Exception:
        return 0

def is_valid_ip(ip):
    """التحقق من صحة عنوان IP"""
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False

def is_valid_port(port):
    """التحقق من صحة المنفذ"""
    try:
        port = int(port)
        return 1 <= port <= 65535
    except ValueError:
        return False

def sanitize_filename(filename):
    """تنظيف اسم الملف"""
    try:
        # إزالة الأحرف غير المسموحة
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # إزالة المسافات الزائدة
        filename = ' '.join(filename.split())
        
        # تحديد طول الاسم
        if len(filename) > 255:
            filename = filename[:255]
        
        return filename
    except Exception:
        return "unnamed_file"

def get_timestamp():
    """الحصول على الطابع الزمني الحالي"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def parse_timestamp(timestamp_str):
    """تحليل الطابع الزمني"""
    try:
        return datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
    except Exception:
        return None

def is_admin():
    """التحقق من صلاحيات المدير"""
    try:
        if platform.system() == "Windows":
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        else:
            return os.geteuid() == 0
    except Exception:
        return False

def get_network_interfaces():
    """الحصول على واجهات الشبكة"""
    try:
        import netifaces
        interfaces = []
        
        for interface in netifaces.interfaces():
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addrs:
                for addr in addrs[netifaces.AF_INET]:
                    interfaces.append({
                        'name': interface,
                        'ip': addr['addr'],
                        'netmask': addr.get('netmask', ''),
                        'broadcast': addr.get('broadcast', '')
                    })
        
        return interfaces
    except ImportError:
        # fallback method
        try:
            import socket
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            return [{'name': 'default', 'ip': local_ip, 'netmask': '', 'broadcast': ''}]
        except Exception:
            return []
    except Exception:
        return []

def validate_payload_config(config):
    """التحقق من صحة تكوين البايلود"""
    try:
        required_fields = ['name', 'lhost', 'lport']
        
        for field in required_fields:
            if field not in config:
                return False, f"الحقل المطلوب '{field}' مفقود"
        
        if not config['name'] or not isinstance(config['name'], str):
            return False, "اسم البايلود غير صحيح"
        
        if not is_valid_ip(config['lhost']):
            return False, "عنوان IP غير صحيح"
        
        if not is_valid_port(config['lport']):
            return False, "رقم المنفذ غير صحيح"
        
        return True, "التكوين صحيح"
    except Exception as e:
        return False, f"خطأ في التحقق: {e}"

def backup_file(file_path, backup_dir="backups"):
    """إنشاء نسخة احتياطية للملف"""
    try:
        if not os.path.exists(file_path):
            return False
        
        # إنشاء مجلد النسخ الاحتياطية
        create_directory(backup_dir)
        
        # إنشاء اسم النسخة الاحتياطية
        timestamp = get_timestamp()
        filename = os.path.basename(file_path)
        name, ext = os.path.splitext(filename)
        backup_filename = f"{name}_{timestamp}{ext}"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # نسخ الملف
        import shutil
        shutil.copy2(file_path, backup_path)
        
        return backup_path
    except Exception:
        return None

def cleanup_old_files(directory, days=30):
    """تنظيف الملفات القديمة"""
    try:
        if not os.path.exists(directory):
            return 0
        
        cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)
        removed_count = 0
        
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                file_time = os.path.getmtime(file_path)
                if file_time < cutoff_time:
                    os.remove(file_path)
                    removed_count += 1
        
        return removed_count
    except Exception:
        return 0
