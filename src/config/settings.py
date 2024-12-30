from gui.dialogs.base_dialog import HemodosDialog
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QComboBox, QFileDialog, QLineEdit,
                            QTabWidget, QWidget, QGroupBox, QFormLayout,
                            QCalendarWidget, QListWidget, QListWidgetItem,
                            QCheckBox, QSpinBox, QMessageBox, QTextBrowser,
                            QProgressDialog)
from PyQt5.QtCore import QSettings, QDate, Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator, QTextCharFormat, QColor, QPixmap
from core.database import (add_donation_date, get_donation_dates, delete_donation_date, 
                     get_db_path)
import os
import shutil
from datetime import datetime
import sqlite3
from core.year_manager import YearManager
from core.logger import logger
from core.themes import THEMES
from core.delete_db_logic import get_base_path

class SettingsDialog(HemodosDialog):
    def __init__(self, parent=None):
        super().__init__(parent, "Impostazioni")
        self.settings = QSettings('Hemodos', 'DatabaseSettings')
        self.parent = parent
        self.year_manager = YearManager()
        self.year_manager.year_created.connect(self.on_year_created)
        
        # Aggiungi current_year
        self.current_year = QDate.currentDate().year()
        
        # Aggiungi button_style
        self.button_style = """
            QPushButton {
                background-color: #004d4d;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #006666;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """
        
        self.init_ui()

    def init_ui(self):
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Generali tab (Date di donazione)
        general_tab = self.init_general_tab()
        self.tab_widget.addTab(general_tab, "Generali")
        
        # Gestione Anni tab
        years_tab = self.init_years_tab()
        self.tab_widget.addTab(years_tab, "Gestione Anni")
        
        # Cloud Storage tab
        cloud_tab = self.init_cloud_tab()
        self.tab_widget.addTab(cloud_tab, "Cloud Storage")
        
        # Appearance tab
        appearance_tab = self.init_appearance_tab()
        self.tab_widget.addTab(appearance_tab, "Aspetto")
        
        # Saving Options tab
        saving_tab = self.init_saving_tab()
        self.tab_widget.addTab(saving_tab, "Salvataggio")
        
        # Print tab
        print_tab = self.init_print_tab()
        self.tab_widget.addTab(print_tab, "Logo")

        # Aggiornamento tab
        update_tab = self.init_update_tab()
        self.tab_widget.addTab(update_tab, "Aggiornamento")

        self.content_layout.addWidget(self.tab_widget)
        
        # Initialize path based on current service
        self.on_service_changed(self.cloud_service.currentText())

    def init_update_tab(self):
        update_tab = QWidget()
        layout = QVBoxLayout()
        
        # Gruppo Aggiornamenti Automatici
        auto_update_group = QGroupBox("Aggiornamenti Automatici")
        auto_update_layout = QVBoxLayout()
        
        self.check_updates_cb = QCheckBox("Controlla automaticamente gli aggiornamenti")
        self.check_updates_cb.setChecked(
            self.settings.value("check_updates", True, type=bool)
        )
        self.check_updates_cb.toggled.connect(lambda checked: 
            self.settings.setValue("check_updates", checked))
        auto_update_layout.addWidget(self.check_updates_cb)
        
        # Pulsante per controllo manuale
        check_now_btn = QPushButton("Controlla Aggiornamenti")
        check_now_btn.clicked.connect(self.check_updates_manually)
        auto_update_layout.addWidget(check_now_btn)
        
        # Label per la versione corrente
        version_label = QLabel(f"Versione corrente: {self.get_current_version()}")
        auto_update_layout.addWidget(version_label)
        
        auto_update_group.setLayout(auto_update_layout)
        layout.addWidget(auto_update_group)
        
        # Gruppo Cronologia Aggiornamenti
        history_group = QGroupBox("Cronologia Aggiornamenti")
        history_layout = QVBoxLayout()
        
        self.update_history = QTextBrowser()
        self.update_history.setMaximumHeight(200)
        history_layout.addWidget(self.update_history)
        
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)
        
        # Aggiorna la cronologia
        self.update_history_text()
        
        layout.addStretch()
        update_tab.setLayout(layout)
        return update_tab

    def get_current_version(self):
        return "1.0.0"  # Versione corrente dell'app

    def check_updates_manually(self):
        """Controlla manualmente gli aggiornamenti"""
        from core.updater import UpdateChecker
        
        self.update_checker = UpdateChecker(self.get_current_version())
        self.update_checker.update_available.connect(self.show_update_dialog)
        self.update_checker.error_occurred.connect(self.show_update_error)
        self.update_checker.start()

    def show_update_dialog(self, version, release_notes, download_url):
        """Mostra il dialogo di aggiornamento disponibile"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Aggiornamento Disponibile")
        msg.setText(f"È disponibile una nuova versione di Hemodos (v{version})")
        msg.setInformativeText("Note di rilascio:\n" + release_notes)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.Yes)
        
        if msg.exec_() == QMessageBox.Yes:
            self.start_update(download_url)

    def show_update_error(self, error_msg):
        """Mostra errori durante il controllo aggiornamenti"""
        QMessageBox.warning(self, "Errore", error_msg)

    def start_update(self, download_url):
        """Avvia il processo di aggiornamento"""
        from core.updater import Updater
        
        # Crea e mostra la finestra di progresso
        progress = QProgressDialog("Download aggiornamento in corso...", "Annulla", 0, 100, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setAutoClose(True)
        
        self.updater = Updater(download_url)
        self.updater.update_progress.connect(progress.setValue)
        self.updater.update_completed.connect(self.on_update_completed)
        self.updater.update_error.connect(self.show_update_error)
        self.updater.start()

    def on_update_completed(self):
        """Gestisce il completamento dell'aggiornamento"""
        QMessageBox.information(
            self,
            "Aggiornamento Completato",
            "L'aggiornamento è stato scaricato.\n"
            "L'applicazione verrà chiusa per completare l'installazione."
        )
        self.parent().close()

    def init_appearance_tab(self):
        appearance_tab = QWidget()
        layout = QVBoxLayout()
        
        # Tema
        theme_group = QGroupBox("Tema")
        theme_layout = QVBoxLayout()
        
        self.theme_combo = QComboBox()
        for theme_id, theme in THEMES.items():
            self.theme_combo.addItem(theme.name, theme_id)
        
        # Gestisci la migrazione dal vecchio al nuovo sistema di temi
        current_theme = self.settings.value("theme", "light")
        if current_theme == "Scuro":
            current_theme = "dark"
            self.settings.setValue("theme", "dark")
        elif current_theme == "Chiaro":
            current_theme = "light"
            self.settings.setValue("theme", "light")
        
        # Imposta il tema corrente
        index = self.theme_combo.findData(current_theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        else:
            # Se il tema non esiste, usa quello chiaro
            index = self.theme_combo.findData("light")
            self.theme_combo.setCurrentIndex(index)
            self.settings.setValue("theme", "light")
        
        self.theme_combo.currentIndexChanged.connect(self.on_theme_changed)
        theme_layout.addWidget(self.theme_combo)
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)
        
        appearance_tab.setLayout(layout)
        return appearance_tab

    def on_theme_changed(self, index):
        theme_id = self.theme_combo.currentData()
        self.settings.setValue("theme", theme_id)
        
        # Applica il tema alla finestra principale
        if self.parent:
            self.parent.apply_theme()

    def init_cloud_tab(self):
        cloud_tab = QWidget()
        layout = QVBoxLayout()
        
        # Cloud Service Selection
        service_group = QGroupBox("Servizio Cloud")
        service_layout = QFormLayout()
        
        self.cloud_service = QComboBox()
        self.cloud_service.addItems(["Locale", "OneDrive", "Google Drive"])
        self.cloud_service.setCurrentText(self.settings.value("cloud_service", "Locale"))
        self.cloud_service.currentTextChanged.connect(self.on_service_changed)
        service_layout.addRow("Seleziona servizio:", self.cloud_service)
        
        service_group.setLayout(service_layout)
        layout.addWidget(service_group)
        
        # Cloud Path Selection
        path_group = QGroupBox("Percorso Cartella")
        path_layout = QHBoxLayout()
        
        self.path_edit = QLineEdit()
        self.path_edit.setText(self.settings.value("cloud_path", ""))
        path_layout.addWidget(self.path_edit)
        
        browse_btn = QPushButton("Sfoglia")
        browse_btn.clicked.connect(self.browse_path)
        path_layout.addWidget(browse_btn)
        
        path_group.setLayout(path_layout)
        layout.addWidget(path_group)
        
        # Help text
        help_label = QLabel("Seleziona la cartella sincronizzata del tuo servizio cloud.")
        help_label.setWordWrap(True)
        layout.addWidget(help_label)
        
        cloud_tab.setLayout(layout)
        return cloud_tab

    def init_saving_tab(self):
        saving_tab = QWidget()
        layout = QVBoxLayout()
        
        # Auto-save group
        autosave_group = QGroupBox("Salvataggio Automatico")
        autosave_layout = QVBoxLayout()
        
        self.autosave_check = QCheckBox("Abilita salvataggio automatico")
        self.autosave_check.setChecked(self.settings.value("autosave_enabled", False, type=bool))
        autosave_layout.addWidget(self.autosave_check)
        
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("Intervallo di salvataggio:"))
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 60)
        self.interval_spin.setValue(self.settings.value("autosave_interval", 5, type=int))
        interval_layout.addWidget(self.interval_spin)
        interval_layout.addWidget(QLabel("minuti"))
        interval_layout.addStretch()
        autosave_layout.addLayout(interval_layout)
        
        autosave_group.setLayout(autosave_layout)
        layout.addWidget(autosave_group)
        
        saving_tab.setLayout(layout)
        return saving_tab

    def init_print_tab(self):
        print_tab = QWidget()
        layout = QVBoxLayout()
        
        # Logo group
        logo_group = QGroupBox("Logo")
        logo_layout = QVBoxLayout()
        
        # Preview dell'immagine
        self.logo_preview = QLabel()
        self.logo_preview.setFixedSize(150, 150)
        self.logo_preview.setAlignment(Qt.AlignCenter)
        self.logo_preview.setStyleSheet("border: 1px solid #ccc;")
        
        # Carica l'immagine esistente se presente
        current_logo = self.settings.value("print_logo")
        if current_logo and os.path.exists(current_logo):
            pixmap = QPixmap(current_logo)
            self.logo_preview.setPixmap(pixmap.scaled(150, 150, Qt.KeepAspectRatio))
        else:
            self.logo_preview.setText("Nessun logo")
        
        logo_layout.addWidget(self.logo_preview)
        
        # Pulsanti
        btn_layout = QHBoxLayout()
        select_btn = QPushButton("Seleziona Logo")
        select_btn.clicked.connect(self.select_logo)
        remove_btn = QPushButton("Rimuovi Logo")
        remove_btn.clicked.connect(self.remove_logo)
        
        btn_layout.addWidget(select_btn)
        btn_layout.addWidget(remove_btn)
        logo_layout.addLayout(btn_layout)
        
        logo_group.setLayout(logo_layout)
        layout.addWidget(logo_group)
        
        # Help text
        help_label = QLabel("Il logo apparirà in alto a sinistra nei documenti stampati e esportati.")
        help_label.setWordWrap(True)
        layout.addWidget(help_label)
        
        layout.addStretch()
        print_tab.setLayout(layout)
        return print_tab

    def on_service_changed(self, service):
        """Suggerisce il percorso predefinito per il servizio selezionato"""
        if service == "OneDrive":
            default_path = os.path.expanduser("~/OneDrive")
        elif service == "Google Drive":
            default_path = os.path.expanduser("~/Google Drive")
        else:
            default_path = os.path.expanduser("~/Documents")
            
        if not self.path_edit.text():  # Solo se il percorso è vuoto
            self.path_edit.setText(default_path)

    def browse_path(self):
        current_path = self.path_edit.text()
        path = QFileDialog.getExistingDirectory(self, "Seleziona Cartella Cloud", 
                                              current_path)
        if path:
            self.path_edit.setText(path)

    def accept(self):
        try:
            # Salva le impostazioni generali
            self.settings.setValue("theme", self.theme_combo.currentText())
            self.settings.setValue("cloud_service", self.cloud_service.currentText())
            self.settings.setValue("cloud_path", self.path_edit.text())
            self.settings.setValue("autosave_enabled", self.autosave_check.isChecked())
            self.settings.setValue("autosave_interval", self.interval_spin.value())
            
            # Salva le date di donazione nel database
            if self.parent:
                # Aggiorna il calendario principale
                self.parent.highlight_donation_dates()  # Aggiorna le date evidenziate
                self.parent.apply_theme()  # Applica il tema
                self.parent.setup_autosave()  # Aggiorna le impostazioni di autosave
                
                # Forza il refresh del calendario principale
                current_date = self.parent.calendar.selectedDate()
                self.parent.calendar.setSelectedDate(current_date)  # Trigger refresh
            
            super().accept()
        except Exception as e:
            QMessageBox.warning(self, "Errore", f"Errore durante il salvataggio: {str(e)}")

    def init_general_tab(self):
        """Inizializza la tab Generali"""
        general_tab = QWidget()
        layout = QVBoxLayout()
        
        # Gruppo Date di Donazione
        donation_group = QGroupBox("Date di Donazione")
        donation_layout = QHBoxLayout()
        
        # Colonna sinistra: calendario e controlli
        left_column = QVBoxLayout()
        
        # Anno
        year_layout = QHBoxLayout()
        year_label = QLabel("Anno:")
        self.year_combo = QComboBox()
        current_year = QDate.currentDate().year()
        for year in range(current_year - 2, current_year + 3):
            self.year_combo.addItem(str(year))
        self.year_combo.setCurrentText(str(current_year))
        self.year_combo.currentTextChanged.connect(self.on_year_changed)
        
        year_layout.addWidget(year_label)
        year_layout.addWidget(self.year_combo)
        year_layout.addStretch()
        
        left_column.addLayout(year_layout)
        
        # Calendario
        self.donation_calendar = QCalendarWidget()
        self.donation_calendar.setGridVisible(True)
        left_column.addWidget(self.donation_calendar)
        
        # Pulsanti
        buttons_layout = QHBoxLayout()
        add_btn = QPushButton("Aggiungi Data")
        add_btn.clicked.connect(self.add_donation_date)
        add_btn.setStyleSheet(self.button_style)
        
        remove_btn = QPushButton("Rimuovi Data")
        remove_btn.clicked.connect(self.remove_donation_date)
        remove_btn.setStyleSheet(self.button_style)
        
        buttons_layout.addWidget(add_btn)
        buttons_layout.addWidget(remove_btn)
        left_column.addLayout(buttons_layout)
        
        # Colonna destra: lista date
        right_column = QVBoxLayout()
        self.donation_dates_list = QListWidget()
        right_column.addWidget(self.donation_dates_list)
        
        # Aggiungi le colonne al layout principale
        donation_layout.addLayout(left_column, 2)  # Proporzione 2
        donation_layout.addLayout(right_column, 1)  # Proporzione 1
        
        donation_group.setLayout(donation_layout)
        layout.addWidget(donation_group)
        
        general_tab.setLayout(layout)
        
        # Carica le date iniziali
        self.load_donation_dates_for_year(current_year)
        
        return general_tab

    def on_year_changed(self, year_str):
        """Gestisce il cambio di anno nel combo box"""
        try:
            year = int(year_str)
            self.current_year = year
            self.load_donation_dates_for_year(year)
            
        except Exception as e:
            logger.error(f"Errore nel cambio anno: {str(e)}")

    def highlight_saved_dates(self):
        """Evidenzia le date salvate nel calendario"""
        try:
            # Reset formato precedente
            self.donation_calendar.setDateTextFormat(QDate(), QTextCharFormat())
            
            # Formato per le date di donazione
            highlight_format = QTextCharFormat()
            highlight_format.setBackground(QColor("#c2fc03"))  # Verde lime
            highlight_format.setForeground(QColor("#000000"))  # Testo nero
            
            # Applica il formato a tutte le date nella lista
            for i in range(self.donation_dates_list.count()):
                date_str = self.donation_dates_list.item(i).text()
                date = QDate.fromString(date_str, "dd/MM/yyyy")
                if date.isValid():
                    self.donation_calendar.setDateTextFormat(date, highlight_format)
                
        except Exception as e:
            logger.error(f"Errore nell'evidenziazione delle date: {str(e)}")

    def get_current_year(self):
        # Prima prova a ottenere l'anno dal database aperto
        settings = QSettings('Hemodos', 'DatabaseSettings')
        last_db = settings.value("last_database", "")
        if last_db:
            try:
                # Estrai l'anno dal nome del file (hemodos_YYYY.db)
                year = int(os.path.basename(last_db).split('_')[1].split('.')[0])
                return year
            except:
                pass
        
        # Se non riesce, usa l'anno corrente
        return QDate.currentDate().year()

    def add_donation_date(self):
        """Aggiunge una data di donazione"""
        try:
            selected_date = self.donation_calendar.selectedDate()
            
            # Verifica che la data sia nell'anno corrente
            if selected_date.year() != self.current_year:
                QMessageBox.warning(
                    self,
                    "Attenzione",
                    "Puoi aggiungere date solo per l'anno corrente"
                )
                return
            
            # Formatta la data
            date_str = selected_date.toString("yyyy-MM-dd")
            
            # Usa get_db_path per ottenere il percorso corretto
            base_path = get_base_path()
            year_path = os.path.join(base_path, str(self.current_year))
            
            # Crea la directory se non esiste
            os.makedirs(year_path, exist_ok=True)
            
            # Percorso del database delle date di donazione
            db_path = os.path.join(year_path, f"date_donazione_{self.current_year}.db")
            
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            
            # Crea la tabella se non esiste
            c.execute('''CREATE TABLE IF NOT EXISTS donation_dates
                         (date text PRIMARY KEY)''')
            
            # Inserisci la data
            try:
                c.execute("INSERT INTO donation_dates (date) VALUES (?)", (date_str,))
                conn.commit()
                
                # Aggiorna la lista
                self.load_donation_dates()
                
                # Aggiorna il calendario principale se esiste
                if hasattr(self, 'parent') and self.parent:
                    self.parent.highlight_donation_dates()
                
                QMessageBox.information(
                    self,
                    "Successo",
                    f"Data di donazione aggiunta: {selected_date.toString('dd/MM/yyyy')}"
                )
                
            except sqlite3.IntegrityError:
                QMessageBox.warning(
                    self,
                    "Attenzione",
                    "Questa data è già presente nel calendario donazioni"
                )
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Errore nell'aggiunta della data di donazione: {str(e)}")
            QMessageBox.critical(
                self,
                "Errore",
                f"Errore nell'aggiunta della data di donazione: {str(e)}"
            )

    def remove_donation_date(self):
        """Rimuove una data di donazione"""
        try:
            selected_items = self.donation_dates_list.selectedItems()
            if not selected_items:
                QMessageBox.warning(
                    self,
                    "Attenzione",
                    "Seleziona una data da rimuovere"
                )
                return
            
            selected_date = QDate.fromString(
                selected_items[0].text(),
                "dd/MM/yyyy"
            )
            
            # Conferma rimozione
            reply = QMessageBox.question(
                self,
                "Conferma rimozione",
                f"Vuoi davvero rimuovere la data {selected_date.toString('dd/MM/yyyy')}?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Rimuovi dal database
                db_path = get_db_path(selected_date, is_donation_dates=True)
                
                conn = sqlite3.connect(db_path)
                c = conn.cursor()
                
                c.execute(
                    "DELETE FROM donation_dates WHERE date = ?",
                    (selected_date.toString("yyyy-MM-dd"),)
                )
                
                conn.commit()
                conn.close()
                
                # Aggiorna la lista e il calendario
                self.load_donation_dates()
                
                # Aggiorna il calendario principale se esiste
                if hasattr(self, 'parent') and self.parent:
                    self.parent.highlight_donation_dates()
                
                QMessageBox.information(
                    self,
                    "Successo",
                    "Data rimossa con successo"
                )
                
        except Exception as e:
            logger.error(f"Errore nella rimozione della data: {str(e)}")
            QMessageBox.critical(
                self,
                "Errore",
                f"Errore nella rimozione della data: {str(e)}"
            )

    def load_donation_dates_for_year(self, year):
        """Carica le date di donazione per l'anno specificato"""
        try:
            # Pulisci la lista esistente
            self.donation_dates_list.clear()
            
            # Crea una data fittizia per l'anno selezionato
            dummy_date = QDate(year, 1, 1)
            
            # Ottieni le date dal database
            db_path = get_db_path(dummy_date, is_donation_dates=True)
            
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                c = conn.cursor()
                
                # Crea la tabella se non esiste
                c.execute('''CREATE TABLE IF NOT EXISTS donation_dates
                             (date text PRIMARY KEY)''')
                
                # Ottieni le date ordinate
                c.execute("SELECT date FROM donation_dates ORDER BY date")
                dates = c.fetchall()
                
                for date_tuple in dates:
                    date_str = date_tuple[0]
                    date = QDate.fromString(date_str, "yyyy-MM-dd")
                    if date.isValid():
                        # Aggiungi alla lista formattata
                        self.donation_dates_list.addItem(
                            date.toString("dd/MM/yyyy")
                        )
                
                conn.close()
                
                # Evidenzia le date nel calendario
                self.highlight_saved_dates()
                
        except Exception as e:
            logger.error(f"Errore nel caricamento delle date di donazione per l'anno {year}: {str(e)}")
            QMessageBox.critical(
                self,
                "Errore",
                f"Errore nel caricamento delle date di donazione: {str(e)}"
            )

    def select_logo(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleziona Logo", "",
            "Immagini (*.png *.jpg *.jpeg)"
        )
        if file_path:
            # Copia l'immagine nella cartella dell'app
            app_dir = os.path.dirname(get_db_path())
            logo_dir = os.path.join(app_dir, "assets")
            os.makedirs(logo_dir, exist_ok=True)
            
            # Copia con nome univoco basato sulla data
            ext = os.path.splitext(file_path)[1]
            new_name = f"logo_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
            new_path = os.path.join(logo_dir, new_name)
            
            shutil.copy2(file_path, new_path)
            self.settings.setValue("print_logo", new_path)
            
            # Aggiorna preview
            pixmap = QPixmap(new_path)
            self.logo_preview.setPixmap(pixmap.scaled(150, 150, Qt.KeepAspectRatio))

    def remove_logo(self):
        current_logo = self.settings.value("print_logo")
        if current_logo and os.path.exists(current_logo):
            os.remove(current_logo)
        self.settings.remove("print_logo")
        self.logo_preview.setPixmap(QPixmap())
        self.logo_preview.setText("Nessun logo")

    def update_history_text(self):
        """Aggiorna il testo della cronologia aggiornamenti"""
        history = self.settings.value("update_history", [])
        
        if not history:
            self.update_history.setText("Nessun aggiornamento nella cronologia")
            return
        
        text = ""
        for entry in history:
            date = datetime.fromisoformat(entry['date'].replace('Z', '+00:00'))
            formatted_date = date.strftime("%d/%m/%Y %H:%M")
            text += f"Versione {entry['version']} - {formatted_date}\n"
            text += f"Stato: {entry['status']}\n\n"
        
        self.update_history.setText(text)

    def init_years_tab(self):
        """Inizializza il tab per la gestione degli anni"""
        years_tab = QWidget()
        layout = QVBoxLayout()
        
        # Gruppo per la creazione di un nuovo anno
        new_year_group = QGroupBox("Crea Nuovo Anno")
        new_year_layout = QVBoxLayout()
        
        # Selezione anno
        year_layout = QHBoxLayout()
        year_layout.addWidget(QLabel("Anno:"))
        self.new_year_spin = QSpinBox()
        current_year = datetime.now().year
        self.new_year_spin.setRange(current_year, 2039)  # Limite al 2039
        self.new_year_spin.setValue(current_year + 1)
        year_layout.addWidget(self.new_year_spin)
        new_year_layout.addLayout(year_layout)
        
        # Pulsante crea
        create_btn = QPushButton("Crea Struttura Anno")
        create_btn.clicked.connect(self.create_year_structure)
        create_btn.setStyleSheet(self.button_style)
        new_year_layout.addWidget(create_btn)
        
        new_year_group.setLayout(new_year_layout)
        layout.addWidget(new_year_group)
        
        # Lista anni esistenti
        existing_group = QGroupBox("Anni Esistenti")
        existing_layout = QVBoxLayout()
        
        self.years_list = QListWidget()
        self.load_existing_years()
        existing_layout.addWidget(self.years_list)
        
        existing_group.setLayout(existing_layout)
        layout.addWidget(existing_group)
        
        years_tab.setLayout(layout)
        return years_tab

    def load_existing_years(self):
        """Carica la lista degli anni esistenti"""
        self.years_list.clear()
        base_path = os.path.dirname(get_db_path())
        
        if os.path.exists(base_path):
            years = set()
            for filename in os.listdir(base_path):
                if os.path.isdir(os.path.join(base_path, filename)):
                    try:
                        year = int(filename)
                        years.add(year)
                    except ValueError:
                        continue
            
            for year in sorted(years, reverse=True):
                item = QListWidgetItem(str(year))
                self.years_list.addItem(item)

    def create_year_structure(self):
        """Crea la struttura delle directory e dei database per il nuovo anno"""
        year = self.new_year_spin.value()
        
        try:
            self.year_manager.create_year_structure(year)
            
            # Aggiorna la lista degli anni
            self.load_existing_years()
            
            # Aggiorna il combo box nella tab Generali
            current_year = self.year_combo.currentText()
            self.year_combo.addItem(str(year))
            self.year_combo.setCurrentText(current_year)
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Errore",
                f"Errore nella creazione della struttura: {str(e)}"
            )
    
    def on_year_created(self, year):
        """Gestisce la creazione di un nuovo anno"""
        self.load_existing_years()  # Ricarica la lista degli anni

    def load_donation_dates(self):
        """Carica le date di donazione nella lista"""
        try:
            # Pulisci la lista esistente
            self.donation_dates_list.clear()
            
            # Ottieni le date dal database
            db_path = os.path.join(
                os.path.dirname(get_db_path()),
                str(self.current_year),
                f"date_donazione_{self.current_year}.db"
            )
            
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                c = conn.cursor()
                
                c.execute("SELECT date FROM donation_dates ORDER BY date")
                dates = c.fetchall()
                
                for date_tuple in dates:
                    date_str = date_tuple[0]
                    date = QDate.fromString(date_str, "yyyy-MM-dd")
                    if date.isValid():
                        # Aggiungi alla lista formattata
                        self.donation_dates_list.addItem(
                            date.toString("dd/MM/yyyy")
                        )
                
                conn.close()
                
            # Evidenzia le date nel calendario
            self.highlight_saved_dates()
            
        except Exception as e:
            logger.error(f"Errore nel caricamento delle date di donazione: {str(e)}")
            QMessageBox.critical(
                self,
                "Errore",
                f"Errore nel caricamento delle date di donazione: {str(e)}"
            )