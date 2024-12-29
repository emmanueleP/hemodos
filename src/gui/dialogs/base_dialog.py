from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import QSettings
from core.themes import THEMES

class HemodosDialog(QDialog):
    def __init__(self, parent=None, title=""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.apply_theme()
        
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