from gui.dialogs.base_dialog import HemodosDialog
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QRadioButton, QButtonGroup, QFileDialog,
                            QMessageBox, QGroupBox, QWidget)
from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtGui import QIcon, QPixmap
import os
from core.database import get_db_path

class FirstRunDialog(HemodosDialog):
    def __init__(self, parent=None):
        super().__init__(parent, "Benvenuto in Hemodos")
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
            logo_path = "assets/logo_info.png"

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

        # Opzione 3: OneDrive
        onedrive_radio = QRadioButton("Usa OneDrive")
        self.button_group.addButton(onedrive_radio, 3)
        options_layout.addWidget(onedrive_radio)

        # Opzione 4: Google Drive
        gdrive_radio = QRadioButton("Usa Google Drive")
        self.button_group.addButton(gdrive_radio, 4)
        options_layout.addWidget(gdrive_radio)

        options_group.setLayout(options_layout)
        main_layout.addWidget(options_group)

        self.content_layout.addWidget(main_container)

    def check_and_accept(self):
        selected_button = self.button_group.checkedButton()
        if not selected_button:
            QMessageBox.warning(self, "Errore", "Seleziona un'opzione")
            return

        self.selected_option = self.button_group.id(selected_button)
        self.accept() 