from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtGui import QPixmap, QIcon, QFont
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QPushButton, QVBoxLayout
from gui.dialogs.base_dialog import HemodosDialog
from gui.dialogs.database_dialog import ConfigDatabaseDialog
import sys

class FirstRunDialog(HemodosDialog):
    def __init__(self, parent=None):
        super().__init__(parent, "Hemodos - Primo avvio")
        self.settings = QSettings('Hemodos', 'DatabaseSettings')
        self.first_run = True
        #Rimuovi ok e annulla da HemodosDialog
        for i in reversed(range(self.buttons_layout.count())):
            widget = self.buttons_layout.itemAt(i).widget()
            if isinstance(widget, QPushButton):
                widget.setParent(None)
                widget.deleteLater()
        self.init_ui()

    def init_ui(self):
        self.content_layout.addWidget(QLabel())
        # Logo
        logo_layout = QHBoxLayout()
        logo_label = QLabel()
        logo_pixmap = QPixmap('src/assets/logo_info.png')
        logo_label.setPixmap(logo_pixmap.scaled(500, 500, Qt.KeepAspectRatio))
        logo_layout.addWidget(logo_label, alignment=Qt.AlignCenter)
        self.content_layout.addLayout(logo_layout)

        # Titolo
        title = QLabel("Benvenuto in Hemodos")
        title.setFont(QFont('Arial', 30, QFont.Bold))
        title.setStyleSheet("color: #004d4d;")
        title.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(title)
        
        # Messaggio
        welcome_text = QLabel()
        welcome_text.setFont(QFont('Arial', 14))
        welcome_text.setStyleSheet("color: #ffffff;")
        
        if self.first_run:
            welcome_text.setText(
                "Benvenuto in Hemodos!\n\n"
                "Per iniziare, clicca sul manuale o sul database per aprire la configurazione.\n"
                "Potrai scegliere:\n"
                "• Il tipo di database (locale o cloud).\n"
                "• La struttura per l'anno corrente.\n"
                "• Le date di donazione.\n\n"
                )

        self.content_layout.addWidget(welcome_text)
        
        # Aggiungi uno spazio elastico prima dei pulsanti
        self.content_layout.addStretch()       

        #Pulsante manuale
        manual_button = QPushButton()
        manual_button.setIcon(QIcon('src/assets/user_guide_64px.png'))  # Assicurati di avere questa icona
        manual_button.setToolTip("Apri Manuale")
        manual_button.setStyleSheet("""
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
        manual_button.clicked.connect(self.show_manual_dialog)
        self.buttons_layout.addWidget(manual_button)

        #Pulsante configurazione database
        database_button = QPushButton()
        database_button.setIcon(QIcon('src/assets/database_64px.png'))  # Assicurati di avere questa icona
        database_button.setToolTip("Configura il database")
        database_button.setStyleSheet("""
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
        database_button.clicked.connect(self.show_database_dialog)
        self.buttons_layout.addWidget(database_button)

        #Pulsante esci
        exit_button = QPushButton("Esci")
        exit_button.setIcon(QIcon('src/assets/exit_64px.png'))
        exit_button.setStyleSheet("""
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
        exit_button.clicked.connect(sys.exit)
        self.buttons_layout.addWidget(exit_button)

        self.buttons_layout.addStretch()

    def check_and_accept(self):
        if self.first_run:
            self.accept()
        else:
            self.close()
    
    def show_manual_dialog(self):
        from gui.dialogs.manual_dialog import ManualDialog
        manual_dialog = ManualDialog()
        manual_dialog.exec_()
    
    def show_info_dialog(self):
        from gui.dialogs.info_dialog import InfoDialog
        info_dialog = InfoDialog()
        info_dialog.exec_()
    
    def show_database_dialog(self):
        from gui.dialogs.database_dialog import ConfigDatabaseDialog
        database_dialog = ConfigDatabaseDialog()
        database_dialog.exec_()

    def closeEvent(self, event):
        """Chiude l'applicazione"""
        sys.exit()
    
