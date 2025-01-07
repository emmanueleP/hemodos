from PyQt5.QtCore import QObject, QSettings, QDate
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QInputDialog
import os

class DatabaseDirManager(QObject):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.settings = QSettings('Hemodos', 'DatabaseSettings')

    def setup_local_database(self):
        """Crea un nuovo database locale"""
        try:
            base_path = os.path.expanduser("~/Documents/Hemodos")
            year_path = os.path.join(base_path, str(QDate.currentDate().year()))
            os.makedirs(year_path, exist_ok=True)
            self.settings.setValue("cloud_service", "Locale")
            self.settings.setValue("selected_year", str(QDate.currentDate().year()))
            return True
        except Exception as e:
            QMessageBox.critical(self.main_window, "Errore", f"Errore nella creazione del database locale: {str(e)}")
            return False

    def open_local_database(self):
        """Apre un database locale esistente"""
        try:
            base_path = QFileDialog.getExistingDirectory(
                self.main_window,
                "Seleziona la cartella dell'anno",
                os.path.expanduser("~/Documents/Hemodos")
            )
            if not base_path:
                return False

            if os.path.basename(base_path).isdigit():
                year = os.path.basename(base_path)
                self.settings.setValue("selected_year", year)
                self.settings.setValue("cloud_service", "Locale")
                self.settings.setValue("last_database", os.path.join(base_path, f"hemodos_{year}.db"))
                return True
            else:
                QMessageBox.warning(self.main_window, "Errore", "Seleziona una cartella anno valida")
                return False
        except Exception as e:
            QMessageBox.critical(self.main_window, "Errore", f"Errore nell'apertura del database: {str(e)}")
            return False

    def setup_cloud_database(self, service_type):
        """Configura un nuovo database su cloud"""
        try:
            cloud_path = self._get_cloud_path(service_type)
            if not cloud_path:
                QMessageBox.warning(self.main_window, "Errore", f"Cartella {service_type} non trovata")
                return False

            base_path = os.path.join(cloud_path, "Hemodos")
            year_path = os.path.join(base_path, str(QDate.currentDate().year()))
            os.makedirs(year_path, exist_ok=True)
            
            self.settings.setValue("cloud_service", service_type)
            self.settings.setValue("cloud_path", cloud_path)
            self.settings.setValue("selected_year", str(QDate.currentDate().year()))
            return True
        except Exception as e:
            QMessageBox.critical(self.main_window, "Errore", f"Errore nella configurazione cloud: {str(e)}")
            return False

    def open_cloud_database(self, service_type):
        """Apre un database esistente su cloud"""
        try:
            cloud_path = self._get_cloud_path(service_type)
            if not cloud_path:
                QMessageBox.warning(self.main_window, "Errore", f"Cartella {service_type} non trovata")
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
                self.settings.setValue("cloud_service", service_type)
                self.settings.setValue("selected_year", year)
                return True
            return False
        except Exception as e:
            QMessageBox.critical(self.main_window, "Errore", f"Errore nell'apertura del database cloud: {str(e)}")
            return False

    def _get_cloud_path(self, service_type):
        """Ottiene il percorso del servizio cloud"""
        if service_type == "OneDrive":
            return self._get_onedrive_path()
        elif service_type == "GoogleDrive":
            return self._get_gdrive_path()
        return None

    def _get_onedrive_path(self):
        """Trova il percorso di OneDrive"""
        possible_paths = [
            os.path.expanduser("~/OneDrive"),
            os.path.expanduser("~/OneDrive - Personal"),
            "C:/Users/" + os.getlogin() + "/OneDrive",
        ]
        return next((path for path in possible_paths if os.path.exists(path)), None)

    def _get_gdrive_path(self):
        """Trova il percorso di Google Drive"""
        possible_paths = [
            os.path.expanduser("~/Google Drive"),
            os.path.expanduser("~/GoogleDrive"),
            "C:/Users/" + os.getlogin() + "/Google Drive",
            "C:/Users/" + os.getlogin() + "/GoogleDrive",
        ]
        return next((path for path in possible_paths if os.path.exists(path)), None) 