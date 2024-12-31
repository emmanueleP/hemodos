from PyQt5.QtGui import QPalette, QColor
from core.themes import THEMES

class ThemeManager:
    def __init__(self, main_window):
        self.main_window = main_window

    def apply_theme(self):
        """Applica il tema all'applicazione"""
        # Gestisci la migrazione dal vecchio al nuovo sistema di temi
        theme_id = self.main_window.settings.value("theme", "light")
        if theme_id == "Scuro":
            theme_id = "dark"
            self.main_window.settings.setValue("theme", "dark")
        elif theme_id == "Chiaro":
            theme_id = "light"
            self.main_window.settings.setValue("theme", "light")
        
        # Assicurati che il tema esista, altrimenti usa quello chiaro
        if theme_id not in THEMES:
            theme_id = "light"
            self.main_window.settings.setValue("theme", "light")
        
        theme = THEMES[theme_id]
        
        # Applica il foglio di stile
        self.main_window.setStyleSheet(theme.get_stylesheet())
        
        # Applica il tema anche ai widget principali
        if hasattr(self.main_window, 'reservations_widget'):
            self.main_window.reservations_widget.setStyleSheet(theme.get_stylesheet())
        
        # Applica la palette di colori
        palette = QPalette()
        if theme_id == "dark":
            palette.setColor(QPalette.Window, QColor("#2b2b2b"))
            palette.setColor(QPalette.WindowText, QColor("#ffffff"))
            palette.setColor(QPalette.Base, QColor("#3b3b3b"))
            palette.setColor(QPalette.AlternateBase, QColor("#353535"))
            palette.setColor(QPalette.Text, QColor("#ffffff"))
            palette.setColor(QPalette.Button, QColor("#353535"))
            palette.setColor(QPalette.ButtonText, QColor("#ffffff"))
            palette.setColor(QPalette.Highlight, QColor("#2979ff"))
            palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
        else:
            palette.setColor(QPalette.Window, QColor("#f0f0f0"))
            palette.setColor(QPalette.WindowText, QColor("#000000"))
            palette.setColor(QPalette.Base, QColor("#ffffff"))
            palette.setColor(QPalette.AlternateBase, QColor("#f7f7f7"))
            palette.setColor(QPalette.Text, QColor("#000000"))
            palette.setColor(QPalette.Button, QColor("#e0e0e0"))
            palette.setColor(QPalette.ButtonText, QColor("#000000"))
            palette.setColor(QPalette.Highlight, QColor("#0078d7"))
            palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))

        self.main_window.setPalette(palette)

    def get_current_theme(self):
        """Restituisce il tema corrente"""
        theme_id = self.main_window.settings.value("theme", "light")
        return THEMES.get(theme_id, THEMES["light"]) 