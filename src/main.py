from gui.gui import MainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QFileDialog, QMessageBox, QProgressDialog
from PyQt5.QtGui import QFont, QIcon
from core.themes import THEMES
from gui.dialogs.first_run_dialog import FirstRunDialog
from gui.dialogs.welcome_dialog import WelcomeDialog
from gui.dialogs.database_dialog import ConfigDatabaseDialog
from PyQt5.QtCore import QSettings, Qt
import os
import json
import sys
import logging
from core.paths_manager import PathsManager

# Configura il logging
def setup_logging(paths_manager):
    log_dir = paths_manager.get_logs_path()
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'hemodos.log')
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger('Hemodos')

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
                "theme": "dark",
                "primary_color": "#004d4d",
                "font": "Arial",
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
    try:
        app = QApplication(sys.argv)
        paths_manager = PathsManager()
        logger = setup_logging(paths_manager)
        
        logger.info("Avvio dell'applicazione")
        logger.debug(f"Directory risorse: {paths_manager.resources_path}")
        
        # Verifica se è il primo avvio
        config_file = os.path.join(paths_manager.get_config_path(), 'config.json')
        is_first_run = not os.path.exists(config_file)
        logger.debug(f"Primo avvio: {is_first_run}")
        
        if is_first_run:
            logger.info("Mostra dialog primo avvio")
            first_run = FirstRunDialog(None)
            first_run.paths_manager = paths_manager
            if first_run.exec_() != QDialog.Accepted:
                logger.info("Primo avvio annullato")
                sys.exit(0)
            # Dopo il primo avvio, non mostrare il welcome dialog
            settings = QSettings('Hemodos', 'DatabaseSettings')
            settings.setValue("first_run", False)
        elif not QSettings('Hemodos', 'DatabaseSettings').value("current_user"):
            # Mostra welcome dialog solo se non c'è un utente già loggato
            logger.info("Mostra welcome dialog")
            welcome = WelcomeDialog(None)
            welcome.paths_manager = paths_manager
            if welcome.exec_() != QDialog.Accepted:
                logger.info("Login annullato")
                sys.exit(0)

        app.setApplicationName("Hemodos")
        app.setStyle("Fusion")
        
        # Imposta l'icona dell'applicazione
        icon_path = paths_manager.get_asset_path("logo.png")
        logger.debug(f"Percorso icona: {icon_path}")
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))
            logger.info("Icona caricata con successo")
        else:
            logger.warning(f"Icona non trovata: {icon_path}")
            # Prova percorsi alternativi
            alt_paths = [
                os.path.join(paths_manager.resources_path, 'assets', 'logo.png'),
                os.path.join(paths_manager.base_path, 'src', 'assets', 'logo.png'),
                'src/assets/logo.png'
            ]
            for path in alt_paths:
                logger.debug(f"Tentativo percorso alternativo: {path}")
                if os.path.exists(path):
                    app.setWindowIcon(QIcon(path))
                    logger.info(f"Icona caricata dal percorso alternativo: {path}")
                    break
        
        settings = QSettings('Hemodos', 'DatabaseSettings')
        
        # Load config
        try:
            config = load_config()
            logger.debug("Configurazione caricata con successo")
        except Exception as e:
            logger.error(f"Errore nel caricamento della configurazione: {str(e)}")
            QMessageBox.critical(None, "Errore", 
                               "Errore nel caricamento della configurazione.\n"
                               f"Dettagli: {str(e)}")
            sys.exit(1)
        
        # Crea la finestra principale
        window = MainWindow(config)
        window.paths_manager = paths_manager
        
        # Imposta e applica il tema scuro come predefinito
        settings.setValue("theme", "dark")
        window.theme_manager.apply_theme()
        
        # Mostra la finestra principale
        window.show()
        logger.info("Applicazione avviata con successo")
        sys.exit(app.exec_())
        
    except Exception as e:
        logger = logging.getLogger('Hemodos')
        logger.error(f"Errore fatale: {str(e)}", exc_info=True)
        QMessageBox.critical(None, "Errore Fatale", 
                           f"Si è verificato un errore fatale:\n{str(e)}\n\n"
                           "Controlla i log per maggiori dettagli.")
        sys.exit(1)

if __name__ == "__main__":
    main()
