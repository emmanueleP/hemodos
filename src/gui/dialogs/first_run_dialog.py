from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtGui import QPixmap, QIcon, QFont
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QPushButton, QVBoxLayout, QDialog, QMessageBox
from gui.dialogs.base_dialog import HemodosDialog
from gui.dialogs.database_dialog import ConfigDatabaseDialog
import sys
from core.paths_manager import PathsManager

class FirstRunDialog(HemodosDialog):
    def __init__(self, parent=None):
        super().__init__(parent, "Hemodos - Primo avvio")
        self.settings = QSettings('Hemodos', 'DatabaseSettings')
        self.first_run = True
        # Rimuovi ok e annulla da HemodosDialog
        for i in reversed(range(self.buttons_layout.count())):
            widget = self.buttons_layout.itemAt(i).widget()
            if isinstance(widget, QPushButton):
                widget.setParent(None)
                widget.deleteLater()
        # Assicurati che paths_manager sia inizializzato prima di init_ui
        self.paths_manager = PathsManager()
        self.init_ui()

    def init_ui(self):
        self.content_layout.addWidget(QLabel())
        # Logo
        logo_layout = QHBoxLayout()
        logo_label = QLabel()
        logo_path = self.paths_manager.get_asset_path('logo_info.png')
        logo_pixmap = QPixmap(logo_path)
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
                "Per iniziare, clicca sul manuale e poi su Configura database per aprire la configurazione.\n"
                "Dovrai fare il login con le credenziali admin o quelle fornite dal tuo amministratore.\n"
                "Trovi le credenziali admin per il primo accesso nel manuale.\n\n"
                )

        self.content_layout.addWidget(welcome_text)
        
        # Aggiungi uno spazio elastico prima dei pulsanti
        self.content_layout.addStretch()       

        #Pulsante manuale
        manual_button = QPushButton("Apri Manuale")
        manual_button.setIcon(QIcon(self.paths_manager.get_asset_path('user_guide_64px.png')))
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
        database_button = QPushButton("Configura database")
        database_button.setIcon(QIcon(self.paths_manager.get_asset_path('database_64px.png')))
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
        exit_button.setIcon(QIcon(self.paths_manager.get_asset_path('exit_64px.png')))
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
        manual_dialog = ManualDialog(self)
        manual_dialog.exec_()
    
    def show_info_dialog(self):
        from gui.dialogs.info_dialog import InfoDialog
        info_dialog = InfoDialog(self)
        info_dialog.exec_()
    
    def show_database_dialog(self):
        from gui.dialogs.database_dialog import ConfigDatabaseDialog
        database_dialog = ConfigDatabaseDialog(self.parent())
        if database_dialog.exec_() == QDialog.Accepted:
            # Mostra il WelcomeDialog per il login dell'admin
            from gui.dialogs.welcome_dialog import WelcomeDialog
            welcome = WelcomeDialog(self.parent())
            if welcome.exec_() == QDialog.Accepted:
                # Imposta first_run a False e rimuovi i flag temporanei
                self.settings.setValue("first_run", False)
                self.settings.remove("first_run_dialog_shown")
                self.settings.remove("database_configured")
                self.settings.sync()
                self.accept()  # Chiudi il FirstRunDialog se il login è avvenuto con successo
            else:
                sys.exit(0)  # Esci se l'utente annulla il login

    def closeEvent(self, event):
        """Gestisce la chiusura del dialog"""
        if self.first_run:
            reply = QMessageBox.question(
                self,
                'Conferma uscita',
                'Vuoi davvero uscire? La configurazione non è completa.',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                event.accept()
                sys.exit()
            else:
                event.ignore()
        else:
            event.accept()
    
