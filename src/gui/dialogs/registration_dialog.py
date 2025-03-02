from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, 
                            QLineEdit, QPushButton, QMessageBox)
from src.core.user_manager import UserManager

class RegistrationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.user_manager = UserManager()
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Registrazione Nuovo Utente")
        layout = QVBoxLayout()
        
        form = QFormLayout()
        
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.Password)
        self.email = QLineEdit()
        
        form.addRow("Username:", self.username)
        form.addRow("Password:", self.password)
        form.addRow("Conferma Password:", self.confirm_password)
        form.addRow("Email:", self.email)
        
        layout.addLayout(form)
        
        register_btn = QPushButton("Registrati")
        register_btn.clicked.connect(self.handle_registration)
        layout.addWidget(register_btn)
        
        self.setLayout(layout)
        
    def handle_registration(self):
        username = self.username.text()
        password = self.password.text()
        confirm = self.confirm_password.text()
        email = self.email.text()
        
        if not all([username, password, confirm, email]):
            QMessageBox.warning(self, "Errore", "Compila tutti i campi")
            return
            
        if password != confirm:
            QMessageBox.warning(self, "Errore", "Le password non coincidono")
            return
            
        if self.user_manager.register_user(username, password, email):
            QMessageBox.information(
                self,
                "Successo",
                "Registrazione completata. Ora puoi accedere."
            )
            self.accept()
        else:
            QMessageBox.warning(
                self,
                "Errore",
                "Username già in uso o errore nella registrazione"
            ) 