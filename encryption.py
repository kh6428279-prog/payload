#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مدير التشفير المتقدم
Advanced Encryption Manager
"""

import os
import json
import base64
import hashlib
from datetime import datetime
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from utils.logger import Logger

class EncryptionManager:
    """كلاس إدارة التشفير"""
    
    def __init__(self):
        self.logger = Logger()
        self.keys_dir = Path("keys")
        self.keys_dir.mkdir(exist_ok=True)
        self.symmetric_key = None
        self.public_key = None
        self.private_key = None
        self.load_keys()
    
    def generate_symmetric_key(self):
        """توليد مفتاح تشفير متماثل"""
        try:
            self.symmetric_key = Fernet.generate_key()
            self.save_symmetric_key()
            self.logger.info("تم توليد مفتاح التشفير المتماثل")
            return True
        except Exception as e:
            self.logger.error(f"خطأ في توليد المفتاح المتماثل: {e}")
            return False
    
    def generate_asymmetric_keys(self):
        """توليد مفاتيح التشفير غير المتماثل"""
        try:
            # توليد زوج المفاتيح
            self.private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            self.public_key = self.private_key.public_key()
            
            self.save_asymmetric_keys()
            self.logger.info("تم توليد مفاتيح التشفير غير المتماثل")
            return True
        except Exception as e:
            self.logger.error(f"خطأ في توليد المفاتيح غير المتماثلة: {e}")
            return False
    
    def generate_new_keys(self):
        """توليد مفاتيح جديدة"""
        try:
            # توليد المفتاح المتماثل
            self.generate_symmetric_key()
            
            # توليد المفاتيح غير المتماثلة
            self.generate_asymmetric_keys()
            
            self.logger.info("تم توليد جميع المفاتيح بنجاح")
            return True
        except Exception as e:
            self.logger.error(f"خطأ في توليد المفاتيح: {e}")
            return False
    
    def save_symmetric_key(self):
        """حفظ المفتاح المتماثل"""
        try:
            if self.symmetric_key:
                key_file = self.keys_dir / "symmetric.key"
                with open(key_file, 'wb') as f:
                    f.write(self.symmetric_key)
                self.logger.info("تم حفظ المفتاح المتماثل")
        except Exception as e:
            self.logger.error(f"خطأ في حفظ المفتاح المتماثل: {e}")
    
    def save_asymmetric_keys(self):
        """حفظ المفاتيح غير المتماثلة"""
        try:
            if self.private_key and self.public_key:
                # حفظ المفتاح الخاص
                private_file = self.keys_dir / "private.pem"
                with open(private_file, 'wb') as f:
                    f.write(self.private_key.private_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PrivateFormat.PKCS8,
                        encryption_algorithm=serialization.NoEncryption()
                    ))
                
                # حفظ المفتاح العام
                public_file = self.keys_dir / "public.pem"
                with open(public_file, 'wb') as f:
                    f.write(self.public_key.public_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PublicFormat.SubjectPublicKeyInfo
                    ))
                
                self.logger.info("تم حفظ المفاتيح غير المتماثلة")
        except Exception as e:
            self.logger.error(f"خطأ في حفظ المفاتيح غير المتماثلة: {e}")
    
    def load_keys(self):
        """تحميل المفاتيح المحفوظة"""
        try:
            # تحميل المفتاح المتماثل
            symmetric_file = self.keys_dir / "symmetric.key"
            if symmetric_file.exists():
                with open(symmetric_file, 'rb') as f:
                    self.symmetric_key = f.read()
            
            # تحميل المفتاح الخاص
            private_file = self.keys_dir / "private.pem"
            if private_file.exists():
                with open(private_file, 'rb') as f:
                    self.private_key = serialization.load_pem_private_key(
                        f.read(),
                        password=None
                    )
            
            # تحميل المفتاح العام
            public_file = self.keys_dir / "public.pem"
            if public_file.exists():
                with open(public_file, 'rb') as f:
                    self.public_key = serialization.load_pem_public_key(f.read())
            
            self.logger.info("تم تحميل المفاتيح المحفوظة")
        except Exception as e:
            self.logger.error(f"خطأ في تحميل المفاتيح: {e}")
    
    def get_keys(self):
        """الحصول على المفاتيح"""
        return {
            'symmetric_key': base64.b64encode(self.symmetric_key).decode() if self.symmetric_key else None,
            'public_key': base64.b64encode(self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )).decode() if self.public_key else None,
            'private_key': base64.b64encode(self.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )).decode() if self.private_key else None
        }
    
    def encrypt_symmetric(self, data):
        """تشفير البيانات بالمفتاح المتماثل"""
        try:
            if not self.symmetric_key:
                self.generate_symmetric_key()
            
            fernet = Fernet(self.symmetric_key)
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            encrypted_data = fernet.encrypt(data)
            return base64.b64encode(encrypted_data).decode()
        except Exception as e:
            self.logger.error(f"خطأ في التشفير المتماثل: {e}")
            return None
    
    def decrypt_symmetric(self, encrypted_data):
        """فك تشفير البيانات بالمفتاح المتماثل"""
        try:
            if not self.symmetric_key:
                self.logger.error("المفتاح المتماثل غير موجود")
                return None
            
            fernet = Fernet(self.symmetric_key)
            encrypted_bytes = base64.b64decode(encrypted_data)
            decrypted_data = fernet.decrypt(encrypted_bytes)
            return decrypted_data.decode('utf-8')
        except Exception as e:
            self.logger.error(f"خطأ في فك التشفير المتماثل: {e}")
            return None
    
    def encrypt_asymmetric(self, data, public_key=None):
        """تشفير البيانات بالمفتاح العام"""
        try:
            key = public_key or self.public_key
            if not key:
                self.logger.error("المفتاح العام غير موجود")
                return None
            
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            encrypted_data = key.encrypt(
                data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return base64.b64encode(encrypted_data).decode()
        except Exception as e:
            self.logger.error(f"خطأ في التشفير غير المتماثل: {e}")
            return None
    
    def decrypt_asymmetric(self, encrypted_data):
        """فك تشفير البيانات بالمفتاح الخاص"""
        try:
            if not self.private_key:
                self.logger.error("المفتاح الخاص غير موجود")
                return None
            
            encrypted_bytes = base64.b64decode(encrypted_data)
            decrypted_data = self.private_key.decrypt(
                encrypted_bytes,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return decrypted_data.decode('utf-8')
        except Exception as e:
            self.logger.error(f"خطأ في فك التشفير غير المتماثل: {e}")
            return None
    
    def generate_password_hash(self, password, salt=None):
        """توليد هاش كلمة المرور"""
        try:
            if salt is None:
                salt = os.urandom(32)
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            return {
                'hash': key.decode(),
                'salt': base64.b64encode(salt).decode()
            }
        except Exception as e:
            self.logger.error(f"خطأ في توليد هاش كلمة المرور: {e}")
            return None
    
    def verify_password(self, password, password_hash, salt):
        """التحقق من كلمة المرور"""
        try:
            salt_bytes = base64.b64decode(salt)
            hash_data = self.generate_password_hash(password, salt_bytes)
            return hash_data['hash'] == password_hash
        except Exception as e:
            self.logger.error(f"خطأ في التحقق من كلمة المرور: {e}")
            return False
    
    def encrypt_file(self, file_path, output_path=None):
        """تشفير ملف"""
        try:
            if not output_path:
                output_path = file_path + ".encrypted"
            
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            encrypted_data = self.encrypt_symmetric(file_data)
            if encrypted_data:
                with open(output_path, 'w') as f:
                    f.write(encrypted_data)
                self.logger.info(f"تم تشفير الملف: {file_path}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"خطأ في تشفير الملف: {e}")
            return False
    
    def decrypt_file(self, file_path, output_path=None):
        """فك تشفير ملف"""
        try:
            if not output_path:
                output_path = file_path.replace(".encrypted", "")
            
            with open(file_path, 'r') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.decrypt_symmetric(encrypted_data)
            if decrypted_data:
                with open(output_path, 'wb') as f:
                    f.write(decrypted_data.encode('utf-8'))
                self.logger.info(f"تم فك تشفير الملف: {file_path}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"خطأ في فك تشفير الملف: {e}")
            return False
    
    def export_keys(self, output_file=None):
        """تصدير المفاتيح"""
        try:
            if not output_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"keys_export_{timestamp}.json"
            
            keys_data = {
                'symmetric_key': base64.b64encode(self.symmetric_key).decode() if self.symmetric_key else None,
                'public_key': base64.b64encode(self.public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )).decode() if self.public_key else None,
                'private_key': base64.b64encode(self.private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )).decode() if self.private_key else None,
                'exported_at': datetime.now().isoformat()
            }
            
            with open(output_file, 'w') as f:
                json.dump(keys_data, f, indent=2)
            
            self.logger.info(f"تم تصدير المفاتيح إلى: {output_file}")
            return True
        except Exception as e:
            self.logger.error(f"خطأ في تصدير المفاتيح: {e}")
            return False
    
    def import_keys(self, input_file):
        """استيراد المفاتيح"""
        try:
            with open(input_file, 'r') as f:
                keys_data = json.load(f)
            
            # استيراد المفتاح المتماثل
            if keys_data.get('symmetric_key'):
                self.symmetric_key = base64.b64decode(keys_data['symmetric_key'])
            
            # استيراد المفتاح العام
            if keys_data.get('public_key'):
                public_key_bytes = base64.b64decode(keys_data['public_key'])
                self.public_key = serialization.load_pem_public_key(public_key_bytes)
            
            # استيراد المفتاح الخاص
            if keys_data.get('private_key'):
                private_key_bytes = base64.b64decode(keys_data['private_key'])
                self.private_key = serialization.load_pem_private_key(
                    private_key_bytes,
                    password=None
                )
            
            # حفظ المفاتيح
            self.save_symmetric_key()
            self.save_asymmetric_keys()
            
            self.logger.info(f"تم استيراد المفاتيح من: {input_file}")
            return True
        except Exception as e:
            self.logger.error(f"خطأ في استيراد المفاتيح: {e}")
            return False
