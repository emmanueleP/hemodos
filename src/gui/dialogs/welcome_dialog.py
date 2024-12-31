from gui.dialogs.base_dialog import HemodosDialog
from PyQt5.QtWidgets import (QVBoxLayout, QLabel, QPushButton, 
                            QHBoxLayout, QCheckBox, QDialog)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QPixmap, QFont, QIcon
from gui.dialogs.database_dialog import FirstRunDialog

class WelcomeDialog(HemodosDialog):
    def __init__(self, parent=None, is_first_run=False):
        super().__init__(parent, "Benvenuto in Hemodos" if is_first_run else "Bentornato in Hemodos")
        self.settings = QSettings('Hemodos', 'DatabaseSettings')
        self.is_first_run = is_first_run
        self.init_ui()

    def init_ui(self):
        # Logo
        logo_layout = QHBoxLayout()
        logo_label = QLabel()
        logo_pixmap = QPixmap('assets/logo_info.png')
        logo_label.setPixmap(logo_pixmap.scaled(500, 500, Qt.KeepAspectRatio))
        logo_layout.addWidget(logo_label, alignment=Qt.AlignCenter)
        self.content_layout.addLayout(logo_layout)
        
        # Titolo
        title = QLabel("Benvenuto in Hemodos" if self.is_first_run else "Bentornato in Hemodos")
        title.setFont(QFont('Arial', 36, QFont.Bold))
        title.setStyleSheet("color: #004d4d;")
        title.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(title)
        
        # Messaggio
        welcome_text = QLabel()
        welcome_text.setFont(QFont('Arial', 14))
        welcome_text.setStyleSheet("color: #ffffff;")
        
        if self.is_first_run:
            welcome_text.setText(
                "Benvenuto in Hemodos!\n\n"
                "Per iniziare, dovrai configurare:\n"
                "• Il tipo di database (locale o cloud)\n"
                "• La struttura per l'anno corrente\n"
                "• Le date di donazione\n\n"
                "Clicca su 'Configura' per procedere."
            )
        else:
            welcome_text.setText(
                "Bentornato in Hemodos!\n\n"
                "Il tuo database è pronto all'uso.\n"
                "Puoi modificare le impostazioni in qualsiasi momento\n"
                "dal menu Impostazioni."
            )
        
        welcome_text.setWordWrap(True)
        welcome_text.setAlignment(Qt.AlignLeft)
        self.content_layout.addWidget(welcome_text)
        
        # Checkbox "Non mostrare più" (solo per bentornato)
        if not self.is_first_run:
            self.show_again_cb = QCheckBox("Non mostrare più questo messaggio")
            self.show_again_cb.setStyleSheet("color: #ffffff;")
            self.content_layout.addWidget(self.show_again_cb)

        # Copyright
        copyright_label = QLabel("© 2025 Emmanuele Pani. Under MIT License.")
        copyright_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 11px;
                padding: 10px;
            }
        """)
        copyright_label.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(copyright_label)
        
        # Pulsanti
        buttons_layout = QHBoxLayout()
        
        # Pulsante manuale (aggiunto a sinistra)
        manual_btn = QPushButton()
        manual_btn.setIcon(QIcon('assets/user_guide.png'))  # Assicurati di avere questa icona
        manual_btn.setToolTip("Apri Manuale")
        manual_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 3px;
            }
        """)
        manual_btn.clicked.connect(self.show_manual)
        buttons_layout.addWidget(manual_btn)
        
        buttons_layout.addStretch()  # Spazio flessibile tra i pulsanti
        
        if self.is_first_run:
            config_btn = QPushButton("Configura")
            config_btn.setStyleSheet(self.button_style)
            config_btn.clicked.connect(self.show_database_dialog)
            buttons_layout.addWidget(config_btn)
        else:
            settings_btn = QPushButton("Apri Impostazioni")
            settings_btn.setStyleSheet(self.button_style)
            settings_btn.clicked.connect(self.open_settings)
            
            start_btn = QPushButton("Inizia")
            start_btn.setStyleSheet(self.button_style)
            start_btn.clicked.connect(self.close)
            
            buttons_layout.addWidget(settings_btn)
            buttons_layout.addWidget(start_btn)
        
        self.content_layout.addLayout(buttons_layout)

    def show_database_dialog(self):
        """Mostra il dialog di configurazione database"""
        dialog = FirstRunDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.accept()

    def open_settings(self):
        """Apre la finestra delle impostazioni"""
        from config.settings import SettingsDialog
        settings_dialog = SettingsDialog(self)
        settings_dialog.exec_()

    def close(self):
        """Chiude il dialog e salva le preferenze"""
        if not self.is_first_run and hasattr(self, 'show_again_cb'):
            if self.show_again_cb.isChecked():
                self.settings.setValue("show_welcome", False)
        self.accept()

    def accept(self):
        """Salva la preferenza e chiude"""
        if not self.is_first_run and hasattr(self, 'show_again_cb'):
            if self.show_again_cb.isChecked():
                self.settings.setValue("show_welcome", False)
        super().accept()

    def show_manual(self):
        """Apre la finestra del manuale"""
        from gui.dialogs.manual_dialog import ManualDialog
        manual = ManualDialog(self)
        manual.exec_() 