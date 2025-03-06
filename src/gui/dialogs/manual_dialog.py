from gui.dialogs.base_dialog import HemodosDialog
from PyQt5.QtWidgets import (QVBoxLayout, QTabWidget, QWidget, QTextBrowser, 
                            QLabel, QScrollArea, QPushButton, QHBoxLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont, QIcon
import os

class ManualDialog(HemodosDialog):
    def __init__(self, parent=None):
        super().__init__(parent, "Manuale Utente")
        self.setMinimumSize(800, 600)
        self.init_ui()

    def init_ui(self):
        # Crea un tab widget per organizzare le sezioni
        tab_widget = QTabWidget()

        # Aggiungi le varie sezioni
        tab_widget.addTab(self.create_overview_tab(), "Panoramica")
        tab_widget.addTab(self.create_calendar_tab(), "Calendario")
        tab_widget.addTab(self.create_reservations_tab(), "Prenotazioni")
        tab_widget.addTab(self.create_tools_tab(), "Strumenti")
        tab_widget.addTab(self.create_settings_tab(), "Impostazioni")
        tab_widget.addTab(self.create_shortcuts_tab(), "Scorciatoie")
        tab_widget.addTab(self.create_admin_tab(), "HemodosAdmin")

        self.content_layout.addWidget(tab_widget)

        # Crea i pulsanti
        manual_button = QPushButton("Manuale")
        info_button = QPushButton("Info")
        database_button = QPushButton("Database")

        # Imposta le icone
        manual_button.setIcon(QIcon(self.paths_manager.get_asset_path('user_guide_64px.png')))
        info_button.setIcon(QIcon(self.paths_manager.get_asset_path('info_64px.png')))
        database_button.setIcon(QIcon(self.paths_manager.get_asset_path('database_64px.png')))

        # Aggiungi i pulsanti al layout
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(manual_button)
        buttons_layout.addWidget(info_button)
        buttons_layout.addWidget(database_button)
        self.content_layout.addLayout(buttons_layout)

    def create_overview_tab(self):
        content = """
        <h2>Hemodos</h2>
        <p>Hemodos è un software completo per la gestione delle donazioni di sangue, progettato per semplificare 
        il processo di prenotazione e monitoraggio delle donazioni.</p>

        <h3>Caratteristiche principali:</h3>
        <ul>
            <li>Gestione completa delle prenotazioni per le donazioni</li>
            <li>Calendario interattivo con evidenziazione delle date di donazione</li>
            <li>Sistema di gestione delle prime donazioni</li>
            <li>Tracciamento dello stato delle donazioni</li>
            <li>Statistiche dettagliate</li>
            <li>Esportazione dati in formato DOCX</li>
            <li>Sistema cloud integrato per la sincronizzazione dei dati</li>
            <li>Gestione utenti sicura con crittografia</li>
            <li>Backup automatico dei dati</li>
            <li>Gestione multi-anno con archivio storico</li>
            <li>Sistema di cronologia con tracciamento modifiche</li>
        </ul>

        <h3>Primo Avvio:</h3>
        <p>Al primo avvio, verrai guidato attraverso:</p>
        <ul>
            <li>Configurazione del percorso cloud per i dati</li>
            <li>Creazione o accesso al tuo account utente</li>
            <li>Impostazione delle date di donazione</li>
            <li>Personalizzazione delle preferenze</li>
        </ul>
        """
        return self.create_text_tab(content)

    def create_calendar_tab(self):
        content = """
        <h2>Utilizzo del Calendario</h2>

        <h3>Visualizzazione</h3>
        <ul>
            <li>Le date con donazioni programmate sono evidenziate in verde</li>
            <li>Clic su una data per visualizzare/modificare le prenotazioni</li>
            <li>Menu contestuale disponibile con clic destro sulla data</li>
            <li>Sincronizzazione automatica con il cloud</li>
        </ul>

        <h3>Funzionalità del menu contestuale:</h3>
        <ul>
            <li><b>Aggiungi Orario</b>: Inserisce un nuovo slot orario per le donazioni</li>
            <li><b>Salva</b>: Salva le modifiche correnti</li>
            <li><b>Esporta in DOCX</b>: Esporta le prenotazioni del giorno in formato Word</li>
            <li><b>Stampa</b>: Stampa le prenotazioni del giorno selezionato</li>
        </ul>
        """
        return self.create_text_tab(content)

    def create_reservations_tab(self):
        content = """
        <h2>Gestione Prenotazioni</h2>

        <h3>Tabella Prenotazioni</h3>
        <p>La tabella mostra le seguenti informazioni per ogni prenotazione:</p>
        <ul>
            <li><b>Orario</b>: Ora della donazione</li>
            <li><b>Nome</b>: Nome del donatore</li>
            <li><b>Cognome</b>: Cognome del donatore</li>
            <li><b>Prima Donazione</b>: Indica se è la prima donazione del donatore</li>
            <li><b>Stato</b>: Stato della donazione (Non effettuata/Sì/Annullata/Rimandata)</li>
        </ul>

        <h3>Modifica Prenotazioni</h3>
        <ul>
            <li>Doppio clic su una cella per modificare i dati</li>
            <li>Checkbox per segnare le prime donazioni</li>
            <li>Menu a tendina per aggiornare lo stato</li>
            <li>Pulsante di reset per cancellare una prenotazione</li>
            <li>Sincronizzazione automatica delle modifiche</li>
        </ul>

        <h3>Salvataggio</h3>
        <ul>
            <li>Automatico ogni 5 minuti (configurabile)</li>
            <li>Manuale tramite pulsante "Salva" o Ctrl+S</li>
            <li>Sincronizzazione immediata con il cloud</li>
            <li>Conferma al momento della chiusura</li>
        </ul>
        """
        return self.create_text_tab(content)

    def create_tools_tab(self):
        content = """
        <h2>Strumenti Disponibili</h2>

        <h3>Cronologia</h3>
        <p>Visualizza lo storico completo delle modifiche e delle operazioni effettuate:</p>
        <ul>
            <li>Registro dettagliato di tutte le modifiche</li>
            <li>Filtro per anno</li>
            <li>Possibilità di eliminare la cronologia dell'anno corrente</li>
            <li>Tracciamento automatico delle modifiche</li>
            <li>Sincronizzazione della cronologia tra utenti</li>
        </ul>

        <h3>Statistiche</h3>
        <p>Fornisce analisi dettagliate su:</p>
        <ul>
            <li>Donazioni mensili</li>
            <li>Donazioni trimestrali</li>
            <li>Totali annuali</li>
            <li>Prime donazioni</li>
            <li>Percentuali di completamento</li>
            <li>Confronto tra anni diversi</li>
            <li>Esportazione statistiche in vari formati</li>
        </ul>

        <h3>Gestione Database</h3>
        <ul>
            <li>Database centralizzato nel cloud</li>
            <li>Gestione multi-anno</li>
            <li>Backup automatico</li>
            <li>Sincronizzazione tra dispositivi</li>
            <li>Protezione dati con crittografia</li>
            <li>Gestione permessi utente</li>
        </ul>
        """
        return self.create_text_tab(content)

    def create_settings_tab(self):
        content = """
        <h2>Impostazioni</h2>

        <h3>Generali</h3>
        <ul>
            <li>Gestione date di donazione</li>
            <li>Configurazione orari disponibili</li>
            <li>Personalizzazione intervalli</li>
            <li>Gestione utenti e permessi</li>
        </ul>

        <h3>Cloud</h3>
        <ul>
            <li>Configurazione percorso cloud</li>
            <li>Gestione sincronizzazione</li>
            <li>Impostazioni backup</li>
            <li>Gestione accessi utente</li>
        </ul>

        <h3>Aspetto</h3>
        <ul>
            <li>Selezione tema (Chiaro/Scuro)</li>
            <li>Personalizzazione colori</li>
            <li>Configurazione font</li>
        </ul>

        <h3>Salvataggio</h3>
        <ul>
            <li>Attivazione/disattivazione autosave</li>
            <li>Configurazione intervallo di salvataggio</li>
            <li>Impostazioni backup</li>
            <li>Sincronizzazione automatica</li>
        </ul>
        """
        return self.create_text_tab(content)

    def create_shortcuts_tab(self):
        content = """
        <h2>Scorciatoie da Tastiera</h2>

        <h3>Generali</h3>
        <ul>
            <li><b>Ctrl+S</b>: Salva modifiche</li>
            <li><b>Ctrl+P</b>: Stampa</li>
            <li><b>Ctrl+E</b>: Esporta in DOCX</li>
            <li><b>F1</b>: Mostra informazioni</li>
            <li><b>Ctrl+Q</b>: Chiudi applicazione</li>
            <li><b>Ctrl+U</b>: Gestione utenti</li>
        </ul>

        <h3>Calendario</h3>
        <ul>
            <li><b>Ctrl+T</b>: Aggiungi nuovo orario</li>
            <li><b>Frecce</b>: Navigazione date</li>
            <li><b>Ctrl+PagUp/PagDown</b>: Cambia mese</li>
        </ul>

        <h3>Tabella</h3>
        <ul>
            <li><b>Tab</b>: Sposta tra le celle</li>
            <li><b>Enter</b>: Modifica cella</li>
            <li><b>Esc</b>: Annulla modifica</li>
            <li><b>Canc</b>: Cancella contenuto</li>
            <li><b>Ctrl+F</b>: Cerca</li>
        </ul>
        """
        return self.create_text_tab(content)

    def create_admin_tab(self):
        content = """
        <h2>HemodosAdmin</h2>
        <p>HemodosAdmin è l'interfaccia di amministrazione di Hemodos che permette la gestione completa 
        del sistema e degli utenti.</p>

        <h3>Primo Accesso</h3>
        <p>Al primo avvio, viene creato automaticamente un account amministratore con le seguenti credenziali:</p>
        <ul>
            <li><b>Username:</b> admin</li>
            <li><b>Password:</b> admin123</li>
        </ul>
        <p><b>IMPORTANTE:</b> Per motivi di sicurezza, si raccomanda di cambiare immediatamente la password 
        al primo accesso.</p>

        <h3>Funzionalità Amministrative</h3>
        <ul>
            <li>Gestione completa degli utenti:
                <ul>
                    <li>Creazione nuovi account</li>
                    <li>Modifica permessi</li>
                    <li>Reset password</li>
                    <li>Disattivazione account</li>
                </ul>
            </li>
            <li>Gestione del database:
                <ul>
                    <li>Backup manuale</li>
                    <li>Ripristino dati</li>
                    <li>Pulizia archivi</li>
                    <li>Ottimizzazione</li>
                </ul>
            </li>
            <li>Configurazione sistema:
                <ul>
                    <li>Impostazioni cloud</li>
                    <li>Policy di sicurezza</li>
                    <li>Parametri di sistema</li>
                    <li>Gestione backup automatici</li>
                </ul>
            </li>
            <li>Monitoraggio:
                <ul>
                    <li>Log di sistema</li>
                    <li>Attività utenti</li>
                    <li>Stato sincronizzazione</li>
                    <li>Performance sistema</li>
                </ul>
            </li>
        </ul>

        <h3>Sicurezza</h3>
        <ul>
            <li>Tutte le password sono crittografate con algoritmi sicuri</li>
            <li>I dati sensibili sono protetti con crittografia</li>
            <li>Le sessioni admin hanno timeout di sicurezza</li>
            <li>Viene mantenuto un log dettagliato delle operazioni amministrative</li>
        </ul>

        <h3>Best Practices</h3>
        <ul>
            <li>Cambiare regolarmente la password admin</li>
            <li>Creare account individuali per ogni amministratore</li>
            <li>Utilizzare password complesse (minimo 8 caratteri, maiuscole, numeri e simboli)</li>
            <li>Effettuare backup regolari del database</li>
            <li>Controllare periodicamente i log di sistema</li>
            <li>Mantenere aggiornato il software</li>
        </ul>
        """
        return self.create_text_tab(content)

    def create_text_tab(self, content):
        tab = QWidget()
        layout = QVBoxLayout()
        
        text_browser = QTextBrowser()
        text_browser.setOpenExternalLinks(True)
        text_browser.setHtml(content)
        
        # Applica stile al testo
        text_browser.setStyleSheet("""
            QTextBrowser {
                border: none;
                background-color: transparent;
                font-size: 14px;
                line-height: 1.6;
            }
        """)
        
        layout.addWidget(text_browser)
        tab.setLayout(layout)
        return tab 