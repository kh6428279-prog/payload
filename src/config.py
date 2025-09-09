"""
إعدادات النظام
System Configuration
"""

# إعدادات الشبكة
NETWORK_CONFIG = {
    'DEFAULT_PORT': 4444,
    'DEFAULT_IP': '0.0.0.0',
    'BUFFER_SIZE': 1024,
    'TIMEOUT': 5,
    'MAX_CONNECTIONS': 10
}

# إعدادات Android
ANDROID_CONFIG = {
    'PACKAGE_NAME': 'com.example.clientapp',
    'APP_NAME': 'Remote Control',
    'MIN_SDK_VERSION': 21,
    'TARGET_SDK_VERSION': 33,
    'COMPILE_SDK_VERSION': 33,
    'VERSION_CODE': 1,
    'VERSION_NAME': '1.0'
}

# إعدادات Gradle
GRADLE_CONFIG = {
    'GRADLE_VERSION': '7.5',
    'ANDROID_GRADLE_PLUGIN': '7.4.2',
    'BUILD_TOOLS_VERSION': '33.0.0'
}

# إعدادات الواجهة
UI_CONFIG = {
    'WINDOW_WIDTH': 800,
    'WINDOW_HEIGHT': 600,
    'FONT_FAMILY': 'Arial',
    'FONT_SIZE': 12,
    'TITLE_FONT_SIZE': 16
}

# مسارات Android SDK الشائعة
ANDROID_SDK_PATHS = [
    "~/AppData/Local/Android/Sdk",  # Windows
    "~/Library/Android/sdk",        # macOS
    "~/Android/Sdk",                # Linux
]

# أوامر التحكم المتاحة
AVAILABLE_COMMANDS = {
    'TOAST': 'إرسال رسالة مخصصة',
    'VIBRATE': 'تشغيل اهتزاز',
    'RINGTONE': 'تشغيل رنين',
    'GET_INFO': 'الحصول على معلومات الجهاز',
    'SCREEN_ON': 'تشغيل الشاشة',
    'DISCONNECT': 'قطع الاتصال',
    'OPEN_APP': 'فتح تطبيق',
    'OPEN_URL': 'فتح موقع ويب'
}

# تطبيقات شائعة
COMMON_APPS = {
    'WhatsApp': 'com.whatsapp',
    'Telegram': 'org.telegram.messenger',
    'Facebook': 'com.facebook.katana',
    'Instagram': 'com.instagram.android',
    'YouTube': 'com.google.android.youtube',
    'Chrome': 'com.android.chrome',
    'Gmail': 'com.google.android.gm',
    'Maps': 'com.google.android.apps.maps'
}
