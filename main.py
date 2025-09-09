#!/usr/bin/env python3
"""
نظام Android Client & Server
Remote Control System

نقطة البداية الرئيسية للتطبيق
Main entry point for the application
"""

import sys
import os

# إضافة مجلد src إلى مسار Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main_app import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nتم إغلاق التطبيق بواسطة المستخدم")
        sys.exit(0)
    except Exception as e:
        print(f"خطأ في تشغيل التطبيق: {e}")
        sys.exit(1)
