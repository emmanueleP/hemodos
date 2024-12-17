from dialog_base import HemodosDialog
from PyQt5.QtWidgets import QTextBrowser
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont

class InfoDialog(HemodosDialog):
    def __init__(self, parent=None):
        super().__init__(parent, "Informazioni su Hemodos")
        self.setMinimumSize(600, 600)
        self.resize(700, 700)
        self.init_ui()

    def init_ui(self):
        info_text = QTextBrowser()
        info_text.setOpenExternalLinks(True)
        info_text.setStyleSheet("""
            QTextBrowser {
                border: none;
                background-color: transparent;
                font-size: 14px;
                line-height: 1.4;
            }
        """)
        info_text.setHtml("""
            <p style='text-align: center;'>
            <b>Software per la Gestione delle Donazioni di Sangue</b>
            </p>
            <p>Aristotele, <i>Historia Animalium 3.19</i>: "τὰ δ᾽ ἔχοντα αἷμα ζωογονοῦσιν" ("gli animali che hanno sangue generano vita").</p>
            
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
                <li>RAM minimum: ~4GB</li>          
            </ul>
            
            <h3>Developed by:</h3>
            <p>Emmanuele Pani<br>
            <p>To report bugs or suggest improvements, please use the GitHub repository.</p>
            
            <h3>License:</h3>
            <p>© 2024 Emmanuele Pani. Under MIT License.</p>
            <a href='https://github.com/emmanueleP/Hemodos'>GitHub</a>
            
            <h3>Version:</h3>
            <p>1.0.0</p>
        """)
        self.content_layout.addWidget(info_text) 