from gui.dialogs.base_dialog import HemodosDialog
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QRadioButton, QButtonGroup, QFileDialog,
                            QMessageBox, QGroupBox, QWidget, QInputDialog)
from PyQt5.QtCore import QSettings, Qt, QDate
from PyQt5.QtGui import QIcon, QPixmap
import os
from core.database import get_db_path
from core.delete_db_logic import get_base_path
from core.logger import logger
from core.themes import THEMES
import sqlite3

class ConfigDatabaseDialog(HemodosDialog):
    def __init__(self, parent=None):
        super().__init__(parent, "Gestione database Hemodos")
        self.settings = QSettings('Hemodos', 'DatabaseSettings')
        self.selected_option = None
        self.init_ui()

    def init_ui(self):
        # Container principale
        main_container = QWidget()
        main_layout = QVBoxLayout(main_container)

        # Logo container
        logo_container = QWidget()
        logo_container.setFixedHeight(220)  # Altezza fissa per il logo
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)  # Rimuovi i margini
        
        # Aggiungi il logo
        logo_label = QLabel()
        # Usa il percorso relativo alla directory dell'applicazione
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "logo_info.png")
        # Prova percorsi alternativi se il primo fallisce
        if not os.path.exists(logo_path):
            logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo_info.png")
        if not os.path.exists(logo_path):
            logo_path = "src/assets/logo_info.png"

        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            scaled_pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
            print(f"Logo caricato con successo da: {logo_path}")
        else:
            logo_label.setText("Logo non trovato")
            logo_label.setStyleSheet("QLabel { color: red; }")
            print(f"Logo non trovato. Percorsi tentati:")
            print(f"1. {os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'logo_info.png')}")
            print(f"2. {os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'logo_info.png')}")
            print(f"3. assets/logo_info.png")
            print(f"Directory corrente: {os.getcwd()}")
        
        logo_layout.addWidget(logo_label)
        main_layout.addWidget(logo_container)

        # Resto del contenuto
        welcome_label = QLabel("Scegli come vuoi gestire il database:")
        welcome_label.setStyleSheet("font-size: 14px;")
        main_layout.addWidget(welcome_label)

        # Gruppo opzioni per il database
        options_group = QGroupBox("Opzioni Database")
        options_layout = QVBoxLayout()
        
        self.button_group = QButtonGroup()
        
        # Opzione 1: Nuovo database locale
        new_local_radio = QRadioButton("Crea nuovo database locale")
        self.button_group.addButton(new_local_radio, 1)
        options_layout.addWidget(new_local_radio)

        # Opzione 2: Database esistente locale
        existing_local_radio = QRadioButton("Apri database locale esistente")
        self.button_group.addButton(existing_local_radio, 2)
        options_layout.addWidget(existing_local_radio)

        # Opzione 3: Database esistente su cloud
        existing_cloud_radio = QRadioButton("Apri database esistente su cloud")
        self.button_group.addButton(existing_cloud_radio, 3)
        options_layout.addWidget(existing_cloud_radio)

        # Opzione 4: OneDrive
        onedrive_radio = QRadioButton("Crea nuovo database su OneDrive")
        self.button_group.addButton(onedrive_radio, 4)
        options_layout.addWidget(onedrive_radio)

        # Opzione 5: Google Drive
        gdrive_radio = QRadioButton("Crea nuovo database su Google Drive")
        self.button_group.addButton(gdrive_radio, 5)
        options_layout.addWidget(gdrive_radio)

        options_group.setLayout(options_layout)
        main_layout.addWidget(options_group)

        # Aggiungi il copyright
        copyright_label = QLabel("© 2025 Emmanuele Pani. Under MIT License.")
        copyright_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 11px;
                padding: 10px;
            }
        """)
        copyright_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(copyright_label)

        # Aggiungi uno spazio elastico prima dei pulsanti
        main_layout.addStretch()

        self.content_layout.addWidget(main_container)

        # Modifica i pulsanti
        self.buttons_layout.itemAt(1).widget().setText("Avanti")  
        self.buttons_layout.itemAt(2).widget().setText("Esci")    
        # Collega il pulsante Avanti alla verifica
        ok_button = self.buttons_layout.itemAt(1).widget()
        ok_button.clicked.disconnect()  # Disconnetti il vecchio segnale
        ok_button.clicked.connect(self.check_and_accept)

    def check_and_accept(self):
        selected_button = self.button_group.checkedButton()
        if not selected_button:
            QMessageBox.warning(self, "Errore", "Seleziona un'opzione")
            return

        self.selected_option = self.button_group.id(selected_button)
        
        try:
            if self.selected_option == 1:  # Nuovo database locale
                # Crea la directory Hemodos in Documenti
                base_path = os.path.expanduser("~/Documents/Hemodos")
                year_path = os.path.join(base_path, str(QDate.currentDate().year()))
                os.makedirs(year_path, exist_ok=True)
                self.settings.setValue("cloud_service", "Locale")
                
            elif self.selected_option == 2:  # Database locale esistente
                # Seleziona la cartella Hemodos
                base_path = QFileDialog.getExistingDirectory(
                    self, 
                    "Seleziona la cartella Hemodos",
                    os.path.expanduser("~/Documents")
                )
                if not base_path:
                    return
                    
                # Verifica se la cartella selezionata è un anno
                if os.path.basename(base_path).isdigit():
                    year = os.path.basename(base_path)
                    self.settings.setValue("selected_year", year)
                    self.settings.setValue("cloud_service", "Locale")
                    
                    # Carica i database dell'anno selezionato
                    self.load_year_databases(base_path, year)
                else:
                    QMessageBox.warning(self, "Errore", "Seleziona una cartella anno valida")
                    return
                
            elif self.selected_option == 3:  # Database esistente su cloud
                # Chiedi quale servizio cloud
                cloud_service = QMessageBox.question(
                    self,
                    "Seleziona Servizio Cloud",
                    "Quale servizio cloud vuoi utilizzare?",
                    "OneDrive|Google Drive",
                    defaultButtonNumber=0
                )
                
                cloud_path = None
                if cloud_service == 0:  # OneDrive
                    cloud_path = self._get_onedrive_path()
                    self.settings.setValue("cloud_service", "OneDrive")
                else:  # Google Drive
                    cloud_path = self._get_gdrive_path()
                    self.settings.setValue("cloud_service", "GoogleDrive")
                
                if not cloud_path:
                    QMessageBox.warning(self, "Errore", "Cartella cloud non trovata")
                    return
                
                # Seleziona la cartella Hemodos esistente
                hemodos_path = QFileDialog.getExistingDirectory(
                    self, 
                    "Seleziona la cartella Hemodos",
                    os.path.join(cloud_path, "Hemodos")
                )
                if hemodos_path:
                    self.settings.setValue("cloud_path", cloud_path)
                else:
                    return

            elif self.selected_option == 4:  # Nuovo database OneDrive
                onedrive_path = self._get_onedrive_path()
                if not onedrive_path:
                    QMessageBox.warning(self, "Errore", "Cartella OneDrive non trovata")
                    return
                base_path = os.path.join(onedrive_path, "Hemodos")
                year_path = os.path.join(base_path, str(QDate.currentDate().year()))
                os.makedirs(year_path, exist_ok=True)
                self.settings.setValue("cloud_service", "OneDrive")
                self.settings.setValue("cloud_path", onedrive_path)

            elif self.selected_option == 5:  # Nuovo database Google Drive
                gdrive_path = self._get_gdrive_path()
                if not gdrive_path:
                    QMessageBox.warning(self, "Errore", "Cartella Google Drive non trovata")
                    return
                base_path = os.path.join(gdrive_path, "Hemodos")
                year_path = os.path.join(base_path, str(QDate.currentDate().year()))
                os.makedirs(year_path, exist_ok=True)
                self.settings.setValue("cloud_service", "GoogleDrive")
                self.settings.setValue("cloud_path", gdrive_path)
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante la configurazione: {str(e)}")

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