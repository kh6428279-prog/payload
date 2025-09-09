"""
خادم الاستماع والتحكم
Server Listener and Control
"""

import socket
import threading
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Dict, Any

from .config import NETWORK_CONFIG, AVAILABLE_COMMANDS, COMMON_APPS
from .utils import format_device_info


class ServerListener:
    def __init__(self, parent):
        self.parent = parent
        self.server_socket = None
        self.is_listening = False
        self.connected_devices: Dict[str, Dict[str, Any]] = {}
        self.setup_ui()
        
    def setup_ui(self):
        # إطار العنوان
        title_frame = ttk.Frame(self.parent)
        title_frame.pack(pady=10)
        
        title_label = ttk.Label(title_frame, text="خادم الاستماع", 
                               font=("Arial", 16, "bold"))
        title_label.pack()
        
        # إطار الإدخال
        input_frame = ttk.LabelFrame(self.parent, text="إعدادات الخادم", padding=10)
        input_frame.pack(pady=10, padx=20, fill="x")
        
        # حقل IP
        ttk.Label(input_frame, text="عنوان IP:").grid(row=0, column=0, sticky="w", pady=5)
        self.ip_entry = ttk.Entry(input_frame, width=20)
        self.ip_entry.grid(row=0, column=1, pady=5, padx=(10, 0))
        self.ip_entry.insert(0, NETWORK_CONFIG['DEFAULT_IP'])
        
        # حقل Port
        ttk.Label(input_frame, text="المنفذ (Port):").grid(row=1, column=0, sticky="w", pady=5)
        self.port_entry = ttk.Entry(input_frame, width=20)
        self.port_entry.grid(row=1, column=1, pady=5, padx=(10, 0))
        self.port_entry.insert(0, str(NETWORK_CONFIG['DEFAULT_PORT']))
        
        # أزرار التحكم
        button_frame = ttk.Frame(self.parent)
        button_frame.pack(pady=20)
        
        self.start_button = ttk.Button(button_frame, text="بدء الاستماع", 
                                      command=self.start_listening)
        self.start_button.pack(side="left", padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="إيقاف الاستماع", 
                                     command=self.stop_listening, state="disabled")
        self.stop_button.pack(side="left", padx=5)
        
        # إطار الأجهزة المتصلة
        devices_frame = ttk.LabelFrame(self.parent, text="الأجهزة المتصلة", padding=10)
        devices_frame.pack(pady=10, padx=20, fill="x")
        
        # قائمة الأجهزة
        self.devices_listbox = tk.Listbox(devices_frame, height=3)
        self.devices_listbox.pack(fill="x", pady=5)
        
        # إطار الأوامر
        commands_frame = ttk.LabelFrame(self.parent, text="أوامر التحكم", padding=10)
        commands_frame.pack(pady=10, padx=20, fill="x")
        
        # أزرار الأوامر
        commands_grid = ttk.Frame(commands_frame)
        commands_grid.pack(fill="x")
        
        # الصف الأول
        ttk.Button(commands_grid, text="رسالة مخصصة", 
                  command=self.send_custom_toast).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(commands_grid, text="اهتزاز", 
                  command=lambda: self.send_command("VIBRATE")).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(commands_grid, text="رنين", 
                  command=lambda: self.send_command("RINGTONE")).grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        
        # الصف الثاني
        ttk.Button(commands_grid, text="معلومات الجهاز", 
                  command=lambda: self.send_command("GET_INFO")).grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(commands_grid, text="تشغيل الشاشة", 
                  command=lambda: self.send_command("SCREEN_ON")).grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(commands_grid, text="قطع الاتصال", 
                  command=lambda: self.send_command("DISCONNECT")).grid(row=1, column=2, padx=5, pady=5, sticky="ew")
        
        # إطار الأوامر المخصصة
        custom_frame = ttk.Frame(commands_frame)
        custom_frame.pack(fill="x", pady=10)
        
        ttk.Label(custom_frame, text="أمر مخصص:").pack(side="left")
        self.custom_command_entry = ttk.Entry(custom_frame, width=30)
        self.custom_command_entry.pack(side="left", padx=5)
        ttk.Button(custom_frame, text="إرسال", 
                  command=self.send_custom_command).pack(side="left", padx=5)
        
        # إطار فتح التطبيقات
        apps_frame = ttk.Frame(commands_frame)
        apps_frame.pack(fill="x", pady=5)
        
        ttk.Label(apps_frame, text="فتح تطبيق:").pack(side="left")
        self.app_package_entry = ttk.Entry(apps_frame, width=25)
        self.app_package_entry.pack(side="left", padx=5)
        self.app_package_entry.insert(0, COMMON_APPS['WhatsApp'])
        ttk.Button(apps_frame, text="فتح", 
                  command=self.open_app).pack(side="left", padx=5)
        
        # إطار فتح المواقع
        url_frame = ttk.Frame(commands_frame)
        url_frame.pack(fill="x", pady=5)
        
        ttk.Label(url_frame, text="فتح موقع:").pack(side="left")
        self.url_entry = ttk.Entry(url_frame, width=25)
        self.url_entry.pack(side="left", padx=5)
        self.url_entry.insert(0, "https://www.google.com")
        ttk.Button(url_frame, text="فتح", 
                  command=self.open_url).pack(side="left", padx=5)
        
        # منطقة السجلات
        log_frame = ttk.LabelFrame(self.parent, text="سجل الاتصالات", padding=10)
        log_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        self.log_text = tk.Text(log_frame, height=10, wrap="word")
        log_scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side="left", fill="both", expand=True)
        log_scrollbar.pack(side="right", fill="y")
        
    def log_message(self, message: str):
        """إضافة رسالة إلى منطقة السجلات"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.parent.update()
        
    def start_listening(self):
        """بدء الاستماع على المنفذ"""
        try:
            ip = self.ip_entry.get().strip()
            port = int(self.port_entry.get().strip())
            
            if not ip or not port:
                messagebox.showerror("خطأ", "يرجى إدخال IP والمنفذ")
                return
                
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((ip, port))
            self.server_socket.listen(NETWORK_CONFIG['MAX_CONNECTIONS'])
            
            self.is_listening = True
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            
            self.log_message(f"🚀 بدء الاستماع على {ip}:{port}")
            
            # بدء thread للاستماع
            self.listen_thread = threading.Thread(target=self.listen_for_connections, daemon=True)
            self.listen_thread.start()
            
        except ValueError:
            self.log_message("❌ خطأ: تأكد من إدخال رقم صحيح للمنفذ")
        except Exception as e:
            self.log_message(f"❌ خطأ في بدء الخادم: {str(e)}")
            
    def stop_listening(self):
        """إيقاف الاستماع"""
        self.is_listening = False
        if self.server_socket:
            self.server_socket.close()
            
        # قطع جميع الاتصالات
        for device_id, device_info in list(self.connected_devices.items()):
            try:
                device_info['socket'].close()
            except:
                pass
        self.connected_devices.clear()
        self.update_devices_list()
            
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.log_message("⏹️ تم إيقاف الخادم")
        
    def listen_for_connections(self):
        """الاستماع للاتصالات الواردة"""
        while self.is_listening:
            try:
                client_socket, client_address = self.server_socket.accept()
                self.log_message(f"📱 اتصال جديد من: {client_address[0]}:{client_address[1]}")
                
                # معالجة الاتصال في thread منفصل
                client_thread = threading.Thread(
                    target=self.handle_client, 
                    args=(client_socket, client_address), 
                    daemon=True
                )
                client_thread.start()
                
            except Exception as e:
                if self.is_listening:
                    self.log_message(f"❌ خطأ في قبول الاتصال: {str(e)}")
                    
    def handle_client(self, client_socket: socket.socket, client_address: tuple):
        """معالجة اتصال العميل"""
        device_id = f"{client_address[0]}:{client_address[1]}"
        self.connected_devices[device_id] = {
            'socket': client_socket,
            'address': client_address,
            'info': 'غير معروف'
        }
        
        # تحديث قائمة الأجهزة
        self.update_devices_list()
        
        try:
            while True:
                # قراءة البيانات من العميل
                data = client_socket.recv(NETWORK_CONFIG['BUFFER_SIZE']).decode('utf-8')
                if not data:
                    break
                    
                self.log_message(f"📨 من {client_address[0]}: {data}")
                
                # معالجة أنواع مختلفة من الرسائل
                if data.startswith("DEVICE_INFO:"):
                    device_info = data[12:]  # إزالة "DEVICE_INFO:"
                    self.connected_devices[device_id]['info'] = device_info
                    self.update_devices_list()
                    self.log_message(f"📱 معلومات الجهاز: {format_device_info(device_info)}")
                    
                elif data.startswith("MESSAGE:"):
                    message = data[8:]  # إزالة "MESSAGE:"
                    self.log_message(f"💬 رسالة: {message}")
                    
                elif data.startswith("COMMAND_EXECUTED:"):
                    command = data[17:]  # إزالة "COMMAND_EXECUTED:"
                    self.log_message(f"✅ تم تنفيذ الأمر: {command}")
                    
                elif data.startswith("COMMAND_ERROR:"):
                    error = data[14:]  # إزالة "COMMAND_ERROR:"
                    self.log_message(f"❌ خطأ في الأمر: {error}")
                    
                else:
                    # رسالة عادية
                    response = f"تم استلام رسالتك: {data}"
                    client_socket.send(response.encode('utf-8'))
                    self.log_message(f"📤 تم إرسال الرد: {response}")
                    
        except Exception as e:
            self.log_message(f"❌ خطأ في معالجة العميل {client_address[0]}: {str(e)}")
        finally:
            # إزالة الجهاز من القائمة
            if device_id in self.connected_devices:
                del self.connected_devices[device_id]
                self.update_devices_list()
            client_socket.close()
            self.log_message(f"🔌 تم إغلاق الاتصال مع {client_address[0]}")
            
    def update_devices_list(self):
        """تحديث قائمة الأجهزة المتصلة"""
        self.devices_listbox.delete(0, tk.END)
        for device_id, device_info in self.connected_devices.items():
            display_text = f"{device_id} - {format_device_info(device_info['info'])}"
            self.devices_listbox.insert(tk.END, display_text)
            
    def send_command(self, command: str):
        """إرسال أمر لجميع الأجهزة المتصلة"""
        if not self.connected_devices:
            self.log_message("❌ لا توجد أجهزة متصلة")
            return
            
        for device_id, device_info in self.connected_devices.items():
            try:
                device_info['socket'].send(command.encode('utf-8'))
                self.log_message(f"📤 تم إرسال الأمر '{command}' إلى {device_id}")
            except Exception as e:
                self.log_message(f"❌ فشل إرسال الأمر إلى {device_id}: {str(e)}")
                
    def send_custom_command(self):
        """إرسال أمر مخصص"""
        command = self.custom_command_entry.get().strip()
        if command:
            self.send_command(command)
            self.custom_command_entry.delete(0, tk.END)
        else:
            self.log_message("❌ يرجى إدخال أمر")
            
    def send_custom_toast(self):
        """إرسال رسالة مخصصة كـ Toast"""
        message = simpledialog.askstring("رسالة مخصصة", "أدخل الرسالة:")
        if message:
            command = f"TOAST:{message}"
            self.send_command(command)
            
    def open_app(self):
        """فتح تطبيق على الأجهزة المتصلة"""
        package_name = self.app_package_entry.get().strip()
        if package_name:
            command = f"OPEN_APP:{package_name}"
            self.send_command(command)
        else:
            self.log_message("❌ يرجى إدخال اسم التطبيق")
            
    def open_url(self):
        """فتح موقع على الأجهزة المتصلة"""
        url = self.url_entry.get().strip()
        if url:
            command = f"OPEN_URL:{url}"
            self.send_command(command)
        else:
            self.log_message("❌ يرجى إدخال رابط الموقع")
            
    def get_connected_devices_count(self) -> int:
        """الحصول على عدد الأجهزة المتصلة"""
        return len(self.connected_devices)
        
    def get_device_info(self, device_id: str) -> Dict[str, Any]:
        """الحصول على معلومات جهاز محدد"""
        return self.connected_devices.get(device_id, {})
        
    def disconnect_device(self, device_id: str):
        """قطع الاتصال مع جهاز محدد"""
        if device_id in self.connected_devices:
            try:
                self.connected_devices[device_id]['socket'].close()
                del self.connected_devices[device_id]
                self.update_devices_list()
                self.log_message(f"🔌 تم قطع الاتصال مع {device_id}")
            except Exception as e:
                self.log_message(f"❌ خطأ في قطع الاتصال مع {device_id}: {str(e)}")
