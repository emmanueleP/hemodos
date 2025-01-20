from gui.dialogs.base_dialog import HemodosDialog
from PyQt5.QtWidgets import QTextBrowser, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont
import os
from core.database import get_db_path

class InfoDialog(HemodosDialog):
    def __init__(self, parent=None):
        super().__init__(parent, "Informazioni su Hemodos")
        self.setMinimumSize(600, 600)
        self.resize(700, 700)
        self.init_ui()

    def init_ui(self):
        # Container principale
        main_container = QWidget()
        main_layout = QVBoxLayout(main_container)
        main_layout.setSpacing(10)  # Riduci lo spazio tra gli elementi
        main_layout.setContentsMargins(20, 10, 20, 20)  # Riduci i margini

        # Logo container
        logo_container = QWidget()
        logo_container.setFixedHeight(160)  # Riduci l'altezza del container
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        
        # Aggiungi il logo
        logo_label = QLabel()
        # Usa il percorso relativo alla directory dell'applicazione
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "logo_info.png")
        if not os.path.exists(logo_path):
            logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo_info.png")
        if not os.path.exists(logo_path):
            logo_path = "src/assets/logo_info.png"

        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            scaled_pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)  # Logo più piccolo
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
            <p>Aristotele, <i>Historia Animalium</i> 3.19: "τὰ δ᾽ ἔχοντα αἷμα ζωογονοῦσιν" ("gli animali che hanno sangue generano vita").</p>

            
            <p>
            Hemodos è un'applicazione progettata per gestire e organizzare le prenotazioni 
            per le donazioni di sangue.
            </p>
            <p>Αἱμοδός è un termine greco moderno che significa"donazione di sangue". L'idea del nome nasce dai miei studi di greco antico al liceo e all'università. In greco antico la parola non esiste, ma ha la sua origine dalle due parole: αἷμα (sangue) e δόσις (donazione).
            </p>              
            
            <h3>Caratteristiche principali:</h3>
            <ul>
                <li>Gestione calendario donazioni con evidenziazione delle date</li>
                <li>Prenotazioni per fasce orarie (7:50 - 12:10)</li>
                <li>Gestione automatica prime donazioni (disabilitate dopo le 10:00)</li>
                <li>Tracciamento stato donazioni (effettuata, non effettuata, ecc.)</li>
                <li>Supporto per salvataggio su cloud (OneDrive, Google Drive)</li>
                <li>Salvataggio automatico configurabile</li>
                <li>Esportazione dati in formato Word (.docx)</li>
                <li>Stampa documenti con layout personalizzato</li>
                <li>Possibilità di aggiungere logo personalizzato in cima al documento</li>
                <li>Cronologia completa delle modifiche</li>
                <li>Statistiche mensili, trimestrali e annuali delle donazioni</li>
                <li>Temi chiaro e scuro</li>
            </ul>
            
            <h3>Funzionalità avanzate:</h3>
            <ul>
                <li>Menu contestuale sul calendario per accesso rapido</li>
                <li>Gestione orari personalizzabili a intervalli di 5 minuti</li>
                <li>Sincronizzazione automatica con servizi cloud</li>
                <li>Backup automatico dei dati</li>
                <li>Gestione separata delle date di donazione</li>
                <li>Interfaccia intuitiva e responsive</li>
            </ul>
            
            <h3>System requirements:</h3>
            <ul>
                <li>Windows 10 or higher</li>
                <li>Disk space: ~100MB</li>
                <li>RAM minimum: ~2GB</li>          
            </ul>
            
            <h3>Developed by:</h3>
            <p>Emmanuele Pani<br>
            <p>To report bugs or suggest improvements, please use the GitHub repository.</p>
            
            <h3>License:</h3>
            <p>© 2025 Emmanuele Pani. Under MIT License.</p>
            <a href='https://github.com/emmanueleP/Hemodos'>GitHub</a>
            
            <h3>Version:</h3>
            <p>1.0.7</p>
        """)
        main_layout.addWidget(info_text)
        self.content_layout.addWidget(main_container)