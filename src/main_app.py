"""
التطبيق الرئيسي
Main Application
"""

import tkinter as tk
from tkinter import ttk

from .config import UI_CONFIG
from .android_generator import AndroidAppGenerator
from .server_listener import ServerListener


class MainApplication:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_main_window()
        
    def setup_main_window(self):
        """إعداد النافذة الرئيسية"""
        self.root.title("نظام Android Client & Server")
        self.root.geometry(f"{UI_CONFIG['WINDOW_WIDTH']}x{UI_CONFIG['WINDOW_HEIGHT']}")
        self.root.configure(bg="#f0f0f0")
        
        # العنوان الرئيسي
        title_frame = ttk.Frame(self.root)
        title_frame.pack(pady=20)
        
        main_title = ttk.Label(title_frame, text="نظام Android Client & Server", 
                              font=(UI_CONFIG['FONT_FAMILY'], 20, "bold"))
        main_title.pack()
        
        subtitle = ttk.Label(title_frame, text="أداة لإنشاء تطبيقات Android والاستماع للاتصالات", 
                            font=(UI_CONFIG['FONT_FAMILY'], UI_CONFIG['FONT_SIZE']))
        subtitle.pack()
        
        # أزرار الانتقال
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=30)
        
        android_btn = ttk.Button(button_frame, text="مولد تطبيق Android", 
                                command=self.open_android_generator,
                                style="Accent.TButton")
        android_btn.pack(side="left", padx=20)
        
        server_btn = ttk.Button(button_frame, text="خادم الاستماع", 
                               command=self.open_server_listener,
                               style="Accent.TButton")
        server_btn.pack(side="left", padx=20)
        
        # معلومات إضافية
        info_frame = ttk.LabelFrame(self.root, text="معلومات", padding=15)
        info_frame.pack(pady=20, padx=20, fill="x")
        
        info_text = """
• مولد تطبيق Android: ينشئ تطبيق Android جاهز للاتصال بالخادم
• خادم الاستماع: يستمع للاتصالات الواردة من التطبيقات
• يمكنك اختبار النظام بإنشاء تطبيق والاتصال به من الخادم
• التطبيق يتصل تلقائياً بالخادم عند فتحه على الهاتف
• يمكن التحكم في الهاتف من الكمبيوتر مباشرة
        """
        
        info_label = ttk.Label(info_frame, text=info_text, justify="left")
        info_label.pack()
        
        # إطار الإحصائيات
        stats_frame = ttk.LabelFrame(self.root, text="إحصائيات", padding=15)
        stats_frame.pack(pady=10, padx=20, fill="x")
        
        self.stats_label = ttk.Label(stats_frame, text="عدد الأجهزة المتصلة: 0")
        self.stats_label.pack()
        
        # إطار الحالة
        status_frame = ttk.Frame(self.root)
        status_frame.pack(pady=10, padx=20, fill="x")
        
        self.status_label = ttk.Label(status_frame, text="جاهز للاستخدام", 
                                     font=(UI_CONFIG['FONT_FAMILY'], UI_CONFIG['FONT_SIZE']))
        self.status_label.pack()
        
    def open_android_generator(self):
        """فتح نافذة مولد تطبيق Android"""
        generator_window = tk.Toplevel(self.root)
        generator_window.title("مولد تطبيق Android")
        generator_window.geometry("700x500")
        generator_window.configure(bg="#f0f0f0")
        
        # منع إغلاق النافذة الرئيسية عند إغلاق النافذة الفرعية
        generator_window.transient(self.root)
        generator_window.grab_set()
        
        AndroidAppGenerator(generator_window)
        
    def open_server_listener(self):
        """فتح نافذة خادم الاستماع"""
        server_window = tk.Toplevel(self.root)
        server_window.title("خادم الاستماع")
        server_window.geometry("700x500")
        server_window.configure(bg="#f0f0f0")
        
        # منع إغلاق النافذة الرئيسية عند إغلاق النافذة الفرعية
        server_window.transient(self.root)
        server_window.grab_set()
        
        ServerListener(server_window)
        
    def update_status(self, message: str):
        """تحديث رسالة الحالة"""
        self.status_label.config(text=message)
        
    def update_stats(self, connected_devices: int):
        """تحديث الإحصائيات"""
        self.stats_label.config(text=f"عدد الأجهزة المتصلة: {connected_devices}")
        
    def run(self):
        """تشغيل التطبيق"""
        self.root.mainloop()
        
    def on_closing(self):
        """معالجة إغلاق التطبيق"""
        self.root.quit()
        self.root.destroy()


def main():
    """الدالة الرئيسية لتشغيل التطبيق"""
    app = MainApplication()
    app.root.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.run()


if __name__ == "__main__":
    main()
