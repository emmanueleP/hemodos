from dialog_base import HemodosDialog
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QRadioButton, QButtonGroup, QFileDialog,
                            QMessageBox, QGroupBox)
from PyQt5.QtCore import QSettings
import os

class FirstRunDialog(HemodosDialog):
    def __init__(self, parent=None):
        super().__init__(parent, "Benvenuto in Hemodos")
        self.settings = QSettings('Hemodos', 'DatabaseSettings')
        self.selected_option = None
        self.init_ui()

    def init_ui(self):
        # Messaggio di benvenuto
        welcome_label = QLabel("Scegli come vuoi gestire il database:")
        welcome_label.setStyleSheet("font-size: 14px;")
        self.content_layout.addWidget(welcome_label)

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
        self.content_layout.addWidget(options_group)

    def check_and_accept(self):
        selected_button = self.button_group.checkedButton()
        if not selected_button:
            QMessageBox.warning(self, "Errore", "Seleziona un'opzione")
            return

        self.selected_option = self.button_group.id(selected_button)
        self.accept() 