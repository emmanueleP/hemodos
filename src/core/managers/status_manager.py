from PyQt5.QtWidgets import QStatusBar, QLabel
from datetime import datetime

class StatusManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.status_bar = QStatusBar(main_window)
        main_window.setStatusBar(self.status_bar)
        
        # Crea le label permanenti
        self.db_label = QLabel()
        self.last_save_label = QLabel()
        
        # Aggiungi le label alla status bar
        self.status_bar.addPermanentWidget(self.db_label)
        self.status_bar.addPermanentWidget(self.last_save_label)
        
        # Inizializza le informazioni
        self.update_last_save_info()
        
    def show_message(self, message, timeout=3000):
        """Mostra un messaggio temporaneo nella status bar"""
        self.status_bar.showMessage(message, timeout)
        
    def update_db_info(self, year, date_str, exists=True):
        """Aggiorna le informazioni del database"""
        if exists:
            self.db_label.setText(f"Database: {year} - {date_str}")
        else:
            self.db_label.setText(f"Database: {year} - {date_str} (Non esistente)")
            
    def update_last_save_info(self):
        """Aggiorna le informazioni sull'ultimo salvataggio"""
        last_save = self.main_window.settings.value("last_save_time", "Mai")
        self.last_save_label.setText(f"Ultimo salvataggio: {last_save}")
        
    def set_db_error(self):
        """Imposta il messaggio di errore del database"""
        self.db_label.setText("Errore info database") 