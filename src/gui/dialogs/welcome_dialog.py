from gui.dialogs.base_dialog import HemodosDialog
from PyQt5.QtWidgets import (QVBoxLayout, QLabel, QPushButton, 
                            QHBoxLayout, QCheckBox)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QPixmap, QFont

class WelcomeDialog(HemodosDialog):
    def __init__(self, parent=None):
        super().__init__(parent, "Bentornato in Hemodos")
        self.settings = QSettings('Hemodos', 'DatabaseSettings')
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
        title = QLabel("Bentornato in Hemodos")
        title.setFont(QFont('Arial', 36, QFont.Bold))
        title.setStyleSheet("color: #004d4d;")
        title.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(title)
        
        # Messaggio di benvenuto
        welcome_text = QLabel()
        welcome_text.setFont(QFont('Arial', 16))
        welcome_text.setStyleSheet("color: #ffffff;")
        welcome_text.setText(
            "Grazie per aver scelto Hemodos!\n\n"
            "Questo software ti aiuterà a gestire le prenotazioni "
            "per le donazioni di sangue in modo semplice ed efficiente.\n\n"
            "Prima di iniziare, ti consigliamo di:\n"
            "• Configurare le impostazioni di base\n"
            "• Creare la struttura per l'anno corrente\n"
            "• Impostare le date di donazione\n"
        )
        welcome_text.setWordWrap(True)
        welcome_text.setStyleSheet("color: #ffffff;")
        welcome_text.setAlignment(Qt.AlignLeft)
        self.content_layout.addWidget(welcome_text)
        
        # Checkbox "Non mostrare più"
        self.show_again_cb = QCheckBox("Non mostrare più questo messaggio")
        self.show_again_cb.setStyleSheet("color: #ffffff;")
        self.content_layout.addWidget(self.show_again_cb)

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
        self.content_layout.addWidget(copyright_label)

        
        # Pulsanti
        buttons_layout = QHBoxLayout()
        
        settings_btn = QPushButton("Apri Impostazioni")
        settings_btn.setStyleSheet(self.button_style)
        settings_btn.clicked.connect(self.open_settings)
        
        start_btn = QPushButton("Inizia")
        start_btn.setStyleSheet(self.button_style)
        start_btn.clicked.connect(self.accept)
        
        buttons_layout.addWidget(settings_btn)
        buttons_layout.addWidget(start_btn)
        
        self.content_layout.addLayout(buttons_layout)

    def open_settings(self):
        """Apre la finestra delle impostazioni"""
        from config.settings import SettingsDialog
        settings_dialog = SettingsDialog(self)
        settings_dialog.exec_()

    def accept(self):
        """Salva la preferenza e chiude"""
        if self.show_again_cb.isChecked():
            self.settings.setValue("show_welcome", False)
        super().accept() 