from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtGui import QPixmap, QIcon, QFont
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QPushButton, QVBoxLayout, QDialog, QMessageBox
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
                "Per iniziare, clicca sul manuale o sul database per aprire la configurazione.\n"
                "Dovrai scegliere:\n"
                "• Il tipo di database (locale o sincronizzato con Syncthing).\n"
                "• La struttura per l'anno corrente.\n"
                "• Le date di donazione.\n\n"
                "Se hai bisogno di aiuto con Syncthing, puoi aprire il manuale utente qui sotto.\n\n"
                )

        self.content_layout.addWidget(welcome_text)
        
        # Aggiungi uno spazio elastico prima dei pulsanti
        self.content_layout.addStretch()       

        #Pulsante manuale
        manual_button = QPushButton("Apri Manuale")
        manual_button.setIcon(QIcon('src/assets/user_guide_64px.png'))  
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
        database_button.setIcon(QIcon('src/assets/database_64px.png'))  
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
            self.accept()  # Chiudi il FirstRunDialog se il database è configurato

    def closeEvent(self, event):
        """Gestisce la chiusura del dialog"""
        if self.first_run:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle('Conferma uscita')
            msg_box.setText('Vuoi davvero uscire? La configurazione non è completa.')
            msg_box.setIcon(QMessageBox.Question)
            
            # Crea i pulsanti personalizzati
            yes_button = msg_box.addButton("Sì", QMessageBox.YesRole)
            no_button = msg_box.addButton("No", QMessageBox.NoRole)
            msg_box.setDefaultButton(no_button)
            
            result = msg_box.exec_()
            
            if msg_box.clickedButton() == yes_button:
                event.accept()
                sys.exit()
            else:
                event.ignore()
        else:
            event.accept()
    
