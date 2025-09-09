"""
الوظائف المساعدة
Utility Functions
"""

import os
import sys
import subprocess
import socket
from typing import Optional, List


def find_android_sdk() -> Optional[str]:
    """
    البحث عن Android SDK في المسارات الشائعة
    """
    import os.path
    
    # مسارات Android SDK الشائعة
    sdk_paths = [
        os.path.expanduser("~/AppData/Local/Android/Sdk"),  # Windows
        os.path.expanduser("~/Library/Android/sdk"),        # macOS
        os.path.expanduser("~/Android/Sdk"),                # Linux
        os.environ.get("ANDROID_HOME", ""),
        os.environ.get("ANDROID_SDK_ROOT", "")
    ]
    
    for path in sdk_paths:
        if path and os.path.exists(path):
            return path
    
    return None


def get_latest_build_tools(sdk_path: str) -> Optional[str]:
    """
    الحصول على أحدث إصدار من build-tools
    """
    build_tools_dir = os.path.join(sdk_path, "build-tools")
    if not os.path.exists(build_tools_dir):
        return None
    
    try:
        build_tools_versions = [d for d in os.listdir(build_tools_dir) 
                              if os.path.isdir(os.path.join(build_tools_dir, d))]
        if not build_tools_versions:
            return None
        
        return sorted(build_tools_versions)[-1]
    except Exception:
        return None


def test_connection(ip: str, port: int) -> bool:
    """
    اختبار الاتصال بالخادم
    """
    try:
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.settimeout(5)
        result = test_socket.connect_ex((ip, port))
        test_socket.close()
        return result == 0
    except Exception:
        return False


def open_folder(path: str) -> bool:
    """
    فتح مجلد في نظام الملفات
    """
    try:
        if os.name == 'nt':  # Windows
            os.startfile(path)
        elif os.name == 'posix':  # macOS and Linux
            subprocess.run(['open' if sys.platform == 'darwin' else 'xdg-open', path])
        return True
    except Exception:
        return False


def validate_ip(ip: str) -> bool:
    """
    التحقق من صحة عنوان IP
    """
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False


def validate_port(port: str) -> bool:
    """
    التحقق من صحة رقم المنفذ
    """
    try:
        port_num = int(port)
        return 1 <= port_num <= 65535
    except ValueError:
        return False


def get_local_ip() -> str:
    """
    الحصول على IP المحلي للجهاز
    """
    try:
        # إنشاء socket مؤقت للاتصال
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"


def format_device_info(device_info: str) -> str:
    """
    تنسيق معلومات الجهاز للعرض
    """
    if '|' in device_info:
        parts = device_info.split('|')
        if len(parts) >= 3:
            return f"{parts[1]} {parts[0]} (Android {parts[2]})"
    return device_info


def sanitize_filename(filename: str) -> str:
    """
    تنظيف اسم الملف من الأحرف غير المسموحة
    """
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def create_directory_structure(base_path: str, structure: dict) -> None:
    """
    إنشاء هيكل المجلدات
    """
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_directory_structure(path, content)
        else:
            os.makedirs(path, exist_ok=True)


def log_with_timestamp(message: str) -> str:
    """
    إضافة timestamp للرسالة
    """
    from datetime import datetime
    timestamp = datetime.now().strftime("%H:%M:%S")
    return f"[{timestamp}] {message}"
