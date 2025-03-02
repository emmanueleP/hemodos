from gui.dialogs.base_dialog import HemodosDialog
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QRadioButton, QButtonGroup, QFileDialog,
                            QMessageBox, QGroupBox, QWidget, QInputDialog, QMenu, QDialog, QApplication)
from PyQt5.QtCore import QSettings, Qt, QDate, QTimer
from PyQt5.QtGui import QIcon, QPixmap
import os
import platform
from core.database import get_db_path
from core.delete_db_logic import get_base_path
from core.logger import logger
from core.themes import THEMES
import sqlite3

class ConfigDatabaseDialog(HemodosDialog):
    def __init__(self, parent=None):
        super().__init__(parent, "Gestione database Hemodos")
        self.main_window = parent
        self.settings = QSettings('Hemodos', 'DatabaseSettings')
        self.selected_option = None
        self.cloud_thread = None  # Inizializza il thread cloud
        self.init_ui()

    def init_ui(self):
        # Container principale
        main_container = QWidget()
        main_layout = QVBoxLayout(main_container)

        # Logo container
        logo_container = QWidget()
        logo_container.setFixedHeight(220)
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        
        # Aggiungi il logo
        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "logo_info.png")
        if not os.path.exists(logo_path):
            logo_path = "src/assets/logo_info.png"

        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            scaled_pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
        else:
            logo_label.setText("Logo non trovato")
            logo_label.setStyleSheet("QLabel { color: red; }")
        
        logo_layout.addWidget(logo_label)
        main_layout.addWidget(logo_container)

        # Testo introduttivo
        welcome_label = QLabel("Scegli come vuoi gestire il database:")
        welcome_label.setStyleSheet("font-size: 14px;")
        main_layout.addWidget(welcome_label)

        # Gruppo opzioni database
        options_group = QGroupBox("Tipo di Database")
        options_layout = QVBoxLayout()
        
        # Opzione Locale
        local_group = QGroupBox("Database Locale")
        local_layout = QVBoxLayout()
        
        self.local_new_button = QPushButton("Nuovo database")
        self.local_new_button.clicked.connect(lambda: self.handle_selection(1))
        self.local_new_button.setStyleSheet("""
            QPushButton {
                padding: 10px;
                background-color: #004d4d;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #006666;
            }
        """)
        local_layout.addWidget(self.local_new_button)
        
        self.local_existing_button = QPushButton("Database esistente")
        self.local_existing_button.clicked.connect(lambda: self.handle_selection(2))
        self.local_existing_button.setStyleSheet("""
            QPushButton {
                padding: 10px;
                background-color: #004d4d;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #006666;
            }
        """)
        local_layout.addWidget(self.local_existing_button)
        
        local_group.setLayout(local_layout)
        options_layout.addWidget(local_group)
        
        # Opzione Syncthing
        syncthing_group = QGroupBox("Database Sincronizzato (Syncthing)")
        syncthing_layout = QVBoxLayout()
        
        self.syncthing_button = QPushButton("Configura Syncthing")
        self.syncthing_button.clicked.connect(self._handle_cloud_database)
        self.syncthing_button.setStyleSheet("""
            QPushButton {
                padding: 10px;
                background-color: #004d4d;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #006666;
            }
        """)
        
        # Controlla se Syncthing è già configurato
        if self.settings.value("cloud_service") == "Syncthing":
            self.syncthing_button.setText("Database su Syncthing (Configurato)")
            self.selected_option = 3
            ok_button = self.buttons_layout.itemAt(1).widget()
            ok_button.setEnabled(True)
            
        syncthing_layout.addWidget(self.syncthing_button)
        
        # Aggiungi descrizione Syncthing
        syncthing_desc = QLabel(
            "Syncthing permette di sincronizzare automaticamente\n"
            "il database tra più dispositivi in modo sicuro."
        )
        syncthing_desc.setStyleSheet("color: #666; font-size: 11px;")
        syncthing_desc.setAlignment(Qt.AlignCenter)
        syncthing_layout.addWidget(syncthing_desc)
        
        syncthing_group.setLayout(syncthing_layout)
        options_layout.addWidget(syncthing_group)
        
        options_group.setLayout(options_layout)
        main_layout.addWidget(options_group)

        # Copyright
        copyright_label = QLabel("© 2025 Emmanuele Pani. Under MIT License.")
        copyright_label.setStyleSheet("color: #666666; font-size: 11px; padding: 10px;")
        copyright_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(copyright_label)

        main_layout.addStretch()
        self.content_layout.addWidget(main_container)

        # Modifica i pulsanti
        self.buttons_layout.itemAt(1).widget().setText("Avanti")  
        self.buttons_layout.itemAt(2).widget().setText("Esci")    
        ok_button = self.buttons_layout.itemAt(1).widget()
        ok_button.clicked.disconnect()
        ok_button.clicked.connect(self.check_and_accept)

    def check_and_accept(self):
        """Verifica e accetta il dialog"""
        try:
            # Salva le impostazioni prima di chiudere
            self.settings.sync()
            
            # Se è il primo avvio, non tentare di configurare il cloud_manager
            if self.settings.value("first_run", True, type=bool):
                self.accept()
                return
                
            # Altrimenti procedi con la configurazione normale
            cloud_path = self.settings.value("cloud_path", "")
            service_name = self.settings.value("cloud_service", "")
            
            if cloud_path and os.path.exists(cloud_path):
                self.accept()
            else:
                QMessageBox.critical(
                    self,
                    "Errore",
                    "Il percorso selezionato non è valido o non esiste"
                )
                
        except Exception as e:
            logger.error(f"Errore nella verifica finale: {str(e)}")
            QMessageBox.critical(
                self,
                "Errore",
                f"Errore nella configurazione finale:\n{str(e)}"
            )

    def load_year_databases(self, base_path, year):
        """Carica i database per l'anno selezionato"""
        try:
            # Imposta il percorso del database
            db_path = os.path.join(base_path, f"hemodos_{year}.db")
            self.settings.setValue("last_database", db_path)
            
            # Carica i dati dal database
            self.parent().database_manager.load_current_day()
            self.parent().calendar_manager.highlight_donation_dates()
            
            QMessageBox.information(self, "Successo", f"Database dell'anno {year} caricato con successo")
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nel caricamento dei database: {str(e)}")

    def handle_selection(self, option):
        """Gestisce la selezione dell'opzione database"""
        self.selected_option = option
        
        try:
            if option == 1:  # Nuovo database locale
                if not self.main_window.database_dir_manager.setup_local_database():
                    return
                self.accept()
                
            elif option == 2:  # Database locale esistente
                if not self.main_window.database_dir_manager.open_local_database():
                    return
                self.accept()
                
            elif option == 3:  # Database cloud
                self._handle_cloud_database()
                
        except Exception as e:
            logger.error(f"Errore nella selezione del database: {str(e)}")
            QMessageBox.critical(
                self,
                "Errore",
                f"Errore nella selezione del database:\n{str(e)}"
            )

    def closeEvent(self, event):
        """Gestisce la chiusura del dialog"""
        try:
            # Ferma tutti i processi cloud prima di chiudere
            if hasattr(self.main_window, 'cloud_manager'):
                self.main_window.cloud_manager.cleanup()
            event.accept()
            
        except Exception as e:
            logger.error(f"Errore nella chiusura del dialog: {str(e)}")
            event.accept()

    def get_cloud_paths(self):
        """Restituisce i percorsi dei servizi cloud per il sistema operativo corrente"""
        system = platform.system()
        username = os.getlogin()
        home = os.path.expanduser("~")
        
        paths = {
            "OneDrive": [],
            "Google Drive": [],
            "iCloud": []
        }
        
        if system == "Windows":
            paths["OneDrive"] = [
                os.path.join(home, "OneDrive"),
                os.path.join(home, "OneDrive - Personal"),
                f"C:\\Users\\{username}\\OneDrive"
            ]
            paths["Google Drive"] = [
                os.path.join(home, "Google Drive"),
                os.path.join(home, "GoogleDrive"),
                f"C:\\Users\\{username}\\Google Drive",
                f"C:\\Users\\{username}\\GoogleDrive"
            ]
            paths["iCloud"] = [
                os.path.join(home, "iCloudDrive"),
                f"C:\\Users\\{username}\\iCloudDrive"
            ]
        elif system == "Darwin":  # macOS
            paths["OneDrive"] = [
                os.path.join(home, "OneDrive"),
                os.path.join(home, "Library", "CloudStorage", "OneDrive-Personal")
            ]
            paths["Google Drive"] = [
                os.path.join(home, "Google Drive"),
                os.path.join(home, "Library", "CloudStorage", "GoogleDrive")
            ]
            paths["iCloud"] = [
                os.path.join(home, "Library", "Mobile Documents", "com~apple~CloudDocs")
            ]
        
        return paths

    def _handle_cloud_database(self):
        """Gestisce la selezione del database cloud"""
        try:
<<<<<<< HEAD
            # Trova i servizi cloud installati
            available_services = []
            cloud_paths = self.get_cloud_paths()
            
            # Controlla ogni servizio
            for service_name, paths in cloud_paths.items():
                for path in paths:
                    if os.path.exists(path):
                        available_services.append((service_name, path))
                        break
            
            if not available_services:
                QMessageBox.warning(
                    self,
                    "Nessun servizio cloud",
                    "Nessun servizio cloud supportato trovato.\n"
                    "Installa OneDrive, Google Drive o iCloud per utilizzare questa funzionalità."
                )
                return
            
            # Crea il menu di selezione
            menu = QMenu(self)
            for service_name, path in available_services:
                action = menu.addAction(service_name)
                action.setData(path)
            
            # Mostra il menu
            pos = self.cloud_button.mapToGlobal(self.cloud_button.rect().bottomLeft())
            selected_action = menu.exec_(pos)
            
            if selected_action:
                service_name = selected_action.text()
                cloud_path = selected_action.data()
                
                # Crea la directory Hemodos nel percorso cloud se non esiste
                hemodos_cloud_path = os.path.join(cloud_path, "Hemodos")
                os.makedirs(hemodos_cloud_path, exist_ok=True)
                
                # Salva le impostazioni
                self.settings.setValue("cloud_service", service_name)
                self.settings.setValue("cloud_path", hemodos_cloud_path)
                self.selected_option = 3
=======
            # Inizializza Syncthing
            if not hasattr(self.main_window, 'syncthing_manager'):
                from core.managers.syncthing_manager import SyncthingManager
                self.main_window.syncthing_manager = SyncthingManager(self.main_window)
            
            # Configura Syncthing
            if self.main_window.syncthing_manager.setup_syncthing():
                # Salva le impostazioni
                self.settings.setValue("cloud_service", "Syncthing")
                self.selected_option = 3  # Imposta l'opzione cloud
>>>>>>> e96e87b7ca2acbc94ed418b25497070b11d1b288
                
                # Aggiorna il testo del pulsante
                self.syncthing_button.setText("Database su Syncthing (Configurato)")
                
                # Abilita il pulsante Avanti
                ok_button = self.buttons_layout.itemAt(1).widget()
                ok_button.setEnabled(True)
                
                # Mostra messaggio di successo
                self.main_window.status_manager.show_message(
                    "Syncthing configurato correttamente", 
                    3000
                )
            else:
                QMessageBox.warning(
                    self,
                    "Errore",
                    "Impossibile configurare Syncthing.\nVerifica che sia installato correttamente."
                )
                
        except Exception as e:
            logger.error(f"Errore nella configurazione cloud: {str(e)}")
            QMessageBox.critical(
                self,
                "Errore",
                f"Errore nella configurazione cloud:\n{str(e)}"
            )

    def accept(self):
        """Override del metodo accept per gestire la chiusura corretta"""
        try:
            # Ferma il monitoraggio prima di chiudere
            if hasattr(self.main_window, 'observer'):
                self.main_window.observer.stop()
                self.main_window.observer = None
            
            # Attendi che eventuali operazioni in sospeso siano completate
            QApplication.processEvents()
            
            # Chiama il metodo della classe base
            super().accept()
            
        except Exception as e:
            logger.error(f"Errore nella chiusura del dialog: {str(e)}")
            super().accept()

    def add_donation_date(self):
        """Aggiunge una data di donazione"""
        try:
            selected_date = self.donation_calendar.selectedDate()
            
            # Verifica che la data sia nell'anno corrente
            if selected_date.year() != self.current_year:
                QMessageBox.warning(
                    self,
                    "Attenzione",
                    "Puoi aggiungere date solo per l'anno corrente"
                )
                return
            
            # Formatta la data
            date_str = selected_date.toString("yyyy-MM-dd")
            
            # Usa get_db_path per ottenere il percorso corretto
            base_path = get_base_path()
            year_path = os.path.join(base_path, str(self.current_year))
            
            # Crea la directory se non esiste
            os.makedirs(year_path, exist_ok=True)
            
            # Percorso del database delle date di donazione
            db_path = os.path.join(year_path, f"date_donazione_{self.current_year}.db")
            
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            
            # Crea la tabella se non esiste
            c.execute('''CREATE TABLE IF NOT EXISTS donation_dates
                         (date text PRIMARY KEY)''')
            
            # Inserisci la data
            try:
                c.execute("INSERT INTO donation_dates (date) VALUES (?)", (date_str,))
                conn.commit()
                
                # Aggiorna la lista
                self.load_donation_dates()
                
                # Aggiorna il calendario principale se esiste
                if hasattr(self, 'parent') and self.parent:
                    self.parent().calendar_manager.highlight_donation_dates()
                
                QMessageBox.information(
                    self,
                    "Successo",
                    f"Data di donazione aggiunta: {selected_date.toString('dd/MM/yyyy')}"
                )
                
            except sqlite3.IntegrityError:
                QMessageBox.warning(
                    self,
                    "Attenzione",
                    "Questa data è già presente nel calendario donazioni"
                )
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Errore nell'aggiunta della data di donazione: {str(e)}")
            QMessageBox.critical(
                self,
                "Errore",
                f"Errore nell'aggiunta della data di donazione: {str(e)}"
            )