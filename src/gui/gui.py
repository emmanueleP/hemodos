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

class MainWindow(QMainWindow):
    def __init__(self, config):
        super().__init__()
        self.settings = QSettings('Hemodos', 'DatabaseSettings')

        # Set window properties
        self.setWindowTitle("Hemodos - Prenotazioni Donazioni di Sangue")
        self.resize(1024, 768)
        self.setMinimumSize(800, 600)

        # Set theme and colors
        self.primary_color = "#004d4d"  # Colore petrolio
        self.apply_theme()

        # Inizializza il database prima di tutto
        init_db()

        # Create menu bar
        self.create_menu_bar()

        # Create status bar
        self.create_status_bar()

        # Initialize UI
        self.init_ui()

        # Evidenzia le date dopo che tutto è stato inizializzato
        self.highlight_donation_dates()

        # Aggiorna le informazioni del database
        self.update_db_info()

        # Aggiungi scorciatoia da tastiera per il salvataggio
        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        save_shortcut.activated.connect(self.save_reservations)

        # Setup autosave timer
        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self.auto_save)
        self.setup_autosave()

        # Setup cloud monitoring
        self.observer = setup_cloud_monitoring(self)

    def create_menu_bar(self):
        menubar = self.menuBar()

        # Menu File
        file_menu = menubar.addMenu('File')
        
        # Add Time Entry action
        add_time_action = QAction('Aggiungi Orario', self)
        add_time_action.setShortcut('Ctrl+T')
        add_time_action.triggered.connect(self.show_time_entry_dialog)
        file_menu.addAction(add_time_action)
        
        # Azione di salvataggio
        save_action = QAction('Salva', self)
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

        export_action = QAction('Esporta in DOCX', self)
        export_action.triggered.connect(self.export_to_docx)
        file_menu.addAction(export_action)

        print_action = QAction('Stampa', self)
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
        
        history_action = QAction('Cronologia', self)
        history_action.triggered.connect(self.show_history)
        tools_menu.addAction(history_action)
        
        delete_action = QAction('Elimina Database...', self)
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

        statistics_action = QAction('Statistiche', self)
        statistics_action.triggered.connect(self.show_statistics)
        tools_menu.addAction(statistics_action)

    def create_status_bar(self):
        self.statusBar = self.statusBar()
        
        # Database info label (right-aligned)
        self.db_info_label = QLabel()
        self.db_info_label.setAlignment(Qt.AlignRight)
        self.statusBar.addPermanentWidget(self.db_info_label)

    def update_db_info(self):
        try:
            db_path = get_db_path()
            last_modified = datetime.now()  # Usa sempre l'ora corrente
            last_modified_str = last_modified.strftime("%d/%m/%Y %H:%M:%S")
            
            # Ottieni solo il nome della cartella contenente il database
            db_location = os.path.basename(os.path.dirname(db_path))
            
            # Aggiungi info sulla sincronizzazione cloud
            service = self.settings.value("cloud_service", "Locale")
            sync_info = f" - Sincronizzato con {service}" if service != "Locale" else ""
            
            info_text = f"Database: {db_location} | Ultima modifica: {last_modified_str}{sync_info}"
            self.db_info_label.setText(info_text)
        except Exception as e:
            print(f"Errore nell'aggiornamento delle informazioni del database: {str(e)}")
            self.db_info_label.setText("Informazioni database non disponibili")

    def create_new_database(self):
        reply = QMessageBox.question(self, 'Nuovo Database', 
                                   'Vuoi davvero creare un nuovo database? Questo cancellerà tutti i dati esistenti.',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            init_db()
            QMessageBox.information(self, "Database", "Nuovo database creato con successo.")
            self.load_default_times()

    def init_ui(self):
        central_widget = QWidget()
        layout = QVBoxLayout()

        # Calendar for selecting donation days
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.selectionChanged.connect(self.load_reservations)
        # Abilita il menu contestuale
        self.calendar.setContextMenuPolicy(Qt.CustomContextMenu)
        self.calendar.customContextMenuRequested.connect(self.show_calendar_context_menu)
        layout.addWidget(self.calendar)

        # Table for managing appointments
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Orario", "Nome", "Cognome", 
                                             "Prima Donazione", "Stato", ""])
        self.table.setColumnWidth(0, 80)
        self.table.setColumnWidth(1, 150)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(3, 120)
        self.table.setColumnWidth(4, 110)
        self.table.setColumnWidth(5, 40)
        layout.addWidget(self.table)

        # Save button
        save_button = QPushButton("Salva")
        save_button.clicked.connect(self.save_reservations)
        layout.addWidget(save_button)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Load initial data
        self.load_default_times()

    def apply_theme(self):
        theme = self.settings.value("theme", "Scuro")
        palette = QPalette()
        
        if theme == "Scuro":
            # Tema scuro
            palette.setColor(QPalette.Window, QColor("#2b2b2b"))
            palette.setColor(QPalette.WindowText, QColor("#ffffff"))
            palette.setColor(QPalette.Base, QColor("#3b3b3b"))
            palette.setColor(QPalette.AlternateBase, QColor("#353535"))
            palette.setColor(QPalette.Text, QColor("#ffffff"))
            palette.setColor(QPalette.Button, QColor(self.primary_color))
            palette.setColor(QPalette.ButtonText, QColor("#ffffff"))
            palette.setColor(QPalette.Highlight, QColor(self.primary_color))
            palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
        else:
            # Tema chiaro
            palette.setColor(QPalette.Window, QColor("#f0f0f0"))
            palette.setColor(QPalette.WindowText, QColor("#000000"))
            palette.setColor(QPalette.Base, QColor("#ffffff"))
            palette.setColor(QPalette.AlternateBase, QColor("#f7f7f7"))
            palette.setColor(QPalette.Text, QColor("#000000"))
            palette.setColor(QPalette.Button, QColor(self.primary_color))
            palette.setColor(QPalette.ButtonText, QColor("#ffffff"))
            palette.setColor(QPalette.Highlight, QColor(self.primary_color))
            palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))

        self.setPalette(palette)

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
        try:
            # Ottieni il percorso dove salvare il file
            selected_date = self.calendar.selectedDate()
            default_name = f"prenotazioni_{selected_date.toString('dd_MM_yyyy')}.docx"
            file_path, _ = QFileDialog.getSaveFileName(
                self, 
                "Esporta in DOCX",
                default_name,
                "Documenti Word (*.docx)"
            )
            
            if file_path:
                # Raccogli i dati dalla tabella
                table_data = []
                for row in range(self.table.rowCount()):
                    orario = self.table.item(row, 0).text() if self.table.item(row, 0) else ""
                    nome = self.table.item(row, 1).text() if self.table.item(row, 1) else ""
                    cognome = self.table.item(row, 2).text() if self.table.item(row, 2) else ""
                    first_combo = self.table.cellWidget(row, 3)
                    prima_donazione = first_combo.currentText() if first_combo else "No"
                    
                    if nome or cognome:  # Includi solo le righe con prenotazioni
                        table_data.append((orario, nome, cognome, prima_donazione))
                
                # Ottieni il percorso del logo se presente
                logo_path = self.settings.value("print_logo")
                
                # Esporta il documento
                export_to_docx(file_path, table_data, logo_path)
                
                # Mostra messaggio di successo
                self.statusBar.showMessage(f"File esportato con successo: {file_path}", 3000)
                
                # Aggiungi alla cronologia
                details = f"File: {file_path}"
                add_history_entry("Esportazione DOCX", details)
                
                # Aggiorna info database
                self.update_db_info()
                
        except Exception as e:
            QMessageBox.warning(self, "Errore", f"Errore durante l'esportazione: {str(e)}")
            print(f"Errore durante l'esportazione: {str(e)}")

    def print_table(self):
        """Apre il dialogo di stampa e stampa il database corrente"""
        from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
        from PyQt5.QtGui import QTextDocument
        
        # Crea il documento da stampare
        document = QTextDocument()
        html_content = self.get_printable_content()
        document.setHtml(html_content)
        
        # Crea e configura la stampante
        printer = QPrinter(QPrinter.HighResolution)
        printer.setPageSize(QPrinter.A4)
        
        # Mostra il dialogo di stampa
        dialog = QPrintDialog(printer, self)
        if dialog.exec_() == QDialog.Accepted:
            document.print_(printer)

    def get_printable_content(self):
        """Genera il contenuto HTML per la stampa"""
        selected_date = self.calendar.selectedDate()
        date_str = selected_date.toString("dddd d MMMM yyyy")  # es: "Lunedì 15 Gennaio 2024"
        current_datetime = datetime.now().strftime("%d/%m/%Y alle %H:%M:%S")
        
        # Stile CSS per il documento
        style = """
            <style>
                @font-face {
                    font-family: 'SF Pro Display';
                    src: local('SF Pro Display');
                }
                body { font-family: 'SF Pro Display', Arial, sans-serif; }
                table { 
                    width: 100%; 
                    border-collapse: collapse; 
                    margin-top: 20px;
                    margin-bottom: 40px;
                }
                th, td { 
                    border: 1px solid black; 
                    padding: 8px; 
                    text-align: left;
                }
                th { background-color: #f2f2f2; }
                .title { 
                    text-align: center;
                    color: #ff0000;
                    font-weight: bold;
                    font-size: 86px;
                    margin-bottom: 10px;
                }
                .date { 
                    text-align: center;
                    color: #ff0000;
                    font-weight: bold;
                    font-size: 90px;
                    margin-bottom: 30px;
                }
                .footer {
                    text-align: right;
                    font-size: 40px;
                    color: #666666;
                    margin-top: 600px;
                }
            </style>
        """
        
        # Aggiungi il logo se presente
        logo_html = ""
        logo_path = self.settings.value("print_logo")
        if logo_path and os.path.exists(logo_path):
            logo_html = f"""
                <div style='position: absolute; top: 20px; left: 20px;'>
                    <img src='{logo_path}' style='max-width: 150px; max-height: 150px;'>
                </div>
            """
        
        # Intestazione
        header = f"""
            <div class='title'>Prenotazioni</div>
            <div class='date'>{date_str}</div>
        """
        
        # Tabella (rimossa la colonna Stato)
        table = "<table><tr><th>Orario</th><th>Nome</th><th>Cognome</th><th>Prima Donazione</th></tr>"
        
        # Raccogli i dati dalla tabella
        rows = []
        for row in range(self.table.rowCount()):
            orario = self.table.item(row, 0).text() if self.table.item(row, 0) else ""
            nome = self.table.item(row, 1).text() if self.table.item(row, 1) else ""
            cognome = self.table.item(row, 2).text() if self.table.item(row, 2) else ""
            combo = self.table.cellWidget(row, 3)
            prima_donazione = combo.currentText() if combo else "No"
            
            if nome or cognome:  # Includi solo le righe con prenotazioni
                rows.append(f"<tr><td>{orario}</td><td>{nome}</td><td>{cognome}</td><td>{prima_donazione}</td></tr>")
        
        table += "\n".join(rows)
        table += "</table>"
        
        # Footer
        footer = f"""
            <div class='footer'>Creato da Hemodos il {current_datetime}</div>
        """
        
        # Assembla il documento completo
        return f"{style}\n{logo_html}\n{header}\n{table}\n{footer}"

    def load_reservations(self):
        try:
            self.table.clearContents()
            self.load_default_times()
            
            selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
            reservations = get_reservations(selected_date)
            
            for orario, nome, cognome, first_donation, stato in reservations:
                for row in range(self.table.rowCount()):
                    if self.table.item(row, 0) and self.table.item(row, 0).text() == orario:
                        self.table.setItem(row, 1, QTableWidgetItem(nome))
                        self.table.setItem(row, 2, QTableWidgetItem(cognome))
                        
                        first_combo = QComboBox()
                        first_combo.addItems(["No", "Sì"])
                        
                        # Gestione orari dopo le 10:00
                        time_obj = QTime.fromString(orario, "HH:mm")
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
                        break
                    
        except Exception as e:
            print(f"Errore nel caricamento delle prenotazioni: {str(e)}")

    def save_reservations(self, show_message=True, is_auto_save=False, is_closing=False):
        selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        try:
            # Salva tutte le righe della tabella
            for row in range(self.table.rowCount()):
                orario_item = self.table.item(row, 0)
                nome_item = self.table.item(row, 1)
                cognome_item = self.table.item(row, 2)
                first_donation_combo = self.table.cellWidget(row, 3)
                status_combo = self.table.cellWidget(row, 4)

                if orario_item:
                    orario = orario_item.text()
                    nome = nome_item.text() if nome_item else ""
                    cognome = cognome_item.text() if cognome_item else ""
                    first_donation = first_donation_combo.currentText() == "Sì" if first_donation_combo else False
                    donation_status = status_combo.currentText() if status_combo else "Non effettuata"

                    # Salva la prenotazione e lo stato
                    add_reservation(selected_date, orario, nome, cognome, first_donation)
                    save_donation_status(selected_date, orario, donation_status)

            # Aggiungi alla cronologia solo messaggi di sistema appropriati
            if is_closing:
                add_history_entry("Sistema", "Chiusura applicazione e salvataggio dati")
            elif is_auto_save:
                add_history_entry("Sistema", "Salvataggio automatico")
            elif show_message:
                add_history_entry("Sistema", f"Salvataggio manuale per la data {selected_date}")

            if show_message:
                self.statusBar.showMessage("Prenotazioni salvate con successo", 3000)
            
            # Aggiorna info database
            self.update_db_info()
            
            return True
            
        except Exception as e:
            if show_message:
                QMessageBox.warning(self, "Errore", f"Errore durante il salvataggio: {str(e)}")
            print(f"Errore durante il salvataggio: {str(e)}")
            return False

    def show_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            init_db()
            self.apply_theme()
            self.highlight_donation_dates()
            self.setup_autosave()

    def highlight_donation_dates(self):
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
            self.calendar.updateCell(current_date)
            self.calendar.updateCells()
            
        except Exception as e:
            print(f"Errore nell'evidenziazione delle date: {str(e)}")

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
            # Prima rimuovi il riferimento al database precedente
            self.settings.remove("last_database")
            # Poi imposta il nuovo database
            self.settings.setValue("last_database", file_path)
            self.init_db()
            self.load_default_times()
            self.update_db_info()

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
            print(f"Autosave eseguito: {datetime.now().strftime('%H:%M:%S')}")
        except Exception as e:
            print(f"Errore durante l'autosave: {str(e)}")

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
        selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        dialog = TimeEntryDialog(self, selected_date)
        if dialog.exec_() == QDialog.Accepted:
            # Ricarica la tabella per mostrare il nuovo orario
            self.load_reservations()
            # Aggiorna anche il calendario nel caso la data non fosse già evidenziata
            self.highlight_donation_dates()
            # Aggiorna le informazioni del database
            self.update_db_info()

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
