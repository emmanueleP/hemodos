import os
import json
import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from datetime import datetime
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from core.logger import logger
import sqlite3

class ChangePasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cambio Password")
        self.setMinimumWidth(300)
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("È necessario cambiare la password al primo accesso"))
        
        layout.addWidget(QLabel("Nuova Password:"))
        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.new_password)
        
        layout.addWidget(QLabel("Conferma Password:"))
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.confirm_password)
        
        btn = QPushButton("Conferma")
        btn.clicked.connect(self.validate)
        layout.addWidget(btn)
        
    def validate(self):
        if len(self.new_password.text()) < 4:
            QMessageBox.warning(self, "Errore", "La password deve essere di almeno 4 caratteri")
            return
            
        if self.new_password.text() != self.confirm_password.text():
            QMessageBox.warning(self, "Errore", "Le password non coincidono")
            return
            
        self.accept()
        
    def get_password(self):
        return self.new_password.text()

class UserManager:
    def __init__(self):
        self.settings = QSettings('Hemodos', 'DatabaseSettings')
        self.cloud_path = self.settings.value("cloud_path", "")
        self.hemodos_dir = self._get_hemodos_dir()
        self.users_file = None  # Inizializza a None
        self.key_file = None    # Inizializza a None
        
        if self.hemodos_dir:
            self.users_file = os.path.join(self.hemodos_dir, ".hemodos_users")
            self.key_file = os.path.join(self.hemodos_dir, '.hemodos_key')
            self._init_crypto()
        else:
            logger.error("Directory Hemodos non configurata")
        
    def _get_hemodos_dir(self):
        """Ottiene la directory Hemodos nel cloud o nella directory utente"""
        cloud_path = self.settings.value("cloud_path")
        if not cloud_path:
            # Su macOS, usa la directory dell'utente se non è configurato un cloud path
            home = os.path.expanduser("~")
            default_dir = os.path.join(home, "Library", "Application Support", "Hemodos") if os.name == 'posix' else None
            if default_dir:
                os.makedirs(default_dir, exist_ok=True)
                return default_dir
            return None
            
        hemodos_dir = os.path.join(cloud_path, "Hemodos")
        os.makedirs(hemodos_dir, exist_ok=True)
        return hemodos_dir
        
    def _init_crypto(self):
        """Inizializza la crittografia"""
        if not self.key_file:
            logger.error("Key file non configurato")
            return
            
        key_dir = os.path.dirname(self.key_file)
        os.makedirs(key_dir, exist_ok=True)  # Crea directory se non esiste
        
        if not os.path.exists(self.key_file):
            # Genera una nuova chiave master
            master_key = Fernet.generate_key()
            
            # Imposta i permessi corretti per il file su macOS/Linux
            try:
                with open(self.key_file, 'wb') as f:
                    f.write(master_key)
                if os.name == 'posix':  # macOS/Linux
                    os.chmod(self.key_file, 0o600)  # Solo l'utente può leggere/scrivere
            except Exception as e:
                logger.error(f"Errore nella creazione del key file: {str(e)}")
                return
                
            # Inizializza Fernet con la chiave master
            self.fernet = Fernet(master_key)
            
            # Crea l'utente admin di default
            self.create_default_admin()
        else:
            try:
                with open(self.key_file, 'rb') as f:
                    master_key = f.read()
                self.fernet = Fernet(master_key)
            except Exception as e:
                logger.error(f"Errore nel caricamento della chiave: {str(e)}")
        
    def _hash_password(self, password):
        """Genera hash della password usando PBKDF2"""
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.b64encode(kdf.derive(password.encode()))
        return {
            'hash': key.decode(),
            'salt': base64.b64encode(salt).decode()
        }
        
    def _verify_password(self, password, stored_hash, stored_salt):
        """Verifica la password usando PBKDF2"""
        salt = base64.b64decode(stored_salt)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.b64encode(kdf.derive(password.encode()))
        return key.decode() == stored_hash
        
    def _load_users(self):
        """Carica gli utenti dal file crittografato"""
        if not os.path.exists(self.users_file):
            return {}
            
        with open(self.users_file, 'rb') as f:
            encrypted_data = f.read()
            decrypted_data = self.fernet.decrypt(encrypted_data)
            return json.loads(decrypted_data)
            
    def _save_users(self, users_data):
        """Salva gli utenti in modo crittografato"""
        encrypted_data = self.fernet.encrypt(json.dumps(users_data).encode())
        with open(self.users_file, 'wb') as f:
            f.write(encrypted_data)
            
    def register_user(self, username, password, email, is_admin=False):
        """Registra un nuovo utente"""
        users = self._load_users()
        
        if username in users:
            return False
            
        # Usa il metodo _hash_password per la coerenza
        password_data = self._hash_password(password)
        
        users[username] = {
            'password_hash': password_data['hash'],
            'salt': password_data['salt'],
            'email': email,
            'is_admin': is_admin,
            'created_at': datetime.now().isoformat(),
            'last_login': None,
            'password_changed': False,
            'status': 'active'
        }
        
        self._save_users(users)
        return True
        
    def verify_user(self, username, password):
        """Verifica le credenziali dell'utente"""
        try:
            users = self._load_users()
            if username not in users:
                return False
                
            user = users[username]
            return self._verify_password(password, user['password_hash'], user['salt'])
            
        except Exception as e:
            logger.error(f"Errore nella verifica: {str(e)}")
            return False

    def verify_login(self, username, password):
        """Verifica le credenziali dell'utente e gestisce il cambio password se necessario"""
        if not self.users_file or not self.key_file:
            logger.error("File di sistema non configurati correttamente")
            return False
            
        try:
            users = self._load_users()
            if username not in users:
                return False

            user = users[username]
            if not self._verify_password(password, user['password_hash'], user['salt']):
                return False

            # Se la password non è mai stata cambiata, forza il cambio
            if not user.get('password_changed', False):
                dialog = ChangePasswordDialog()
                if dialog.exec_() != QDialog.Accepted:
                    return False
                    
                # Aggiorna la password
                new_password = dialog.get_password()
                password_data = self._hash_password(new_password)
                user['password_hash'] = password_data['hash']
                user['salt'] = password_data['salt']
                user['password_changed'] = True
                self._save_users(users)

            # Aggiorna ultimo accesso
            user['last_login'] = datetime.now().isoformat()
            self._save_users(users)

            # Configura le impostazioni dell'utente
            self.settings.setValue("current_user", username)
            self.settings.setValue("current_user_db", user["database"])
            self.settings.sync()
            return True

        except Exception as e:
            logger.error(f"Errore nella verifica del login: {str(e)}")
            return False

    def is_admin(self, username):
        """Verifica se l'utente è admin"""
        try:
            users = self._load_users()
            return users.get(username, {}).get("is_admin", False)
        except Exception as e:
            logger.error(f"Errore nella verifica dei permessi admin: {str(e)}")
            return False

    def get_user_database(self, username):
        """Ottiene il percorso del database dell'utente"""
        try:
            users = self._load_users()
            return users.get(username, {}).get("database")
        except Exception as e:
            logger.error(f"Errore nel recupero del database utente: {str(e)}")
            return None

    def create_default_admin(self):
        """Crea l'utente admin di default"""
        try:
            if not self.hemodos_dir:
                logger.error("Directory Hemodos non configurata")
                return False

            # Crea la directory per l'admin
            admin_path = os.path.join(self.hemodos_dir, "admin")
            os.makedirs(admin_path, exist_ok=True)

            # Crea l'hash della password temporanea
            password_data = self._hash_password("admin123")  # Password temporanea: admin123
            
            users_data = {
                "admin": {
                    "password_hash": password_data['hash'],
                    "salt": password_data['salt'],
                    "is_admin": True,
                    "database": admin_path,
                    "created_at": datetime.now().isoformat(),
                    "last_login": None,
                    "password_changed": False,
                    "email": "admin@hemodos.local"
                }
            }
            
            # Salva il file degli utenti
            encrypted_data = self.fernet.encrypt(json.dumps(users_data).encode())
            with open(self.users_file, 'wb') as f:
                f.write(encrypted_data)
            return True
                
        except Exception as e:
            logger.error(f"Errore nella creazione dell'admin: {str(e)}")
            return False

    def update_user_password(self, username, new_password):
        """Aggiorna la password di un utente"""
        try:
            users = self._load_users()
            if username not in users:
                return False

            password_data = self._hash_password(new_password)
            users[username]["password_hash"] = password_data['hash']
            users[username]["salt"] = password_data['salt']
            users[username]["password_changed"] = True
            
            self._save_users(users)
            return True
            
        except Exception as e:
            logger.error(f"Errore nell'aggiornamento della password: {str(e)}")
            return False 