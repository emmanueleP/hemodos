from gui.dialogs.base_dialog import HemodosDialog
from PyQt5.QtWidgets import (QVBoxLayout, QLabel, QPushButton, 
                            QHBoxLayout, QCheckBox, QDialog, QApplication, 
                            QLineEdit, QMessageBox, QGroupBox, QWidget)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QPixmap, QFont, QIcon
from gui.dialogs.database_dialog import ConfigDatabaseDialog
import sys
import os
import json
import hashlib
from core.logger import logger
from gui.admin.hemodos_admin import HemodosAdmin


class WelcomeDialog(HemodosDialog):
    def __init__(self, parent=None):
        super().__init__(parent, "Hemodos - Login")
        self.settings = QSettings('Hemodos', 'DatabaseSettings')
        self.current_user = None
        
        # Ottieni il percorso cloud salvato
        self.cloud_path = self.settings.value("cloud_path", "")
        
        # Se è il primo avvio, il percorso cloud sarà configurato dopo il FirstRunDialog
        if not self.cloud_path and not self.settings.value("first_run", True, type=bool):
            # Se non è il primo avvio e non c'è un percorso cloud, configuralo
            self.configure_cloud_path()
        
        # Il file degli utenti sarà nel cloud
        self.users_file = os.path.join(self.cloud_path, ".hemodos_users") if self.cloud_path else None
        
        #Rimuovi ok e annulla da HemodosDialog
        for i in reversed(range(self.buttons_layout.count())):
            widget = self.buttons_layout.itemAt(i).widget()
            if isinstance(widget, QPushButton):
                widget.setParent(None)
                widget.deleteLater()
        
        self.init_ui()
      
    def init_ui(self):
        # Container principale
        main_container = QWidget()
        main_layout = QVBoxLayout(main_container)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # Logo
        logo_label = QLabel()
        logo_pixmap = QPixmap('src/assets/logo_info.png')
        scaled_pixmap = logo_pixmap.scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(scaled_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(logo_label)

        # Form di login
        login_group = QGroupBox("Accesso")
        login_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #004d4d;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
                color: #004d4d;
            }
        """)
        login_layout = QVBoxLayout(login_group)
        login_layout.setSpacing(15)

        # Username
        username_layout = QHBoxLayout()
        username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Inserisci username")
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        login_layout.addLayout(username_layout)

        # Password
        password_layout = QHBoxLayout()
        password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Inserisci password")
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        login_layout.addLayout(password_layout)

        # Login button
        login_button = QPushButton("Login")
        login_button.clicked.connect(self.handle_login)
        login_button.setStyleSheet("""
            QPushButton {
                background-color: #004d4d;
                color: white;
                padding: 8px;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #006666;
            }
        """)
        login_layout.addWidget(login_button, alignment=Qt.AlignCenter)

        main_layout.addWidget(login_group)

        # Container pulsanti
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_container.setStyleSheet("""
            QPushButton {
                background-color: #e6e6e6;
                border: none;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #cccccc;
            }
            QPushButton:disabled {
                background-color: #f2f2f2;
                color: #999999;
            }
        """)

        # Database Config Button
        self.config_db_button = QPushButton("Configura Database")
        self.config_db_button.clicked.connect(self.show_database_config)
        self.config_db_button.setEnabled(False)
        buttons_layout.addWidget(self.config_db_button)

        # Admin Button
        self.admin_button = QPushButton("HemodosAdmin")
        self.admin_button.clicked.connect(self.show_admin)
        self.admin_button.setEnabled(False)
        buttons_layout.addWidget(self.admin_button)

        main_layout.addWidget(buttons_container)

        # Copyright
<<<<<<< HEAD
        copyright_label = QLabel("© 2025 Emmanuele Pani. Under MIT License.")
        copyright_label.setStyleSheet("color: #666666; font-size: 11px; padding: 10px;")
=======
        copyright_label = QLabel("© 2025 Emmanuele Pani.")
        copyright_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 11px;
                padding: 10px;
            }
        """)
>>>>>>> e96e87b7ca2acbc94ed418b25497070b11d1b288
        copyright_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(copyright_label)

        self.content_layout.addWidget(main_container)

    def configure_cloud_path(self):
        """Configura il percorso cloud se non esiste"""
        dialog = ConfigDatabaseDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.cloud_path = self.settings.value("cloud_path", "")
            if self.cloud_path:
                # Crea il file degli utenti nel cloud se non esiste
                self.users_file = os.path.join(self.cloud_path, ".hemodos_users")
                if not os.path.exists(self.users_file):
                    self.create_default_admin()
            else:
                QMessageBox.critical(self, "Errore", "È necessario configurare un percorso cloud per utilizzare l'applicazione")
                sys.exit(1)

    def handle_login(self):
        """Gestisce il login dell'utente"""
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Errore", "Inserisci username e password")
            return

        # Hash della password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Verifica le credenziali
        if self.verify_credentials(username, hashed_password):
            self.current_user = username
            self.settings.setValue("current_user", username)
            
            # Abilita i pulsanti
            self.config_db_button.setEnabled(True)
            self.admin_button.setEnabled(self.is_admin(username))
            
            # Mostra messaggio di benvenuto
            QMessageBox.information(self, "Successo", f"Benvenuto, {username}!")
            
            # Passa alla finestra principale
            self.accept()  # Chiude il dialog con successo
        else:
            QMessageBox.warning(self, "Errore", "Credenziali non valide")

    def verify_credentials(self, username, hashed_password):
        """Verifica le credenziali dell'utente dal file nel cloud"""
        try:
            if not self.cloud_path or not self.users_file:
                QMessageBox.critical(self, "Errore", "Configurazione cloud non trovata")
                self.configure_cloud_path()
                return False

            if not os.path.exists(self.users_file):
                # Se il file non esiste nel cloud, verifica se esiste localmente
                local_users_file = os.path.join(os.path.expanduser("~"), ".hemodos_users")
                if os.path.exists(local_users_file):
                    # Migra il file locale nel cloud
                    with open(local_users_file, 'r') as f:
                        users = json.load(f)
                    with open(self.users_file, 'w') as f:
                        json.dump(users, f)
                    os.remove(local_users_file)  # Rimuovi il file locale
                else:
                    # Se non esiste neanche localmente, crea l'admin di default nel cloud
                    self.create_default_admin()

            with open(self.users_file, 'r') as f:
                users = json.load(f)
                if username in users and users[username]["password"] == hashed_password:
                    # Ottieni il percorso del database dell'utente
                    user_db_path = users[username].get("database_path")
                    if not user_db_path:
                        # Se non esiste, crealo
                        user_db_path = os.path.join(self.cloud_path, username)
                        os.makedirs(user_db_path, exist_ok=True)
                        users[username]["database_path"] = user_db_path
                        # Aggiorna il file degli utenti
                        with open(self.users_file, 'w') as f:
                            json.dump(users, f)
                    
                    # Salva il percorso del database nelle impostazioni
                    self.settings.setValue("current_user_db", user_db_path)
                    self.settings.setValue("cloud_path", self.cloud_path)
                    self.settings.sync()  # Forza il salvataggio delle impostazioni
                    
                    return True
                    
        except Exception as e:
            logger.error(f"Errore nella verifica delle credenziali: {str(e)}")
            QMessageBox.critical(self, "Errore", f"Errore nella verifica delle credenziali: {str(e)}")
        return False

    def create_default_admin(self):
        """Crea l'utente admin di default nel cloud"""
        try:
            if not self.cloud_path:
                QMessageBox.critical(self, "Errore", "Configurazione cloud necessaria")
                return

            # Crea la directory per l'admin
            admin_path = os.path.join(self.cloud_path, "admin")
            os.makedirs(admin_path, exist_ok=True)

            default_admin = {
                "admin": {
                    "password": hashlib.sha256("admin".encode()).hexdigest(),
                    "is_admin": True,
                    "database_path": admin_path
                }
            }
            
            # Salva il file degli utenti nel cloud
            with open(self.users_file, 'w') as f:
                json.dump(default_admin, f)
                
        except Exception as e:
            logger.error(f"Errore nella creazione dell'admin: {str(e)}")
            QMessageBox.critical(self, "Errore", f"Errore nella creazione dell'admin: {str(e)}")

    def is_admin(self, username):
        """Verifica se l'utente è admin"""
        try:
            with open(self.users_file, 'r') as f:
                users = json.load(f)
                return users.get(username, {}).get("is_admin", False)
        except Exception as e:
            logger.error(f"Errore nella verifica dei permessi admin: {str(e)}")
            return False

    def show_database_config(self):
        """Mostra la finestra di configurazione del database"""
        if not self.current_user:
            QMessageBox.warning(self, "Errore", "Effettua prima il login")
            return

        dialog = ConfigDatabaseDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            # Dopo la configurazione del database, passa alla finestra principale
            self.accept()

    def show_admin(self):
        """Mostra la finestra di amministrazione"""
        if not self.current_user or not self.is_admin(self.current_user):
            QMessageBox.warning(self, "Errore", "Accesso non autorizzato")
            return

        admin_dialog = HemodosAdmin(self)
        admin_dialog.exec_()

    def closeEvent(self, event):
        """Gestisce la chiusura del dialog"""
        try:
            if hasattr(self.parent(), 'cloud_manager'):
                self.parent().cloud_manager.cleanup()
            event.accept()
        except Exception as e:
            logger.error(f"Errore nella chiusura del dialog: {str(e)}")
            event.accept() 