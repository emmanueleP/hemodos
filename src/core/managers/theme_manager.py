from PyQt5.QtGui import QPalette, QColor
from core.themes import THEMES

class ThemeManager:
    def __init__(self, main_window):
        self.main_window = main_window

    def apply_theme(self):
        """Applica il tema all'applicazione"""
        theme_id = self.main_window.settings.value("theme", "light")
        
        # Gestisci la migrazione dal vecchio al nuovo sistema di temi
        if theme_id == "Scuro":
            theme_id = "dark"
        elif theme_id == "Chiaro":
            theme_id = "light"
            
        # Assicurati che il tema esista
        if theme_id not in THEMES:
            theme_id = "light"
            
        self.main_window.settings.setValue("theme", theme_id)
        theme = THEMES[theme_id]
        
        # Applica il foglio di stile
        self.main_window.setStyleSheet(theme.get_stylesheet())
        
        # Applica il tema ai widget principali
        if hasattr(self.main_window, 'reservations_widget'):
            self.main_window.reservations_widget.setStyleSheet(theme.get_stylesheet())

    def get_current_theme(self):
        """Restituisce il tema corrente"""
        theme_id = self.main_window.settings.value("theme", "light")
        return THEMES.get(theme_id, THEMES["light"]) 