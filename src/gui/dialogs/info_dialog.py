from gui.dialogs.base_dialog import HemodosDialog
from PyQt5.QtWidgets import QTextBrowser, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont
import os

class InfoDialog(HemodosDialog):
    def __init__(self, parent=None):
        super().__init__(parent, "Informazioni su Hemodos")
        self.setMinimumSize(500, 500)
        self.resize(600, 600)
        self.init_ui()

    def init_ui(self):
        # Container principale
        main_container = QWidget()
        main_layout = QVBoxLayout(main_container)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 10, 20, 20)

        # Logo container
        logo_container = QWidget()
        logo_container.setFixedHeight(150)
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        
        # Aggiungi il logo
        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "logo_info.png")
        if not os.path.exists(logo_path):
            logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo_info.png")
        if not os.path.exists(logo_path):
            logo_path = "src/assets/logo_info.png"

        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            scaled_pixmap = pixmap.scaled(140, 140, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
        else:
            logo_label.setText("Logo non trovato")
            logo_label.setStyleSheet("QLabel { color: red; }")
        
        logo_layout.addWidget(logo_label)
        main_layout.addWidget(logo_container)

        # Contenuto
        info_text = QTextBrowser()
        info_text.setOpenExternalLinks(True)
        info_text.setStyleSheet("""
            QTextBrowser {
                border: none;
                background-color: transparent;
                font-size: 14px;
                line-height: 1.4;
                margin-top: 0px;
            }
        """)
        info_text.setHtml("""
            <p style='text-align: center;'>
            <b>Software per la Gestione delle Donazioni di Sangue</b>
            </p>
            
            <p>
            Hemodos è un'applicazione progettata per gestire e organizzare le prenotazioni 
            per le donazioni di sangue. Il nome deriva dal greco αἷμα (sangue) e δόσις (donazione).
            </p>
            
            <h3>Caratteristiche principali:</h3>
            <ul>
                <li>Gestione calendario donazioni</li>
                <li>Prenotazioni per fasce orarie</li>
                <li>Gestione prime donazioni</li>
                <li>Tracciamento stato donazioni</li>
                <li>Sincronizzazione cloud dei dati</li>
                <li>Statistiche e reportistica</li>
                <li>Sistema multi-utente sicuro</li>
            </ul>
            
            <h3>Requisiti di sistema:</h3>
                <li>Windows 10-11. macOS 13 o superiore (Apple Silicon)</li>       
            </ul>
            
            <p>Sviluppato da Emmanuele Pani</p>
            <p>© 2025 Emmanuele Pani - MIT License</p>
            <p>Versione: 1.0.9</p>
            <p><a href='https://github.com/emmanueleP/Hemodos'>GitHub</a></p>
        """)
        main_layout.addWidget(info_text)
        self.content_layout.addWidget(main_container)