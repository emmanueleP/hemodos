from gui.dialogs.base_dialog import HemodosDialog
from PyQt5.QtWidgets import (QVBoxLayout, QLabel, QPushButton, 
                            QHBoxLayout, QLineEdit, QMessageBox, QGroupBox, QWidget)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QPixmap
from core.user_manager import UserManager
from core.logger import logger

class WelcomeDialog(HemodosDialog):
    def __init__(self, parent=None):
        super().__init__(parent, "Hemodos - Login")
        self.settings = QSettings('Hemodos', 'DatabaseSettings')
        self.user_manager = UserManager()
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

        # Pulsante Login
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

        # Copyright
        copyright_label = QLabel("© 2025 Emmanuele Pani. Under MIT License.")
        copyright_label.setStyleSheet("color: #666666; font-size: 11px; padding: 10px;")
        copyright_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(copyright_label)

        self.content_layout.addWidget(main_container)

    def handle_login(self):
        """Gestisce il login dell'utente"""
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Errore", "Inserisci username e password")
            return

        # Verifica le credenziali usando il UserManager
        if self.user_manager.verify_login(username, password):
            # Salva l'utente corrente nelle impostazioni
            self.settings.setValue("current_user", username)
            # Ottieni e salva il percorso del database dell'utente
            user_db = self.user_manager.get_user_database(username)
            if user_db:
                self.settings.setValue("current_user_db", user_db)
            self.settings.sync()
            QMessageBox.information(self, "Successo", f"Benvenuto, {username}!")
            self.accept()
        else:
            QMessageBox.warning(self, "Errore", "Credenziali non valide") 