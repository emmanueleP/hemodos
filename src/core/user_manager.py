import os
import json
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from datetime import datetime

class UserManager:
    def __init__(self):
        self.settings = QSettings('Hemodos', 'DatabaseSettings')
        self.key_file = os.path.join(self._get_hemodos_dir(), '.hemodos_key')
        self.users_file = os.path.join(self._get_hemodos_dir(), '.users.enc')
        self._init_crypto()
        
    def _get_hemodos_dir(self):
        """Ottiene la directory Hemodos nel cloud"""
        cloud_path = self.settings.value("cloud_path")
        hemodos_dir = os.path.join(cloud_path, "Hemodos")
        os.makedirs(hemodos_dir, exist_ok=True)
        return hemodos_dir
        
    def _init_crypto(self):
        """Inizializza la crittografia"""
        if not os.path.exists(self.key_file):
            # Genera una nuova chiave master
            master_key = Fernet.generate_key()
            
            # Salva la chiave crittografata
            with open(self.key_file, 'wb') as f:
                f.write(master_key)
            
            # Crea l'utente admin di default
            self.register_user(
                "admin",
                "admin123",  # Password temporanea da cambiare al primo accesso
                "admin@hemodos.local",
                is_admin=True
            )
            
        self.fernet = Fernet(open(self.key_file, 'rb').read())
        
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
            
        # Genera salt e hash della password
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.b64encode(kdf.derive(password.encode()))
        
        users[username] = {
            'password_hash': key.decode(),
            'salt': base64.b64encode(salt).decode(),
            'email': email,
            'is_admin': is_admin,
            'created_at': datetime.now().isoformat(),
            'last_login': None,
            'status': 'active'
        }
        
        self._save_users(users)
        return True
        
    def verify_password(self, stored_hash, password):
        """Verifica la password"""
        salt = stored_hash[:32]
        key = stored_hash[32:]
        new_key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000
        )
        return key == new_key
        
    def verify_user(self, username, password):
        """Verifica le credenziali dell'utente"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute("SELECT password_hash FROM users WHERE username=?", (username,))
            result = c.fetchone()
            
            if result and self.verify_password(result[0], password):
                # Aggiorna ultimo accesso
                c.execute("""
                    UPDATE users 
                    SET last_login = ? 
                    WHERE username = ?
                """, (datetime.now(), username))
                conn.commit()
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Errore nella verifica: {str(e)}")
            return False
        finally:
            conn.close() 