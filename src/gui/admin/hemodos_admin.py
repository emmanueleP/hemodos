from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                            QLabel, QLineEdit, QMessageBox, QTableWidget,
                            QTableWidgetItem, QHeaderView, QFileDialog, QFormLayout)
from PyQt5.QtCore import Qt, QSettings
import os
import json
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from datetime import datetime
from core.logger import logger

class HemodosAdmin(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("HemodosAdmin - Gestione Utenti")
        self.settings = QSettings('Hemodos', 'DatabaseSettings')
        self.cloud_path = self.settings.value("cloud_path", "")
        self.hemodos_dir = os.path.join(self.cloud_path, "Hemodos")
        self.key_file = os.path.join(self.hemodos_dir, '.hemodos_key')
        self.users_file = os.path.join(self.hemodos_dir, '.users.enc')
        
        # Assicurati che la directory esista
        if not os.path.exists(self.hemodos_dir):
            os.makedirs(self.hemodos_dir, exist_ok=True)
            logger.info(f"Creata directory Hemodos: {self.hemodos_dir}")
            
        self._init_crypto()
        self.init_ui()
        self.load_users()
        
        # Migra i vecchi utenti se necessario
        self._migrate_old_users()

    def _init_crypto(self):
        """Inizializza la crittografia"""
        try:
            if not os.path.exists(self.key_file):
                # Genera una nuova chiave master
                master_key = Fernet.generate_key()
                
                # Salva la chiave
                with open(self.key_file, 'wb') as f:
                    f.write(master_key)
                
                # Crea l'utente admin di default se non esiste
                self._create_default_admin()
                
            self.fernet = Fernet(open(self.key_file, 'rb').read())
            
        except Exception as e:
            logger.error(f"Errore nell'inizializzazione della crittografia: {str(e)}")
            QMessageBox.critical(self, "Errore", f"Errore nell'inizializzazione della crittografia: {str(e)}")

    def _create_default_admin(self):
        """Crea l'utente admin di default"""
        self.register_user(
            "admin",
            "admin123",  # Password temporanea da cambiare al primo accesso
            is_admin=True
        )

    def _migrate_old_users(self):
        """Migra gli utenti dal vecchio sistema"""
        old_users_file = os.path.join(self.cloud_path, ".hemodos_users")
        if os.path.exists(old_users_file):
            try:
                with open(old_users_file, 'r') as f:
                    old_users = json.load(f)
                
                users = self._load_users()
                migrated = False
                
                for username, data in old_users.items():
                    if username not in users:
                        # Crea un nuovo utente nel nuovo sistema
                        self.register_user(
                            username,
                            "hemodos123",  # Password temporanea
                            is_admin=data.get('is_admin', False)
                        )
                        migrated = True
                
                if migrated:
                    QMessageBox.information(
                        self,
                        "Migrazione Completata",
                        "Gli utenti sono stati migrati al nuovo sistema.\nLe password sono state reimpostate a: hemodos123"
                    )
                    
                # Rinomina il vecchio file
                os.rename(old_users_file, old_users_file + ".bak")
                
            except Exception as e:
                logger.error(f"Errore nella migrazione degli utenti: {str(e)}")

    def init_ui(self):
        layout = QVBoxLayout()

        # Form per aggiungere utenti
        form_layout = QHBoxLayout()
        
        # Username
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        form_layout.addWidget(self.username_input)
        
        # Password
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addWidget(self.password_input)
        
        # Pulsante aggiungi
        add_button = QPushButton("Aggiungi Utente")
        add_button.clicked.connect(self.add_user)
        form_layout.addWidget(add_button)
        
        layout.addLayout(form_layout)

        # Tabella utenti
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(5)
        self.users_table.setHorizontalHeaderLabels(["Username", "Admin", "Ultimo Accesso", "Modifica", "Elimina"])
        header = self.users_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        layout.addWidget(self.users_table)

        # Pulsanti
        buttons_layout = QHBoxLayout()
        close_button = QPushButton("Chiudi")
        close_button.clicked.connect(self.accept)
        buttons_layout.addWidget(close_button)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def _load_users(self):
        """Carica gli utenti dal file crittografato"""
        try:
            if not os.path.exists(self.users_file):
                return {}
                
            with open(self.users_file, 'rb') as f:
                encrypted_data = f.read()
                decrypted_data = self.fernet.decrypt(encrypted_data)
                return json.loads(decrypted_data)
        except Exception as e:
            logger.error(f"Errore nel caricamento degli utenti: {str(e)}")
            return {}

    def _save_users(self, users_data):
        """Salva gli utenti in modo crittografato"""
        try:
            encrypted_data = self.fernet.encrypt(json.dumps(users_data).encode())
            with open(self.users_file, 'wb') as f:
                f.write(encrypted_data)
        except Exception as e:
            logger.error(f"Errore nel salvataggio degli utenti: {str(e)}")
            raise

    def load_users(self):
        """Carica gli utenti nella tabella"""
        try:
            users = self._load_users()
            
            self.users_table.setRowCount(0)
            for username, data in users.items():
                row = self.users_table.rowCount()
                self.users_table.insertRow(row)
                
                # Username
                self.users_table.setItem(row, 0, QTableWidgetItem(username))
                
                # Admin
                is_admin = data.get('is_admin', False)
                admin_item = QTableWidgetItem()
                admin_item.setCheckState(Qt.Checked if is_admin else Qt.Unchecked)
                self.users_table.setItem(row, 1, admin_item)
                
                # Ultimo accesso
                last_login = data.get('last_login', 'Mai')
                if last_login:
                    try:
                        last_login = datetime.fromisoformat(last_login).strftime("%d/%m/%Y %H:%M")
                    except:
                        pass
                self.users_table.setItem(row, 2, QTableWidgetItem(str(last_login)))
                
                # Pulsante modifica
                edit_button = QPushButton("Modifica")
                edit_button.clicked.connect(lambda checked, u=username: self.edit_user(u))
                self.users_table.setCellWidget(row, 3, edit_button)
                
                # Pulsante elimina
                delete_button = QPushButton("Elimina")
                delete_button.clicked.connect(lambda checked, u=username: self.delete_user(u))
                self.users_table.setCellWidget(row, 4, delete_button)

        except Exception as e:
            logger.error(f"Errore nel caricamento degli utenti: {str(e)}")
            QMessageBox.critical(self, "Errore", f"Errore nel caricamento degli utenti: {str(e)}")

    def register_user(self, username, password, is_admin=False):
        """Registra un nuovo utente"""
        try:
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
                'is_admin': is_admin,
                'created_at': datetime.now().isoformat(),
                'last_login': None,
                'status': 'active'
            }
            
            self._save_users(users)
            return True
            
        except Exception as e:
            logger.error(f"Errore nella registrazione dell'utente: {str(e)}")
            return False

    def add_user(self):
        """Aggiunge un nuovo utente"""
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Errore", "Inserisci username e password")
            return

        try:
            if self.register_user(username, password):
                # Pulisci i campi
                self.username_input.clear()
                self.password_input.clear()

                # Ricarica la tabella
                self.load_users()

                QMessageBox.information(self, "Successo", "Utente aggiunto con successo")
            else:
                QMessageBox.warning(self, "Errore", "Username già esistente")

        except Exception as e:
            logger.error(f"Errore nell'aggiunta dell'utente: {str(e)}")
            QMessageBox.critical(self, "Errore", f"Errore nell'aggiunta dell'utente: {str(e)}")

    def edit_user(self, username):
        """Modifica username e password dell'utente"""
        try:
            if username == "admin":
                QMessageBox.warning(self, "Attenzione", "Non puoi modificare l'username dell'admin")
                return

            users = self._load_users()
            if username not in users:
                QMessageBox.warning(self, "Errore", "Utente non trovato")
                return

            # Crea il dialog di modifica
            edit_dialog = QDialog(self)
            edit_dialog.setWindowTitle(f"Modifica Utente: {username}")
            dialog_layout = QVBoxLayout()

            # Form per la modifica
            form_layout = QFormLayout()

            # Nuovo username
            new_username_input = QLineEdit(username)
            form_layout.addRow("Nuovo Username:", new_username_input)

            # Nuova password
            new_password_input = QLineEdit()
            new_password_input.setEchoMode(QLineEdit.Password)
            new_password_input.setPlaceholderText("Lascia vuoto per non modificare")
            form_layout.addRow("Nuova Password:", new_password_input)

            dialog_layout.addLayout(form_layout)

            # Pulsanti
            buttons_layout = QHBoxLayout()
            save_button = QPushButton("Salva")
            cancel_button = QPushButton("Annulla")
            buttons_layout.addWidget(save_button)
            buttons_layout.addWidget(cancel_button)
            dialog_layout.addLayout(buttons_layout)

            edit_dialog.setLayout(dialog_layout)

            # Connetti i pulsanti
            save_button.clicked.connect(edit_dialog.accept)
            cancel_button.clicked.connect(edit_dialog.reject)

            if edit_dialog.exec_() == QDialog.Accepted:
                new_username = new_username_input.text()
                new_password = new_password_input.text()

                # Se il nuovo username è diverso e non esiste già
                if new_username != username:
                    if new_username in users:
                        QMessageBox.warning(self, "Errore", "Username già esistente")
                        return
                    
                    # Copia i dati dell'utente
                    users[new_username] = users[username].copy()
                    del users[username]
                    
                # Se è stata inserita una nuova password
                if new_password:
                    # Genera nuovo salt e hash
                    salt = os.urandom(16)
                    kdf = PBKDF2HMAC(
                        algorithm=hashes.SHA256(),
                        length=32,
                        salt=salt,
                        iterations=100000,
                    )
                    key = base64.b64encode(kdf.derive(new_password.encode()))
                    
                    users[new_username]['password_hash'] = key.decode()
                    users[new_username]['salt'] = base64.b64encode(salt).decode()

                # Salva le modifiche
                self._save_users(users)

                # Ricarica la tabella
                self.load_users()
                QMessageBox.information(self, "Successo", "Utente modificato con successo")

        except Exception as e:
            logger.error(f"Errore nella modifica dell'utente: {str(e)}")
            QMessageBox.critical(self, "Errore", f"Errore nella modifica dell'utente: {str(e)}")

    def delete_user(self, username):
        """Elimina un utente"""
        try:
            if username == "admin":
                QMessageBox.warning(self, "Errore", "Non puoi eliminare l'utente admin")
                return

            reply = QMessageBox.question(
                self, "Conferma",
                f"Sei sicuro di voler eliminare l'utente {username}?",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                users = self._load_users()

                if username in users:
                    # Elimina l'utente
                    del users[username]
                    self._save_users(users)

                    self.load_users()
                    QMessageBox.information(self, "Successo", "Utente eliminato con successo")

        except Exception as e:
            logger.error(f"Errore nell'eliminazione dell'utente: {str(e)}")
            QMessageBox.critical(self, "Errore", f"Errore nell'eliminazione dell'utente: {str(e)}")

    def closeEvent(self, event):
        """Gestisce la chiusura della finestra"""
        try:
            # Salva eventuali modifiche ai permessi admin
            users = self._load_users()

            for row in range(self.users_table.rowCount()):
                username = self.users_table.item(row, 0).text()
                is_admin = self.users_table.item(row, 1).checkState() == Qt.Checked
                if username in users:
                    users[username]["is_admin"] = is_admin

            self._save_users(users)
            event.accept()

        except Exception as e:
            logger.error(f"Errore nel salvataggio delle modifiche: {str(e)}")
            event.accept() 