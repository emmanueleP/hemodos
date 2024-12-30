from gui.gui import MainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QFileDialog, QMessageBox, QProgressDialog
from PyQt5.QtGui import QFont, QIcon
from gui.dialogs.database_dialog import FirstRunDialog
from PyQt5.QtCore import QSettings, Qt
import os
import json
import sys

# Load configuration
def load_config():
    try:
        # Prima cerca nella directory di installazione
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
        config_path = os.path.join(exe_dir, 'config.json')
        
        # Se non esiste, cerca nella directory corrente
        if not os.path.exists(config_path):
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
        
        # Se ancora non esiste, usa il config di default
        if not os.path.exists(config_path):
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config.json')
        
        with open(config_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print("Errore: Il file config.json non è stato trovato")
        # Crea un config di default
        config = {
            "database": {
                "host": "localhost",
                "port": 5432,
                "name": "hemodos_db",
                "user": "admin",
                "password": "password",
                "backup_dir": "backups"
            },
            "app": {
                "debug": True,
                "log_level": "INFO",
                "autosave": {"enabled": True, "interval": 5},
                "cloud": {"service": "Locale", "sync_interval": 30}
            },
            "ui": {
                "theme": "light",
                "primary_color": "#004d4d",
                "font": "SF Pro Display",
                "window": {
                    "width": 1024,
                    "height": 768,
                    "min_width": 800,
                    "min_height": 600
                }
            }
        }
        # Salva il config di default
        try:
            with open(config_path, 'w', encoding='utf-8') as file:
                json.dump(config, file, indent=4)
            return config
        except Exception as e:
            print(f"Errore nel salvare il config di default: {str(e)}")
            raise
    except json.JSONDecodeError:
        print("Errore: Il file config.json non contiene un JSON valido")
        raise

def show_update_dialog(version, release_notes, download_url):
    """Mostra il dialogo quando è disponibile un aggiornamento"""
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle("Aggiornamento Disponibile")
    msg.setText(f"È disponibile una nuova versione di Hemodos (v{version})")
    msg.setInformativeText("Note di rilascio:\n" + release_notes)
    msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    msg.setDefaultButton(QMessageBox.Yes)
    
    if msg.exec_() == QMessageBox.Yes:
        # Crea e mostra la finestra di progresso
        progress = QProgressDialog("Download aggiornamento in corso...", "Annulla", 0, 100)
        progress.setWindowModality(Qt.WindowModal)
        progress.setAutoClose(True)
        
        # Avvia il download e l'installazione
        from core.updater import Updater
        updater = Updater(download_url)
        updater.update_progress.connect(progress.setValue)
        updater.update_completed.connect(lambda: QApplication.instance().quit())
        updater.update_error.connect(lambda msg: QMessageBox.warning(None, "Errore", msg))
        updater.start()

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Hemodos")
    app.setStyle("Fusion")
    
    # Imposta l'icona dell'applicazione
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    settings = QSettings('Hemodos', 'DatabaseSettings')
    
    # Controllo aggiornamenti automatico
    if settings.value("check_updates", True, type=bool):
        from core.updater import UpdateChecker
        update_checker = UpdateChecker("1.0.0")
        update_checker.update_available.connect(show_update_dialog)
        update_checker.start()
    
    first_run = settings.value("first_run", True, type=bool)

    if first_run:
        dialog = FirstRunDialog()
        if dialog.exec_() == QDialog.Accepted:
            option = dialog.selected_option
            if option == 1:  # Nuovo database locale
                settings.setValue("cloud_service", "Locale")
            elif option == 2:  # Database locale esistente
                file_path, _ = QFileDialog.getOpenFileName(
                    None,
                    "Apri Database",
                    os.path.expanduser("~/Documents/Hemodos"),
                    "Database SQLite (*.db)"
                )
                if file_path:
                    settings.setValue("last_database", file_path)
                    settings.setValue("cloud_service", "Locale")
            elif option == 3:  # OneDrive
                settings.setValue("cloud_service", "OneDrive")
            elif option == 4:  # Google Drive
                settings.setValue("cloud_service", "Google Drive")
            
            settings.setValue("first_run", False)
        else:
            sys.exit()

    # Load config
    config = load_config()

    # Mostra il dialogo di benvenuto al primo avvio
    if settings.value("show_welcome", True, type=bool):
        from gui.dialogs.welcome_dialog import WelcomeDialog
        welcome = WelcomeDialog()
        welcome.exec_()
    
    # Avvia l'applicazione principale
    window = MainWindow(config)
    window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
