import sys
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QFileDialog
from PyQt5.QtGui import QFont
from gui import MainWindow
from PyQt5.QtCore import QSettings
from database_dialog import FirstRunDialog
import os

# Load configuration
def load_config():
    try:
        with open('config.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print("Errore: Il file config.json non è stato trovato")
        raise
    except json.JSONDecodeError:
        print("Errore: Il file config.json non contiene un JSON valido")
        raise

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Hemodos")
    app.setStyle("Fusion")
    
    settings = QSettings('Hemodos', 'DatabaseSettings')
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

    # Initialize main window
    window = MainWindow(config)
    window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
