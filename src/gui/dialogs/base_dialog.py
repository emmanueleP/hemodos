from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtCore import QSettings
from core.themes import THEMES

class HemodosDialog(QDialog):
    def __init__(self, parent=None, title=""):
        super().__init__(parent)
        self.setWindowTitle(title)
        
        # Layout principale
        self.main_layout = QVBoxLayout(self)
        
        # Layout per il contenuto
        self.content_layout = QVBoxLayout()
        self.main_layout.addLayout(self.content_layout)
        
        # Layout per i pulsanti
        self.buttons_layout = QHBoxLayout()
        
        # Pulsanti standard
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Annulla")
        cancel_button.clicked.connect(self.reject)
        
        self.buttons_layout.addStretch()
        self.buttons_layout.addWidget(ok_button)
        self.buttons_layout.addWidget(cancel_button)
        
        self.main_layout.addLayout(self.buttons_layout)
        
        # Applica il tema
        self.apply_theme()
        
        # Stile pulsanti
        self.button_style = """
            QPushButton {
                background-color: #004d4d;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #006666;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """
        
        ok_button.setStyleSheet(self.button_style)
        cancel_button.setStyleSheet(self.button_style)
        
    def apply_theme(self):
        """Applica il tema corrente al dialogo"""
        settings = QSettings('Hemodos', 'DatabaseSettings')
        theme_id = settings.value("theme", "light")
        
        # Gestisci la migrazione dal vecchio al nuovo sistema di temi
        if theme_id == "Scuro":
            theme_id = "dark"
        elif theme_id == "Chiaro":
            theme_id = "light"
            
        # Assicurati che il tema esista
        if theme_id not in THEMES:
            theme_id = "light"
            
        theme = THEMES[theme_id]
        self.setStyleSheet(theme.get_stylesheet()) 