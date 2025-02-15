from gui.dialogs.base_dialog import HemodosDialog
from PyQt5.QtWidgets import (QVBoxLayout, QTabWidget, QWidget, QTextBrowser, 
                            QLabel, QScrollArea)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont, QIcon
import os

class ManualDialog(HemodosDialog):
    def __init__(self, parent=None):
        super().__init__(parent, "Manuale Utente")
        self.setMinimumSize(900, 700)
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

        # Aggiungi la tab per Syncthing
        syncthing_tab = QWidget()
        syncthing_layout = QVBoxLayout()
        
        syncthing_text = QTextBrowser()
        syncthing_text.setOpenExternalLinks(True)
        syncthing_text.setHtml("""
            <h2>Configurazione Syncthing</h2>
            
            <p>Hemodos utilizza Syncthing per sincronizzare i database tra diversi dispositivi in modo sicuro e privato.</p>
            
            <h3>Come funziona</h3>
            <p>Syncthing è un software di sincronizzazione file open source che permette di:</p>
            <ul>
                <li>Sincronizzare i database Hemodos tra più computer</li>
                <li>Mantenere i dati al sicuro senza dipendere da servizi cloud di terze parti</li>
                <li>Avere un backup automatico dei dati</li>
            </ul>
            
            <h3>Configurazione iniziale</h3>
            <ol>
                <li>Nella finestra di configurazione del database, seleziona "Database Sincronizzato (Syncthing)"</li>
                <li>Hemodos configurerà automaticamente Syncthing per te</li>
                <li>La cartella Hemodos verrà creata in Documenti e configurata per la sincronizzazione</li>
            </ol>
            
            <h3>Aggiungere un altro dispositivo</h3>
            <ol>
                <li>Apri le Impostazioni di Hemodos</li>
                <li>Vai alla tab "Sync"</li>
                <li>Copia l'ID del dispositivo corrente usando il pulsante "Copia"</li>
                <li>Sul nuovo dispositivo, installa Hemodos</li>
                <li>Configura il nuovo dispositivo con Syncthing</li>
                <li>Usa il pulsante "Aggiungi Dispositivo" e incolla l'ID copiato</li>
                <li>Accetta la richiesta di connessione su entrambi i dispositivi</li>
            </ol>
            
            <h3>Gestione della sincronizzazione</h3>
            <ul>
                <li>Lo stato della sincronizzazione è visibile nella barra di stato di Hemodos</li>
                <li>Puoi aprire l'interfaccia web di Syncthing per configurazioni avanzate</li>
                <li>La sincronizzazione avviene automaticamente quando ci sono modifiche</li>
            </ul>
            
            <h3>Risoluzione problemi</h3>
            <ul>
                <li>Se la sincronizzazione non funziona, verifica che entrambi i dispositivi siano accesi e connessi alla rete</li>
                <li>Usa il pulsante "Riavvia Syncthing" nelle impostazioni se necessario</li>
                <li>Controlla l'interfaccia web di Syncthing per messaggi di errore dettagliati</li>
            </ul>
            
            <p>Per maggiori informazioni su Syncthing, visita la <a href="https://docs.syncthing.net/">documentazione ufficiale</a>.</p>
        """)
        
        syncthing_layout.addWidget(syncthing_text)
        syncthing_tab.setLayout(syncthing_layout)
        
        # Aggiungi la tab al tab widget
        tab_widget.addTab(syncthing_tab, "Sincronizzazione")

        self.content_layout.addWidget(tab_widget)

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
            <li>Sincronizzazione sicura tra dispositivi tramite Syncthing</li>
            <li>Backup automatico dei dati</li>
            <li>Gestione multi-anno con archivio storico</li>
            <li>Sistema di cronologia con tracciamento modifiche</li>
        </ul>

        <h3>Primo Avvio:</h3>
        <p>Al primo avvio, verrai guidato attraverso:</p>
        <ul>
            <li>Configurazione del database (locale o sincronizzato)</li>
            <li>Impostazione delle date di donazione</li>
            <li>Personalizzazione delle preferenze</li>
        </ul>

        <h3>Gestione Database:</h3>
        <ul>
            <li><b>Database Locale</b>: Salva i dati solo sul computer corrente</li>
            <li><b>Database Sincronizzato</b>: Mantiene i dati sincronizzati tra più dispositivi usando Syncthing</li>
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
        </ul>

        <h3>Salvataggio</h3>
        <ul>
            <li>Automatico ogni 5 minuti (configurabile)</li>
            <li>Manuale tramite pulsante "Salva" o Ctrl+S</li>
            <li>Conferma al momento della chiusura</li>
        </ul>
        """
        return self.create_text_tab(content)

    def create_tools_tab(self):
        content = """
        <h2>Strumenti</h2>

        <h3>Gestione Database</h3>
        <ul>
            <li>Backup e ripristino dei dati</li>
            <li>Gestione della sincronizzazione</li>
            <li>Manutenzione del database</li>
        </ul>

        <h3>Esportazione</h3>
        <ul>
            <li>Esportazione in formato DOCX</li>
            <li>Stampa delle prenotazioni</li>
            <li>Generazione report</li>
        </ul>

        <h3>Sincronizzazione</h3>
        <ul>
            <li>Monitoraggio stato Syncthing</li>
            <li>Gestione dispositivi connessi</li>
            <li>Risoluzione problemi di sincronizzazione</li>
        </ul>
        """
        return self.create_text_tab(content)

    def create_settings_tab(self):
        content = """
        <h2>Impostazioni</h2>

        <h3>Generali</h3>
        <ul>
            <li>Gestione delle date di donazione</li>
            <li>Configurazione degli anni disponibili</li>
            <li>Personalizzazione del tema dell'applicazione</li>
        </ul>

        <h3>Sincronizzazione</h3>
        <ul>
            <li>Gestione della sincronizzazione tramite Syncthing</li>
            <li>Aggiunta di dispositivi per la sincronizzazione</li>
            <li>Monitoraggio dello stato della sincronizzazione</li>
        </ul>

        <h3>Salvataggio</h3>
        <ul>
            <li>Configurazione del salvataggio automatico</li>
            <li>Impostazione dell'intervallo di salvataggio</li>
            <li>Gestione dei backup</li>
        </ul>

        <h3>Stampa</h3>
        <ul>
            <li>Personalizzazione del logo per la stampa</li>
            <li>Configurazione del formato di stampa</li>
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