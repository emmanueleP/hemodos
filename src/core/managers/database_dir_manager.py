from PyQt5.QtCore import QObject, QSettings, QDate
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QInputDialog
import os
import logging
import sys
import platform

logger = logging.getLogger(__name__)

class DatabaseDirManager(QObject):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.settings = QSettings('Hemodos', 'DatabaseSettings')

    def is_first_run(self):
        """Verifica se è il primo avvio dell'applicazione"""
        return not bool(self.settings.value("hemodos_configured", False))

    def is_cloud_path(self, path):
        """Determina se il percorso è cloud"""
        if not path:
            return False
            
        # Indicatori di servizi cloud
        cloud_indicators = [
            "OneDrive", "Google Drive", "GoogleDrive", "Dropbox",
            "iCloud", "icloud", "CloudStorage"
        ]
        return any(indicator in path for indicator in cloud_indicators)

    def get_base_path(self):
        """Ottiene il percorso base corrente (locale o cloud)"""
        cloud_path = self.settings.value("cloud_path", "")
        if cloud_path:
            return os.path.join(cloud_path, "Hemodos")
        else:
            # Percorso predefinito basato sul sistema operativo
            if platform.system() == "Darwin":  # macOS
                return os.path.expanduser("~/Documents/Hemodos")
            else:  # Windows e altri
                return os.path.join(os.path.expanduser("~"), "Documents", "Hemodos")

    def is_local_mode(self):
        """Verifica se siamo in modalità locale"""
        return not bool(self.settings.value("cloud_path", ""))

    def is_configured(self):
        """Verifica se Hemodos è già configurato"""
        base_path = self.get_base_path()
        return os.path.exists(base_path) and bool(self.settings.value("hemodos_configured", False))

    def setup_local_database(self):
        """Configura un nuovo database locale"""
        try:
            base_path = self.get_base_path()
            year_path = os.path.join(base_path, str(QDate.currentDate().year()))
            os.makedirs(year_path, exist_ok=True)
            
            # Pulisci le impostazioni cloud e imposta come configurato
            self.settings.setValue("cloud_path", "")
            self.settings.setValue("selected_year", str(QDate.currentDate().year()))
            self.settings.setValue("hemodos_configured", True)
            
            # Imposta modalità locale
            self.main_window.cloud_manager.set_local_mode()
            
            logger.info("Database locale configurato correttamente")
            return True
            
        except Exception as e:
            logger.error(f"Errore nella configurazione del database locale: {str(e)}")
            return False

    def open_local_database(self):
        """Apre un database locale esistente"""
        try:
            base_path = QFileDialog.getExistingDirectory(
                self.main_window,
                "Seleziona la cartella dell'anno",
                self.get_base_path()
            )
            if not base_path:
                return False

            if os.path.basename(base_path).isdigit():
                year = os.path.basename(base_path)
                
                # Imposta le impostazioni
                self.settings.setValue("selected_year", year)
                self.settings.setValue("cloud_path", "")
                self.settings.setValue("last_database", os.path.join(base_path, f"hemodos_{year}.db"))
                self.settings.setValue("hemodos_configured", True)
                
                # Imposta modalità locale
                self.main_window.cloud_manager.set_local_mode()
                
                logger.info(f"Database locale dell'anno {year} aperto correttamente")
                return True
            else:
                QMessageBox.warning(self.main_window, "Errore", "Seleziona una cartella anno valida")
                return False
                
        except Exception as e:
            logger.error(f"Errore nell'apertura del database locale: {str(e)}")
            return False

    def setup_cloud_database(self):
        """Configura un nuovo database su cloud"""
        try:
            cloud_path = QFileDialog.getExistingDirectory(
                self.main_window,
                "Seleziona la cartella cloud",
                os.path.expanduser("~")
            )
            if not cloud_path:
                return False

            if not self.is_cloud_path(cloud_path):
                reply = QMessageBox.question(
                    self.main_window,
                    "Conferma",
                    "Il percorso selezionato non sembra essere una cartella cloud.\n"
                    "Vuoi continuare comunque?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return False

            base_path = os.path.join(cloud_path, "Hemodos")
            year_path = os.path.join(base_path, str(QDate.currentDate().year()))
            os.makedirs(year_path, exist_ok=True)
            
            self.settings.setValue("cloud_path", cloud_path)
            self.settings.setValue("selected_year", str(QDate.currentDate().year()))
            self.settings.setValue("hemodos_configured", True)
            return True
            
        except Exception as e:
            QMessageBox.critical(self.main_window, "Errore", f"Errore nella configurazione cloud: {str(e)}")
            return False

    def open_cloud_database(self):
        """Apre un database esistente su cloud"""
        try:
            cloud_path = QFileDialog.getExistingDirectory(
                self.main_window,
                "Seleziona la cartella cloud",
                os.path.expanduser("~")
            )
            if not cloud_path:
                return False

            hemodos_path = os.path.join(cloud_path, "Hemodos")
            if not os.path.exists(hemodos_path):
                QMessageBox.warning(self.main_window, "Errore", "Cartella Hemodos non trovata nel cloud")
                return False

            years = [d for d in os.listdir(hemodos_path) if os.path.isdir(os.path.join(hemodos_path, d)) and d.isdigit()]
            if not years:
                QMessageBox.warning(self.main_window, "Errore", "Nessun anno trovato nel cloud")
                return False

            year, ok = QInputDialog.getItem(
                self.main_window,
                "Seleziona Anno",
                "Scegli l'anno da aprire:",
                sorted(years, reverse=True),
                0, False
            )

            if ok:
                self.settings.setValue("cloud_path", cloud_path)
                self.settings.setValue("selected_year", year)
                self.settings.setValue("hemodos_configured", True)
                return True
            return False
            
        except Exception as e:
            QMessageBox.critical(self.main_window, "Errore", f"Errore nell'apertura del database cloud: {str(e)}")
            return False 