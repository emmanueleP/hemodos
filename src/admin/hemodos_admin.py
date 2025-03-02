from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
from datetime import datetime
from src.core.user_manager import UserManager

class HemodosAdmin(QMainWindow):
    def __init__(self):
        super().__init__()
        self.user_manager = UserManager()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Hemodos Admin")
        self.setMinimumSize(800, 600)
        
        # Widget centrale
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Tabella utenti
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(7)
        self.users_table.setHorizontalHeaderLabels([
            "Username", "Email", "Admin", "Stato", 
            "Creato il", "Ultimo accesso", "Azioni"
        ])
        layout.addWidget(self.users_table)
        
        # Toolbar
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Azioni
        refresh_action = QAction("Aggiorna", self)
        refresh_action.triggered.connect(self.load_users)
        toolbar.addAction(refresh_action)
        
        add_user_action = QAction("Nuovo Utente", self)
        add_user_action.triggered.connect(self.add_user)
        toolbar.addAction(add_user_action)
        
        self.load_users()
        
    def load_users(self):
        """Carica la lista utenti"""
        users = self.user_manager._load_users()
        self.users_table.setRowCount(len(users))
        
        for row, (username, data) in enumerate(users.items()):
            self.users_table.setItem(row, 0, QTableWidgetItem(username))
            self.users_table.setItem(row, 1, QTableWidgetItem(data['email']))
            self.users_table.setItem(row, 2, QTableWidgetItem('Sì' if data['is_admin'] else 'No'))
            self.users_table.setItem(row, 3, QTableWidgetItem(data['status']))
            self.users_table.setItem(row, 4, QTableWidgetItem(
                datetime.fromisoformat(data['created_at']).strftime('%d/%m/%Y %H:%M')
            ))
            self.users_table.setItem(row, 5, QTableWidgetItem(
                datetime.fromisoformat(data['last_login']).strftime('%d/%m/%Y %H:%M')
                if data['last_login'] else 'Mai'
            ))
            
            # Pulsanti azioni
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            
            edit_btn = QPushButton("Modifica")
            edit_btn.clicked.connect(lambda _, u=username: self.edit_user(u))
            actions_layout.addWidget(edit_btn)
            
            disable_btn = QPushButton("Disabilita" if data['status'] == 'active' else "Abilita")
            disable_btn.clicked.connect(lambda _, u=username: self.toggle_user_status(u))
            actions_layout.addWidget(disable_btn)
            
            self.users_table.setCellWidget(row, 6, actions_widget) 