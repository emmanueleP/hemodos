from gui.dialogs.base_dialog import HemodosDialog
from PyQt5.QtWidgets import (QVBoxLayout, QLabel, QPushButton, 
                            QHBoxLayout, QCheckBox, QDialog, QApplication)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QPixmap, QFont, QIcon
from gui.dialogs.database_dialog import ConfigDatabaseDialog
import sys


class WelcomeDialog(HemodosDialog):
    def __init__(self, parent=None):
        super().__init__(parent, "Bentornato in Hemodos")
        self.settings = QSettings('Hemodos', 'DatabaseSettings')
        #Rimuovi ok e annulla da HemodosDialog
        for i in reversed(range(self.buttons_layout.count())):
            widget = self.buttons_layout.itemAt(i).widget()
            if isinstance(widget, QPushButton):
                widget.setParent(None)
                widget.deleteLater()
        
        self.init_ui()
      
    def init_ui(self):
        # Logo
        logo_layout = QHBoxLayout()
        logo_label = QLabel()
        logo_pixmap = QPixmap('assets/logo_info.png')
        logo_label.setPixmap(logo_pixmap.scaled(100, 100, Qt.KeepAspectRatio))
        logo_layout.addWidget(logo_label, alignment=Qt.AlignCenter)
        self.content_layout.addLayout(logo_layout)
        
        # Titolo
        title = QLabel("Bentornato in Hemodos")
        title.setFont(QFont('Arial', 30, QFont.Bold))
        title.setStyleSheet("color: #004d4d;")
        title.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(title)
        
        # Messaggio
        welcome_text = QLabel()
        welcome_text.setFont(QFont('Arial', 14))
        welcome_text.setStyleSheet("color: white;")
        
        
        welcome_text.setText(
                "Bentornato in Hemodos!\n\n"
                "Clicca su 'Apri database' per aprire il database:\n"
                "Puoi modificare le impostazioni in qualsiasi momento\n"
                "dal menu Impostazioni.\n"
                "Clicca su 'Esci' per uscire."
            )
        
        welcome_text.setWordWrap(True)
        welcome_text.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(welcome_text)
        

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
        manual_btn.setIcon(QIcon('assets/user_guide_64px.png')) #icona 64 px
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
        
        open_button = QPushButton("Apri database")
        open_button.setIcon(QIcon('assets/database_64px.png')) #icona 64 px
        open_button.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                border: none;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #00a3a3;
                border-radius: 3px;
            }
        """)
        open_button.clicked.connect(self.open_button)
        buttons_layout.addWidget(open_button)

        exit_button = QPushButton("Esci")
        exit_button.setIcon(QIcon('assets/exit_64px.png')) #icona 64 px
        exit_button.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                border: none;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #00a3a3;
                border-radius: 3px;
            }
        """)
        exit_button.clicked.connect(self.exit_button)
        buttons_layout.addWidget(exit_button)
        
        self.content_layout.addLayout(buttons_layout)

    def open_button(self):
        """Apre l'applicazione"""
        self.done(QDialog.Accepted) #Chiude il dialog definitivamente

    def exit_button(self):
        """Chiude l'applicazione completamente"""
        QApplication.quit()

    def show_manual(self):
        """Apre la finestra del manuale"""
        from gui.dialogs.manual_dialog import ManualDialog
        manual = ManualDialog(self)
        manual.exec_() 