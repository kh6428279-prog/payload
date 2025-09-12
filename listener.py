import socket
import threading
import json
import time
import datetime
from collections import defaultdict
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import select
import os
from cryptography.fernet import Fernet

class AdvancedListener:
    def __init__(self):
        self.is_listening = False
        self.clients = {}
        self.sessions = defaultdict(list)
        self.current_session = None
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)
        
        # إنشاء النافذة الرئيسية
        self.root = tk.Tk()
        self.root.title("نظام الاستماع المتقدم - Advanced Listener")
        self.root.geometry("900x700")
        
        self.setup_ui()
        
    def setup_ui(self):
        # إطار الإعدادات
        settings_frame = ttk.LabelFrame(self.root, text="إعدادات الاتصال", padding=10)
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
        stats_frame = ttk.LabelFrame(self.root, text="الإحصائيات", padding=10)
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
        sessions_frame = ttk.LabelFrame(self.root, text="الجلسات النشطة", padding=10)
        sessions_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.sessions_tree = ttk.Treeview(sessions_frame, columns=("id", "address", "start_time", "packets"), height=5)
        self.sessions_tree.heading("#0", text="م")
        self.sessions_tree.heading("id", text="معرف الجلسة")
        self.sessions_tree.heading("address", text="العنوان")
        self.sessions_tree.heading("start_time", text="وقت البدء")
        self.sessions_tree.heading("packets", text="عدد الحزم")
        
        self.sessions_tree.column("#0", width=50)
        self.sessions_tree.column("id", width=150)
        self.sessions_tree.column("address", width=200)
        self.sessions_tree.column("start_time", width=150)
        self.sessions_tree.column("packets", width=100)
        
        self.sessions_tree.pack(fill=tk.X)
        
        # إطار البيانات
        data_frame = ttk.LabelFrame(self.root, text="البيانات المستلمة", padding=10)
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
        control_frame = ttk.LabelFrame(self.root, text="خيارات متقدمة", padding=10)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(control_frame, text="الرد التلقائي:").grid(row=0, column=0, padx=5, pady=2)
        self.auto_reply_entry = ttk.Entry(control_frame, width=30)
        self.auto_reply_entry.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Checkbutton(control_frame, text="تمكين الرد التلقائي").grid(row=0, column=2, padx=5, pady=2)
        ttk.Checkbutton(control_frame, text="تسجيل جميع البيانات").grid(row=0, column=3, padx=5, pady=2)
        ttk.Checkbutton(control_frame, text="تشفير السجلات").grid(row=0, column=4, padx=5, pady=2)
        
        # إعدادات المتغيرات
        self.connection_count = 0
        self.packet_count = 0
        self.data_received = 0
        self.session_counter = 0
        
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
                                 values=(session_id, f"{addr[0]}:{addr[1]}", start_time, "0"))
        
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
        
        while self.is_listening:
            try:
                data = client_socket.recv(4096)
                if not data:
                    break
                
                self.packet_count += 1
                self.data_received += len(data)
                self.update_stats()
                
                # تحديث عدد الحزم في الجلسة
                for item in self.sessions_tree.get_children():
                    if self.sessions_tree.item(item, "values")[0] == session_id:
                        current_packets = int(self.sessions_tree.item(item, "values")[3])
                        self.sessions_tree.item(item, values=(
                            self.sessions_tree.item(item, "values")[0],
                            self.sessions_tree.item(item, "values")[1],
                            self.sessions_tree.item(item, "values")[2],
                            str(current_packets + 1)
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
                
                # إمكانية إرسال رد تلقائي
                # if auto_reply_enabled:
                #     client_socket.send(auto_reply_message.encode())
                    
            except socket.timeout:
                continue
            except:
                break
        
        client_socket.close()
        self.connection_count -= 1
        self.connections_label.config(text=str(self.connection_count))
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
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = AdvancedListener()
    app.run()