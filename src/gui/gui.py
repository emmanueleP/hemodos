from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton, 
                            QLabel, QCalendarWidget, QTableWidget, QTableWidgetItem, 
                            QFileDialog, QMessageBox, QMenuBar, QMenu, QAction,
                            QDialog, QComboBox, QStatusBar, QShortcut, QGroupBox, QHBoxLayout)
from PyQt5.QtCore import Qt, QSettings, QDate, QTimer, QTime, QSize
from PyQt5.QtGui import QColor, QPalette, QTextCharFormat, QKeySequence, QPixmap, QIcon
from core.utils import export_to_docx, print_data
from core.database import (add_reservation, get_reservations, delete_reservation,
                     init_db, get_donation_dates, get_db_path, setup_cloud_monitoring, 
                     add_donation_time, save_donation_status, add_history_entry, reset_reservation)
from gui.dialogs.history_dialog import HistoryDialog
from gui.dialogs.info_dialog import InfoDialog
from gui.dialogs.database_dialog import FirstRunDialog
from gui.dialogs.delete_dialog import DeleteFilesDialog
from gui.dialogs.time_entry_dialog import TimeEntryDialog
from gui.dialogs.statistics_dialog import StatisticsDialog
from config.settings import SettingsDialog
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from datetime import datetime
import os
import sqlite3
from core.year_manager import YearManager
from core.logger import logger
from gui.widgets.reservations_widget import ReservationsWidget
from core.themes import THEMES

class MainWindow(QMainWindow):
    def __init__(self, config):
        super().__init__()
        self.settings = QSettings('Hemodos', 'DatabaseSettings')
        self.last_valid_date = QDate.currentDate()

        # Set window properties
        self.setWindowTitle("Hemodos - Prenotazioni Donazioni di Sangue")
        self.resize(1024, 768)
        self.setMinimumSize(800, 600)

        # Set theme and colors
        self.primary_color = "#004d4d"
        self.apply_theme()

        # Create menu bar
        self.create_menu_bar()

        # Create status bar
        self.create_status_bar()

        # Initialize UI
        self.init_ui()

        # Carica il database del giorno corrente
        self.load_current_day_database()

        # Evidenzia le date dopo che tutto è stato inizializzato
        self.highlight_donation_dates()

        # Aggiungi scorciatoia da tastiera per il salvataggio
        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        save_shortcut.activated.connect(self.save_reservations)

        # Setup autosave timer
        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self.auto_save)
        self.setup_autosave()

        # Setup cloud monitoring
        self.observer = setup_cloud_monitoring(self)

        # Inizializza il gestore anni
        self.year_manager = YearManager()
        self.year_manager.year_created.connect(self.on_year_created)
        self.year_manager.year_changed.connect(self.on_year_changed)

        # Aggiungi label per l'ultimo salvataggio
        self.last_save_label = QLabel()
        self.statusBar.addPermanentWidget(self.last_save_label)
        self.update_last_save_info()

    def create_menu_bar(self):
        menubar = self.menuBar()

        # Menu File
        file_menu = menubar.addMenu('File')
        
        # Add Time Entry action
        add_time_action = QAction('Aggiungi Orario', self)
        add_time_action.setShortcut('Ctrl+T')
        add_time_action.triggered.connect(self.show_time_entry_dialog)
        file_menu.addAction(add_time_action)
        
        # Azione di salvataggio con icona
        save_action = QAction(QIcon('assets/diskette.png'), 'Salva', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(lambda: self.save_reservations(show_message=True))
        file_menu.addAction(save_action)
        
        open_db_action = QAction('Apri Database...', self)
        open_db_action.triggered.connect(self.open_database)
        file_menu.addAction(open_db_action)
        
        new_db_action = QAction('Nuovo Database', self)
        new_db_action.triggered.connect(self.create_new_database)
        file_menu.addAction(new_db_action)
        
        close_db_action = QAction('Chiudi Database', self)
        close_db_action.setShortcut('Ctrl+E')
        close_db_action.triggered.connect(self.close_database)
        file_menu.addAction(close_db_action)
        
        file_menu.addSeparator()

        export_action = QAction(QIcon('assets/doc.png'), 'Esporta in Word (.docx)', self)
        export_action.setShortcut('Ctrl+W')
        export_action.triggered.connect(self.export_to_docx)
        file_menu.addAction(export_action)

        print_action = QAction(QIcon('assets/printer.png'), 'Stampa', self)
        print_action.setShortcut('Ctrl+P')
        print_action.triggered.connect(self.print_table)
        file_menu.addAction(print_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Esci', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close_app)
        file_menu.addAction(exit_action)

        # Menu Strumenti
        tools_menu = menubar.addMenu('Strumenti')
        
        history_action = QAction(QIcon('assets/history.png'), 'Cronologia', self)
        history_action.triggered.connect(self.show_history)
        tools_menu.addAction(history_action)
        
        delete_action = QAction(QIcon('assets/trash.png'), 'Elimina Database...', self)
        delete_action.triggered.connect(self.show_delete_dialog)
        tools_menu.addAction(delete_action)
        
        # Aggiungi separatore
        tools_menu.addSeparator()
        
        # Menu Impostazioni
        settings_menu = menubar.addMenu('Impostazioni')
        
        preferences_action = QAction('Preferenze', self)
        preferences_action.triggered.connect(self.show_settings)
        settings_menu.addAction(preferences_action)

        # Menu Info
        info_menu = menubar.addMenu('Info')
        
        manual_action = QAction('Manuale', self)
        manual_action.setShortcut('F1')
        manual_action.triggered.connect(self.show_manual)
        info_menu.addAction(manual_action)
        
        about_action = QAction('Informazioni su Hemodos', self)
        about_action.triggered.connect(self.show_info)
        info_menu.addAction(about_action)

        statistics_action = QAction(QIcon('assets/stats.png'), 'Statistiche', self)
        statistics_action.triggered.connect(self.show_statistics)
        tools_menu.addAction(statistics_action)

    def create_status_bar(self):
        """Crea la barra di stato"""
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        # Label per il database corrente
        self.db_label = QLabel()
        self.statusBar.addPermanentWidget(self.db_label)

    def update_db_info(self):
        """Aggiorna le informazioni del database mostrate nella barra di stato"""
        try:
            selected_date = self.calendar.selectedDate()
            year = selected_date.year()
            date_str = selected_date.toString("dd/MM/yyyy")
            
            # Ottieni il percorso del database
            db_path = get_db_path(selected_date)
            
            if os.path.exists(os.path.dirname(db_path)):
                self.db_label.setText(f"Database: {year} - {date_str}")
            else:
                self.db_label.setText(f"Database: {year} - {date_str} (Non esistente)")
                
        except Exception as e:
            logger.error(f"Errore nell'aggiornamento delle info del database: {str(e)}")
            self.db_label.setText("Errore info database")

    def create_new_database(self):
        reply = QMessageBox.question(self, 'Nuovo Database', 
                                   'Vuoi davvero creare un nuovo database? Questo cancellerà tutti i dati esistenti.',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            init_db()
            QMessageBox.information(self, "Database", "Nuovo database creato con successo.")
            self.load_default_times()

    def init_ui(self):
        """Inizializza l'interfaccia utente"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Toolbar con pulsanti
        toolbar = QHBoxLayout()
        
        # Pulsante Aggiungi con icona
        add_button = QPushButton()
        add_button.setIcon(QIcon('assets/add_time.png'))
        add_button.setIconSize(QSize(24, 24))
        add_button.setToolTip("Aggiungi orario")
        add_button.clicked.connect(self.show_time_entry_dialog)
        add_button.setFixedSize(36, 36)
        toolbar.addWidget(add_button)
       
        # Pulsante Salva con icona
        save_button = QPushButton()
        save_button.setIcon(QIcon('assets/diskette.png'))
        save_button.setIconSize(QSize(24, 24))
        save_button.setToolTip("Salva (Ctrl+S)")
        save_button.clicked.connect(lambda: self.save_reservations(show_message=True))
        save_button.setFixedSize(36, 36)
        toolbar.addWidget(save_button)
        
        # Pulsante Elimina con icona
        delete_button = QPushButton()
        delete_button.setIcon(QIcon('assets/trash.png'))
        delete_button.setIconSize(QSize(24, 24))
        delete_button.setToolTip("Elimina prenotazione")
        delete_button.clicked.connect(self.delete_reservation)
        delete_button.setFixedSize(36, 36)
        toolbar.addWidget(delete_button)

        #Pulsante vai alla donazione successiva
        go_to_next_donation_button = QPushButton()
        go_to_next_donation_button.setIcon(QIcon('assets/blood.png'))
        go_to_next_donation_button.setIconSize(QSize(24, 24))
        go_to_next_donation_button.setToolTip("Vai alla donazione successiva")
        go_to_next_donation_button.clicked.connect(self.go_to_next_donation)
        go_to_next_donation_button.setFixedSize(36, 36)
        toolbar.addWidget(go_to_next_donation_button)
        
        toolbar.addStretch()  # Spazio flessibile
        layout.addLayout(toolbar)

        # Calendario
        calendar_group = QGroupBox("Calendario")
        calendar_layout = QVBoxLayout()
        
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.selectionChanged.connect(self.on_date_changed)
        calendar_layout.addWidget(self.calendar)
        
        calendar_group.setLayout(calendar_layout)
        layout.addWidget(calendar_group)

        # Widget Prenotazioni
        self.reservations_widget = ReservationsWidget(self)
        layout.addWidget(self.reservations_widget)

    def apply_theme(self):
        """Applica il tema all'applicazione"""
        # Gestisci la migrazione dal vecchio al nuovo sistema di temi
        theme_id = self.settings.value("theme", "light")
        if theme_id == "Scuro":
            theme_id = "dark"
            self.settings.setValue("theme", "dark")
        elif theme_id == "Chiaro":
            theme_id = "light"
            self.settings.setValue("theme", "light")
        
        # Assicurati che il tema esista, altrimenti usa quello chiaro
        if theme_id not in THEMES:
            theme_id = "light"
            self.settings.setValue("theme", "light")
        
        theme = THEMES[theme_id]
        
        # Applica il foglio di stile
        self.setStyleSheet(theme.get_stylesheet())
        
        # Aggiorna anche il widget delle prenotazioni
        if hasattr(self, 'reservations_widget'):
            self.reservations_widget.setStyleSheet(theme.get_stylesheet())

    def load_default_times(self):
        # Genera tutti gli orari possibili dalle 7:50 alle 12:10 con intervalli di 5 minuti
        start_time = QTime(7, 50)
        end_time = QTime(12, 10)
        current_time = start_time
        default_times = []
        
        while current_time <= end_time:
            default_times.append(current_time.toString("HH:mm"))
            current_time = current_time.addSecs(5 * 60)  # Aggiungi 5 minuti
        
        # Ottieni gli orari esistenti dal database
        selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        reservations = get_reservations(selected_date)
        existing_times = [res[0] for res in reservations]
        
        # Unisci tutti gli orari
        all_times = list(set(default_times + existing_times))
        
        # Converti in oggetti QTime per un ordinamento corretto
        time_objects = [(QTime.fromString(t, "HH:mm"), t) for t in all_times]
        time_objects.sort(key=lambda x: x[0])  # Ordina per orario
        
        # Filtra gli orari per mantenere solo quelli nel range desiderato
        filtered_times = [t[1] for t in time_objects 
                         if start_time <= t[0] <= end_time]
        
        # Popola la tabella
        self.table.setRowCount(len(filtered_times))
        for row, time in enumerate(filtered_times):
            self.table.setItem(row, 0, QTableWidgetItem(time))
            
            # ComboBox per Prima Donazione
            first_combo = QComboBox()
            first_combo.addItems(["No", "Sì"])
            
            # Se l'orario è dalle 10:00 in poi, imposta "No" e disabilita il ComboBox
            time_obj = QTime.fromString(time, "HH:mm")
            if time_obj >= QTime(10, 0):
                first_combo.setCurrentText("No")
                first_combo.setEnabled(False)
                # Opzionale: cambia lo stile per mostrare visivamente che è disabilitato
                first_combo.setStyleSheet("""
                    QComboBox {
                        background-color: #f0f0f0;
                        color: #666666;
                    }
                """)
            
            self.table.setCellWidget(row, 3, first_combo)
            
            # ComboBox per Stato
            status_combo = QComboBox()
            status_combo.addItems([
                "Non effettuata",
                "Sì",
                "No",
                "Non presentato",
                "Donazione interrotta"
            ])
            status_combo.setStyleSheet(f"""
                QComboBox {{
                    padding: 2px 5px;
                    border: 1px solid #004d4d;
                    border-radius: 3px;
                    min-width: 95px;
                    max-width: 95px;
                    background: white;
                    selection-background-color: #004d4d;
                    selection-color: white;
                }}
                QComboBox::drop-down {{
                    border: none;
                    width: 20px;
                }}
                QComboBox::down-arrow {{
                    image: url(down_arrow.png);
                    width: 10px;
                    height: 10px;
                }}
                QComboBox:hover {{
                    border-color: #006666;
                }}
                QComboBox QAbstractItemView {{
                    border: 1px solid #004d4d;
                    selection-background-color: #004d4d;
                    selection-color: white;
                    background: white;
                }}
                QComboBox QAbstractItemView::item {{
                    min-height: 20px;
                }}
                QComboBox QAbstractItemView::item:hover {{
                    background-color: #e6f3f3;
                }}
            """)
            self.table.setCellWidget(row, 4, status_combo)
            
            # Aggiungi il pulsante di reset
            reset_btn = QPushButton()
            reset_btn.setFixedSize(30, 30)
            
            # Carica l'icona del cestino
            # Prova diversi percorsi possibili per trovare l'icona
            possible_paths = [
                os.path.join(os.path.dirname(get_db_path()), "assets", "trash.png"),
                os.path.join(os.path.dirname(__file__), "assets", "trash.png"),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "trash.png"),
                "assets/trash.png"
            ]
            
            icon_found = False
            for icon_path in possible_paths:
                if os.path.exists(icon_path):
                    icon = QIcon(icon_path)
                    if not icon.isNull():
                        reset_btn.setIcon(icon)
                        reset_btn.setIconSize(QSize(16, 16))  # Dimensione icona più piccola
                        icon_found = True
                        break
            
            if not icon_found:
                reset_btn.setText("X")
                print(f"Icona non trovata. Percorsi tentati: {possible_paths}")
            
            reset_btn.setStyleSheet("""
                QPushButton {
                    border: none;
                    background-color: transparent;
                    margin: 0px;
                    padding: 0px;
                }
                QPushButton:hover {
                    background-color: #004d4d;
                    border-radius: 15px;  /* Metà della larghezza per renderlo circolare */
                }
            """)
            
            # Collega il pulsante alla funzione di reset
            reset_btn.clicked.connect(lambda checked, t=time: self.reset_reservation(t))
            
            # Crea un widget contenitore per centrare il pulsante
            container = QWidget()
            container_layout = QHBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.setAlignment(Qt.AlignCenter)
            container_layout.addWidget(reset_btn)
            
            self.table.setCellWidget(row, 5, container)

    def export_to_docx(self):
        """Esporta i dati in formato Word"""
        try:
            date = self.calendar.selectedDate().toString("yyyy-MM-dd")
            table = self.reservations_widget.get_table()
            
            # Raccogli i dati dalla tabella
            data = []
            for row in range(table.rowCount()):
                time = table.item(row, 0).text()
                name = table.item(row, 1).text() if table.item(row, 1) else ""
                surname = table.item(row, 2).text() if table.item(row, 2) else ""
                first_donation = table.cellWidget(row, 3).currentText()
                stato = table.cellWidget(row, 4).currentText()
                
                if name.strip() or surname.strip():
                    data.append([time, name, surname, first_donation, stato])
            
            # Esporta
            file_path = export_to_docx(date, data)
            if file_path:
                QMessageBox.information(
                    self,
                    "Esportazione Completata",
                    f"File salvato in:\n{file_path}"
                )
                
        except Exception as e:
            logger.error(f"Errore nell'esportazione: {str(e)}")
            QMessageBox.critical(
                self,
                "Errore",
                f"Errore nell'esportazione: {str(e)}"
            )

    def print_table(self):
        """Stampa la tabella delle prenotazioni"""
        try:
            printer = QPrinter(QPrinter.HighResolution)
            dialog = QPrintDialog(printer, self)
            
            if dialog.exec_() == QPrintDialog.Accepted:
                date = self.calendar.selectedDate().toString("yyyy-MM-dd")
                table = self.reservations_widget.get_table()
                
                # Raccogli i dati dalla tabella
                data = []
                for row in range(table.rowCount()):
                    time = table.item(row, 0).text()
                    name = table.item(row, 1).text() if table.item(row, 1) else ""
                    surname = table.item(row, 2).text() if table.item(row, 2) else ""
                    first_donation = table.cellWidget(row, 3).currentText()
                    stato = table.cellWidget(row, 4).currentText()
                    
                    if name.strip() or surname.strip():
                        data.append([time, name, surname, first_donation, stato])
                
                print_data(printer, date, data)
                
        except Exception as e:
            logger.error(f"Errore nella stampa: {str(e)}")
            QMessageBox.critical(
                self,
                "Errore",
                f"Errore nella stampa: {str(e)}"
            )

    def load_reservations(self):
        """Carica le prenotazioni per la data selezionata"""
        try:
            selected_date = self.calendar.selectedDate()
            self.reservations_widget.load_reservations(selected_date)
        except Exception as e:
            logger.error(f"Errore nel caricamento delle prenotazioni: {str(e)}")
            QMessageBox.critical(
                self,
                "Errore",
                f"Errore nel caricamento delle prenotazioni: {str(e)}"
            )

    def save_reservations(self, show_message=True):
        """Salva lo stato corrente delle prenotazioni"""
        try:
            table = self.reservations_widget.get_table()
            date = self.calendar.selectedDate().toString("yyyy-MM-dd")
            
            for row in range(table.rowCount()):
                time = table.item(row, 0).text()
                name = table.item(row, 1).text() if table.item(row, 1) else ""
                surname = table.item(row, 2).text() if table.item(row, 2) else ""
                first_donation = table.cellWidget(row, 3).currentText() == "Sì"
                stato = table.cellWidget(row, 4).currentText()
                
                if name.strip() or surname.strip():
                    add_reservation(date, time, name, surname, first_donation)
                    save_donation_status(date, time, stato)
            
            # Aggiorna l'ora dell'ultimo salvataggio
            current_time = datetime.now().strftime("%H:%M:%S")
            self.settings.setValue("last_save_time", current_time)
            self.update_last_save_info()
            
            if show_message:
                self.statusBar.showMessage("Salvataggio completato", 3000)
                
            return True
            
        except Exception as e:
            logger.error(f"Errore nel salvataggio: {str(e)}")
            if show_message:
                QMessageBox.critical(self, "Errore", f"Errore nel salvataggio: {str(e)}")
            return False

    def show_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            init_db()
            self.apply_theme()
            self.highlight_donation_dates()
            self.setup_autosave()

    def highlight_donation_dates(self):
        """Evidenzia le date di donazione nel calendario"""
        try:
            # Reset formato precedente
            self.calendar.setDateTextFormat(QDate(), QTextCharFormat())
            
            # Ottieni l'anno corrente dal calendario
            current_year = self.calendar.yearShown()
            
            # Formato per le date di donazione
            donation_format = QTextCharFormat()
            donation_format.setBackground(QColor("#c2fc03"))  # Verde lime
            donation_format.setForeground(QColor("#000000"))  # Testo nero
            
            # Ottieni le date di donazione
            dates = get_donation_dates(current_year)
            
            # Applica il formato alle date
            for date_str in dates:
                date = QDate.fromString(date_str, "yyyy-MM-dd")
                if date.isValid():
                    self.calendar.setDateTextFormat(date, donation_format)
                
        except Exception as e:
            logger.error(f"Errore nell'evidenziazione delle date: {str(e)}")

    def show_history(self):
        dialog = HistoryDialog(self)
        dialog.exec_()

    def show_info(self):
        dialog = InfoDialog(self)
        dialog.exec_()

    def open_database(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Apri Database",
            os.path.expanduser("~/Documents/Hemodos"),
            "Database SQLite (*.db)"
        )
        if file_path:
            filename = os.path.basename(file_path)
            
            try:
                # Gestione database prenotazioni giornaliere
                if filename.startswith("prenotazioni_"):
                    # Estrai giorno e mese dal nome del file
                    day = int(filename.split("_")[1])
                    month = int(filename.split("_")[2].split(".")[0])
                    year = QDate.currentDate().year()
                    
                    # Imposta la data nel calendario
                    date = QDate(year, month, day)
                    self.calendar.setSelectedDate(date)
                    # Carica le prenotazioni per quella data
                    self.load_reservations()
                    
                # Gestione database date donazione
                elif filename.startswith("date_donazione_"):
                    # Estrai l'anno dal nome del file
                    year = int(filename.split("_")[2].split(".")[0])
                    # Apri la finestra impostazioni sulla tab delle date
                    settings_dialog = SettingsDialog(self)
                    settings_dialog.tab_widget.setCurrentIndex(0)  # Tab Generali
                    settings_dialog.exec_()
                    
                # Gestione database cronologia
                elif filename.startswith("cronologia_"):
                    # Estrai l'anno dal nome del file
                    year = int(filename.split("_")[1].split(".")[0])
                    # Apri la finestra cronologia
                    history_dialog = HistoryDialog(self)
                    # Imposta l'anno nel combo box della cronologia
                    index = history_dialog.year_combo.findText(str(year))
                    if index >= 0:
                        history_dialog.year_combo.setCurrentIndex(index)
                    history_dialog.exec_()
                    
                # Gestione database statistiche
                elif filename.startswith("statistiche_"):
                    # Apri la finestra statistiche
                    statistics_dialog = StatisticsDialog(self)
                    statistics_dialog.exec_()
                
                # Aggiorna le informazioni del database
                self.settings.setValue("last_database", file_path)
                self.update_db_info()
                
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Errore",
                    f"Errore nell'apertura del database:\n{str(e)}"
                )

    def setup_autosave(self):
        """Configura il timer per il salvataggio automatico"""
        enabled = self.settings.value("autosave_enabled", False, type=bool)
        interval = self.settings.value("autosave_interval", 5, type=int)
        
        if enabled:
            # Converti minuti in millisecondi (1 minuto = 60000 ms)
            interval_ms = interval * 60 * 1000
            self.autosave_timer.setInterval(interval_ms)
            self.autosave_timer.start()
            print(f"Autosave attivato: salvataggio ogni {interval} minuti")
        else:
            self.autosave_timer.stop()
            print("Autosave disattivato")

    def auto_save(self):
        """Esegue il salvataggio automatico"""
        try:
            self.save_reservations(show_message=False)
            self.statusBar.showMessage("Autosave completato", 2000)
            logger.info(f"Autosave eseguito: {datetime.now().strftime('%H:%M:%S')}")
        except Exception as e:
            logger.error(f"Errore durante l'autosave: {str(e)}")

    def reload_database(self):
        """Ricarica i dati quando il database viene modificato esternamente"""
        try:
            # Ricarica i dati della data corrente
            self.load_reservations()
            # Aggiorna le date di donazione evidenziate
            self.highlight_donation_dates()
            # Aggiorna le informazioni del database
            self.update_db_info()
            
            # Mostra notifica di aggiornamento nella barra di stato
            self.statusBar.showMessage("Database aggiornato da modifiche esterne", 3000)
        except Exception as e:
            print(f"Errore durante il ricaricamento del database: {str(e)}")

    def closeEvent(self, event):
        """Gestisce la chiusura dell'applicazione"""
        try:
            # Salva le modifiche correnti
            self.save_reservations(show_message=False)
            
            # Ferma il monitoraggio cloud
            if hasattr(self, 'observer') and self.observer:
                self.observer.stop()
                self.observer.wait()
            
            # Ferma il timer di autosave
            if hasattr(self, 'autosave_timer'):
                self.autosave_timer.stop()
            
            # Salva le impostazioni
            self.settings.sync()
            
            event.accept()
        except Exception as e:
            print(f"Errore durante la chiusura: {str(e)}")
            event.accept()  # Chiudi comunque l'app

    def close_database(self):
        """Chiude il database corrente e mostra la schermata iniziale"""
        # Salva eventuali modifiche
        self.save_reservations(show_message=False)
        
        # Rimuovi il riferimento al database corrente
        self.settings.remove("last_database")
        
        # Mostra la finestra di selezione database
        dialog = FirstRunDialog()
        if dialog.exec_() == QDialog.Accepted:
            option = dialog.selected_option
            if option == 1:  # Nuovo database locale
                self.settings.setValue("cloud_service", "Locale")
                init_db()
            elif option == 2:  # Database locale esistente
                file_path, _ = QFileDialog.getOpenFileName(
                    self,
                    "Apri Database",
                    os.path.expanduser("~/Documents/Hemodos"),
                    "Database SQLite (*.db)"
                )
                if file_path:
                    self.settings.setValue("last_database", file_path)
                    self.settings.setValue("cloud_service", "Locale")
            elif option == 3:  # OneDrive
                self.settings.setValue("cloud_service", "OneDrive")
            elif option == 4:  # Google Drive
                self.settings.setValue("cloud_service", "Google Drive")
            
            # Ricarica l'interfaccia
            self.load_default_times()
            self.highlight_donation_dates()
            self.update_db_info()
        else:
            # Se l'utente annulla, riapri il database precedente
            self.load_reservations()

    def close_app(self):
        """Salva tutto e chiude l'applicazione"""
        try:
            # Salva le modifiche correnti
            self.save_reservations(show_message=False, is_closing=True)
            
            # Ferma il monitoraggio cloud
            if hasattr(self, 'observer') and self.observer:
                self.observer.stop()
                self.observer.wait()
                add_history_entry("Sistema", "Sincronizzazione cloud terminata")
            
            # Ferma il timer di autosave
            if hasattr(self, 'autosave_timer'):
                self.autosave_timer.stop()
            
            # Salva le impostazioni
            self.settings.sync()
            
            # Chiudi l'applicazione
            self.close()
        except Exception as e:
            reply = QMessageBox.question(
                self,
                "Errore durante il salvataggio",
                f"Si è verificato un errore durante il salvataggio: {str(e)}\n\n"
                "Vuoi chiudere comunque l'applicazione?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.close()

    def show_delete_dialog(self):
        dialog = DeleteFilesDialog(self)
        dialog.exec_()

    def update_donation_dates_format(self):
        """Aggiorna solo il formato delle date di donazione nel calendario"""
        try:
            # Prima rimuovi tutti i formati esistenti
            self.calendar.setDateTextFormat(QDate(), QTextCharFormat())
            
            # Formato per le date di donazione
            donation_format = QTextCharFormat()
            donation_format.setBackground(QColor("#c2fc03"))  # Verde lime
            donation_format.setForeground(QColor("#000000"))  # Testo nero
            
            # Ottieni l'anno corrente
            current_date = self.calendar.selectedDate()
            year = current_date.year()
            
            # Evidenzia le date di donazione
            dates = get_donation_dates(year)
            for date_str in dates:
                date = QDate.fromString(date_str, "yyyy-MM-dd")
                if date.isValid():
                    self.calendar.setDateTextFormat(date, donation_format)
            
            # Forza l'aggiornamento visivo
            self.calendar.updateCells()
            
        except Exception as e:
            print(f"Errore nell'aggiornamento del formato delle date: {str(e)}")

    def show_time_entry_dialog(self):
        """Mostra il dialog per l'inserimento degli orari"""
        dialog = TimeEntryDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            time = dialog.get_time()
            date = self.calendar.selectedDate().toString("yyyy-MM-dd")
            if add_donation_time(date, time):
                self.load_reservations()
                self.highlight_donation_dates()

    def show_statistics(self):
        dialog = StatisticsDialog(self)
        dialog.exec_()

    def show_calendar_context_menu(self, position):
        # Ottieni la data sotto il cursore
        date = self.calendar.selectedDate()
        if not date.isValid():
            return
        
        # Crea il menu contestuale
        context_menu = QMenu(self)
        
        # Aggiungi le azioni del menu File
        add_time_action = QAction('Aggiungi Orario', self)
        add_time_action.triggered.connect(self.show_time_entry_dialog)
        context_menu.addAction(add_time_action)
        
        save_action = QAction('Salva', self)
        save_action.triggered.connect(self.save_reservations)
        context_menu.addAction(save_action)
        
        context_menu.addSeparator()
        
        export_action = QAction('Esporta in DOCX', self)
        export_action.triggered.connect(self.export_to_docx)
        context_menu.addAction(export_action)
        
        print_action = QAction('Stampa', self)
        print_action.triggered.connect(self.print_table)
        context_menu.addAction(print_action)
        
        # Mostra il menu alla posizione del mouse
        context_menu.exec_(self.calendar.mapToGlobal(position))

    def reset_reservation(self, time):
        """Gestisce il reset di una prenotazione"""
        reply = QMessageBox.question(
            self,
            "Conferma l'eliminazione",
            f"Sei sicuro di voler cancellare la prenotazione delle {time}?\n"
            "Questa operazione non può essere annullata.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
            
            # Trova la riga corrispondente
            for row in range(self.table.rowCount()):
                if self.table.item(row, 0) and self.table.item(row, 0).text() == time:
                    # Resetta i campi della tabella
                    self.table.setItem(row, 1, QTableWidgetItem(""))  # Nome
                    self.table.setItem(row, 2, QTableWidgetItem(""))  # Cognome
                    
                    # Resetta i combobox
                    first_combo = self.table.cellWidget(row, 3)
                    if first_combo:
                        first_combo.setCurrentText("No")
                    
                    status_combo = self.table.cellWidget(row, 4)
                    if status_combo:
                        status_combo.setCurrentText("Non effettuata")
                    break
            
            # Salva le modifiche nel database
            if reset_reservation(selected_date, time):
                self.save_reservations(show_message=False)  # Salva silenziosamente
                self.statusBar.showMessage("Prenotazione eliminata con successo", 3000)
                # Aggiorna info database
                self.update_db_info()
            else:
                QMessageBox.warning(self, "Errore", "Impossibile eliminare la prenotazione")

    def show_manual(self):
        """Mostra il manuale utente"""
        from gui.dialogs.manual_dialog import ManualDialog
        dialog = ManualDialog(self)
        dialog.exec_()

    def on_date_changed(self):
        """Gestisce il cambio di data nel calendario"""
        try:
            selected_date = self.calendar.selectedDate()
            
            # Gestione cambio anno se necessario
            if self.handle_year_change(selected_date):
                # Inizializza il database per la data selezionata se non esiste
                db_path = get_db_path(selected_date)
                if not os.path.exists(db_path):
                    init_db(specific_date=selected_date)
                
                # Carica le prenotazioni per la data selezionata
                self.reservations_widget.load_reservations(selected_date)
                
                # Aggiorna l'evidenziazione delle date
                self.highlight_donation_dates()
                
                # Aggiorna le info del database
                self.update_db_info()
                
                # Mostra messaggio nella barra di stato
                self.statusBar.showMessage(
                    f"Database caricato: {selected_date.toString('dd/MM/yyyy')}", 
                    3000
                )
                
        except Exception as e:
            logger.error(f"Errore nel cambio data: {str(e)}")
            QMessageBox.critical(
                self,
                "Errore",
                f"Errore nel cambio data: {str(e)}"
            )

    def handle_year_change(self, selected_date):
        """Gestisce il cambio di anno, restituisce True se l'operazione è riuscita"""
        if selected_date.year() != self.last_valid_date.year():
            year_path = os.path.join(self.get_base_path(), str(selected_date.year()))
            
            if not os.path.exists(year_path):
                reply = QMessageBox.question(
                    self,
                    "Nuovo Anno",
                    f"Stai passando all'anno {selected_date.year()}.\nVuoi creare la struttura necessaria?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )
                
                if reply == QMessageBox.Yes:
                    try:
                        self.year_manager.create_year_structure(selected_date.year())
                        self.year_manager.year_changed.emit(selected_date.year())
                        self.last_valid_date = selected_date
                        return True
                    except Exception as e:
                        QMessageBox.critical(self, "Errore", str(e))
                        self.calendar.setSelectedDate(self.last_valid_date)
                        return False
                else:
                    self.calendar.setSelectedDate(self.last_valid_date)
                    return False
        
        self.last_valid_date = selected_date
        return True

    def get_base_path(self):
        """Ottiene il percorso base in base alle impostazioni"""
        service = self.settings.value("cloud_service", "Locale")
        if service == "Locale":
            return os.path.expanduser("~/Documents/Hemodos")
        else:
            cloud_path = self.settings.value("cloud_path", "")
            return os.path.join(cloud_path, "Hemodos")

    def on_year_created(self, year):
        """Gestisce la creazione di un nuovo anno"""
        QMessageBox.information(
            self,
            "Successo",
            f"Struttura per l'anno {year} creata con successo!"
        )
        self.update_db_info()

    def on_year_changed(self, year):
        """Gestisce il cambio di anno"""
        try:
            # Ottieni il percorso base corretto
            settings = QSettings('Hemodos', 'DatabaseSettings')
            service = settings.value("cloud_service", "Locale")
            
            if service == "Locale":
                base_path = os.path.expanduser("~/Documents/Hemodos")
            else:
                cloud_path = settings.value("cloud_path", "")
                base_path = os.path.join(cloud_path, "Hemodos")
            
            # Aggiorna il database corrente usando il percorso corretto
            year_path = os.path.join(base_path, str(year))
            db_path = os.path.join(year_path, f"hemodos_{year}.db")
            self.settings.setValue("last_database", db_path)
            
            # Aggiorna la vista
            self.load_reservations()
            self.highlight_donation_dates()
            self.update_db_info()
            
            # Mostra messaggio nella barra di stato
            self.statusBar.showMessage(f"Anno cambiato: {year}", 3000)
            logger.info(f"Cambio anno effettuato: {year}")
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Errore",
                f"Errore nel cambio di anno: {str(e)}"
            )
            logger.error(f"Errore nel cambio di anno: {str(e)}")

    def add_reservation_to_table(self, time, name, surname, first_donation, stato):
        """Aggiunge una prenotazione alla tabella"""
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # Aggiungi orario
        self.table.setItem(row, 0, QTableWidgetItem(time))
        
        # Aggiungi nome e cognome
        self.table.setItem(row, 1, QTableWidgetItem(name))
        self.table.setItem(row, 2, QTableWidgetItem(surname))
        
        # Combo box per prima donazione
        first_combo = QComboBox()
        first_combo.addItems(["No", "Sì"])
        
        # Gestione orari dopo le 10:00
        time_obj = QTime.fromString(time, "HH:mm")
        if time_obj >= QTime(10, 0):
            first_combo.setCurrentText("No")
            first_combo.setEnabled(False)
            first_combo.setStyleSheet("""
                QComboBox {
                    background-color: #f0f0f0;
                    color: #666666;
                }
            """)
        else:
            first_combo.setCurrentText("Sì" if first_donation else "No")
        
        self.table.setCellWidget(row, 3, first_combo)
        
        # Combo box per lo stato
        stato_combo = QComboBox()
        stato_combo.addItems([
            "Non effettuata",
            "Sì",
            "No",
            "Non presentato",
            "Donazione interrotta"
        ])
        stato_combo.setCurrentText(stato)
        self.table.setCellWidget(row, 4, stato_combo)

    def update_last_save_info(self):
        """Aggiorna le informazioni sull'ultimo salvataggio"""
        last_save = self.settings.value("last_save_time", "Mai")
        self.last_save_label.setText(f"Ultimo salvataggio: {last_save}")

    def delete_reservation(self):
        """Elimina la prenotazione selezionata"""
        try:
            table = self.reservations_widget.get_table()
            current_row = table.currentRow()
            
            if current_row >= 0:
                time = table.item(current_row, 0).text()
                name = table.item(current_row, 1).text() if table.item(current_row, 1) else ""
                surname = table.item(current_row, 2).text() if table.item(current_row, 2) else ""
                
                if name.strip() or surname.strip():
                    reply = QMessageBox.question(
                        self,
                        'Conferma eliminazione',
                        f'Vuoi davvero eliminare la prenotazione delle {time}?',
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No
                    )
                    
                    if reply == QMessageBox.Yes:
                        date = self.calendar.selectedDate().toString("yyyy-MM-dd")
                        if delete_reservation(date, time):
                            # Pulisci le celle ma mantieni l'orario
                            table.setItem(current_row, 1, QTableWidgetItem(""))
                            table.setItem(current_row, 2, QTableWidgetItem(""))
                            
                            # Reimposta i combobox
                            first_combo = table.cellWidget(current_row, 3)
                            first_combo.setCurrentText("No")
                            
                            stato_combo = table.cellWidget(current_row, 4)
                            stato_combo.setCurrentText("Non effettuata")
                            
                            self.statusBar.showMessage("Prenotazione eliminata", 3000)
                            
                else:
                    QMessageBox.warning(
                        self,
                        "Attenzione",
                        "Seleziona una prenotazione da eliminare"
                    )
                    
            else:
                QMessageBox.warning(
                    self,
                    "Attenzione",
                    "Seleziona una prenotazione da eliminare"
                )
                
        except Exception as e:
            logger.error(f"Errore nell'eliminazione della prenotazione: {str(e)}")
            QMessageBox.critical(
                self,
                "Errore",
                f"Errore nell'eliminazione della prenotazione: {str(e)}"
            )

    def load_current_day_database(self):
        """Carica il database del giorno corrente"""
        try:
            current_date = QDate.currentDate()
            # Inizializza il database se non esiste
            db_path = get_db_path(current_date)
            if not os.path.exists(db_path):
                init_db(specific_date=current_date)
            
            # Imposta la data corrente nel calendario
            self.calendar.setSelectedDate(current_date)
            
            # Carica le prenotazioni
            self.reservations_widget.load_reservations(current_date)
            
            # Aggiorna le info del database
            self.update_db_info()
            
        except Exception as e:
            logger.error(f"Errore nel caricamento del database giornaliero: {str(e)}")
            QMessageBox.critical(
                self,
                "Errore",
                f"Errore nel caricamento del database giornaliero: {str(e)}"
            )

    def go_to_next_donation(self):
        """Va alla prossima data di donazione"""
        try:
            current_date = self.calendar.selectedDate()
            current_year = current_date.year()
            
            # Ottieni tutte le date di donazione dell'anno
            donation_dates = get_donation_dates(current_year)
            
            if not donation_dates:
                logger.info("Nessuna data di donazione trovata")
                return
            
            # Converti le date in oggetti QDate
            dates = []
            for date_str in donation_dates:
                date = QDate.fromString(date_str, "yyyy-MM-dd")
                if date.isValid():
                    dates.append(date)
            
            # Ordina le date
            dates.sort()
            
            # Trova la prossima data di donazione
            next_date = None
            for date in dates:
                if date > current_date:
                    next_date = date
                    break
            
            # Se non ci sono date successive, prendi la prima dell'anno successivo
            if not next_date:
                next_year_dates = get_donation_dates(current_year + 1)
                if next_year_dates:
                    next_date = QDate.fromString(min(next_year_dates), "yyyy-MM-dd")
            
            # Se abbiamo trovato una data valida, vai a quella data
            if next_date and next_date.isValid():
                self.calendar.setSelectedDate(next_date)
                self.statusBar.showMessage(
                    f"Prossima donazione: {next_date.toString('dd/MM/yyyy')}", 
                    3000
                )
            else:
                self.statusBar.showMessage(
                    "Nessuna data di donazione successiva trovata", 
                    3000
                )
            
        except Exception as e:
            logger.error(f"Errore nel passaggio alla donazione successiva: {str(e)}")

    def create_menus(self):
        """Crea i menu dell'applicazione"""
        menubar = self.menuBar()
        
        # Menu File
        file_menu = menubar.addMenu('File')
        file_menu.addAction(self.export_action)
        file_menu.addAction(self.print_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)
        
        # Menu Strumenti
        tools_menu = menubar.addMenu('Strumenti')
        
        # Azione Cronologia
        history_action = QAction(QIcon('assets/history.png'), 'Cronologia', self)
        history_action.setStatusTip('Visualizza la cronologia delle operazioni')
        history_action.triggered.connect(self.show_history)
        tools_menu.addAction(history_action)
        
        # Azione Statistiche
        stats_action = QAction(QIcon('assets/stats.png'), 'Statistiche', self)
        stats_action.setStatusTip('Visualizza le statistiche delle donazioni')
        stats_action.triggered.connect(self.show_statistics)
        tools_menu.addAction(stats_action)
        
        # Azione Gestione Database
        db_action = QAction(QIcon('assets/database.png'), 'Gestione Database', self)
        db_action.setStatusTip('Gestisci i database delle donazioni')
        db_action.triggered.connect(self.show_database_manager)
        tools_menu.addAction(db_action)
        
        tools_menu.addSeparator()
        
        # Azione Impostazioni
        settings_action = QAction(QIcon('assets/settings.png'), 'Impostazioni', self)
        settings_action.setStatusTip('Configura le impostazioni dell\'applicazione')
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)
        
        # Menu Aiuto
        help_menu = menubar.addMenu('Aiuto')
        help_menu.addAction(self.manual_action)
        help_menu.addAction(self.about_action)

    def show_database_manager(self):
        """Mostra il gestore database"""
        try:
            dialog = DeleteFilesDialog(self)
            dialog.exec_()
        except Exception as e:
            logger.error(f"Errore nell'apertura del gestore database: {str(e)}")
            QMessageBox.critical(
                self,
                "Errore",
                f"Errore nell'apertura del gestore database: {str(e)}"
            )
