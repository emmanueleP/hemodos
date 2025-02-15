from PyQt5.QtWidgets import QStatusBar, QLabel
from datetime import datetime

class StatusManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.status_bar = QStatusBar(main_window)
        main_window.setStatusBar(self.status_bar)
        
        # Crea le label permanenti
        self.db_label = QLabel()
        self.cloud_label = QLabel()
        self.last_save_label = QLabel()
        
        # Aggiungi le label alla status bar
        self.status_bar.addPermanentWidget(self.db_label)
        self.status_bar.addPermanentWidget(self.cloud_label)
        self.status_bar.addPermanentWidget(self.last_save_label)
        
        # Inizializza le informazioni
        self.update_last_save_info()
        
    def show_message(self, message, timeout=3000):
        """Mostra un messaggio temporaneo nella status bar"""
        self.status_bar.showMessage(message, timeout)
        
    def update_db_info(self, year, date_str, exists=True):
        """Aggiorna le informazioni del database"""
        cloud_service = self.main_window.settings.value("cloud_service", "Locale")
        storage_info = ""
        
        if cloud_service == "Locale":
            storage_info = "(Documenti)"
        elif cloud_service == "Syncthing":
            storage_info = "(Syncthing)"
        
        # Costruisci il messaggio
        if exists:
            self.db_label.setText(f"Database: {year} - {date_str} {storage_info}")
        else:
            self.db_label.setText(f"Database: {year} - {date_str} {storage_info} (Non esistente)")
            
    def update_last_save_info(self):
        """Aggiorna le informazioni sull'ultimo salvataggio"""
        last_save = self.main_window.settings.value("last_save_time", "Mai")
        self.last_save_label.setText(f"Ultimo salvataggio: {last_save}")
        
    def set_db_error(self):
        """Imposta il messaggio di errore del database"""
        cloud_service = self.main_window.settings.value("cloud_service", "Locale")
        storage_info = "(Documenti)" if cloud_service == "Locale" else f"({cloud_service})"
        self.db_label.setText(f"Errore info database {storage_info}")

    def update_cloud_info(self, message):
        """Aggiorna le informazioni del cloud"""
        if self.main_window.settings.value("cloud_service") == "Syncthing":
            self.cloud_label.setText(f"Syncthing: {message}")
        else:
            self.cloud_label.setText("") 