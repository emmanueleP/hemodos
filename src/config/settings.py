from gui.dialogs.base_dialog import HemodosDialog
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QComboBox, QFileDialog, QLineEdit,
                            QTabWidget, QWidget, QGroupBox, QFormLayout,
                            QCalendarWidget, QListWidget, QListWidgetItem,
                            QCheckBox, QSpinBox, QMessageBox, QTextBrowser,
                            QProgressDialog, QMainWindow, QInputDialog)
from PyQt5.QtCore import QSettings, QDate, Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator, QTextCharFormat, QColor, QPixmap
from core.database import (add_donation_date, get_donation_dates, delete_donation_date, 
                     get_db_path)
import os
import shutil
from datetime import datetime
import sqlite3
from core.managers.year_manager import YearManager
from core.logger import logger
from core.themes import THEMES
from core.delete_db_logic import get_base_path
from PyQt5.QtWidgets import QApplication

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
        
        # Prima inizializza l'UI
        self.init_ui()
        
        # Poi gestisci i pulsanti
        # Rimuovi i pulsanti standard
        for i in reversed(range(self.buttons_layout.count())): 
            widget = self.buttons_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
            
        # Crea nuovi pulsanti
        save_btn = QPushButton("Salva")
        save_btn.clicked.connect(self.save_settings)
        save_btn.setStyleSheet(self.button_style)
        
        cancel_btn = QPushButton("Annulla")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet(self.button_style)
        
        self.buttons_layout.addStretch()
        self.buttons_layout.addWidget(save_btn)
        self.buttons_layout.addWidget(cancel_btn)

    def init_ui(self):
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Generali tab (Date di donazione)
        general_tab = self.init_general_tab()
        self.tab_widget.addTab(general_tab, "Generali")
        
        # Gestione Anni tab
        years_tab = self.init_years_tab()
        self.tab_widget.addTab(years_tab, "Gestione Anni")
        
        # Syncthing tab
        sync_tab = self.init_cloud_tab()
        self.tab_widget.addTab(sync_tab, "Syncthing")
        
        # Appearance tab
        appearance_tab = self.init_appearance_tab()
        self.tab_widget.addTab(appearance_tab, "Aspetto")
        
        # Saving Options tab
        saving_tab = self.init_saving_tab()
        self.tab_widget.addTab(saving_tab, "Salvataggio")
        
        # Print tab
        print_tab = self.init_print_tab()
        self.tab_widget.addTab(print_tab, "Logo")

        self.content_layout.addWidget(self.tab_widget)
        
        # Aggiorna lo stato di Syncthing se è configurato
        if self.settings.value("cloud_service") == "Syncthing":
            self._update_syncthing_status()

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
        """Inizializza la tab per la sincronizzazione"""
        cloud_tab = QWidget()
        layout = QVBoxLayout()
        
        # Gruppo Syncthing
        syncthing_group = QGroupBox("Sincronizzazione (Syncthing)")
        syncthing_layout = QVBoxLayout()
        
        # Status
        status_layout = QHBoxLayout()
        status_label = QLabel("Stato:")
        self.status_value = QLabel("Verificando...")
        status_layout.addWidget(status_label)
        status_layout.addWidget(self.status_value)
        status_layout.addStretch()
        syncthing_layout.addLayout(status_layout)
        
        # ID Dispositivo
        device_layout = QHBoxLayout()
        device_label = QLabel("ID Dispositivo:")
        self.device_id = QLineEdit()
        self.device_id.setReadOnly(True)
        copy_button = QPushButton("Copia")
        copy_button.clicked.connect(lambda: self._copy_to_clipboard(self.device_id.text()))
        copy_button.setStyleSheet(self.button_style)
        device_layout.addWidget(device_label)
        device_layout.addWidget(self.device_id)
        device_layout.addWidget(copy_button)
        syncthing_layout.addLayout(device_layout)
        
        # Cartella sincronizzata
        folder_layout = QHBoxLayout()
        folder_label = QLabel("Cartella:")
        self.folder_path = QLineEdit()
        self.folder_path.setReadOnly(True)
        folder_layout.addWidget(folder_label)
        folder_layout.addWidget(self.folder_path)
        syncthing_layout.addLayout(folder_layout)
        
        # Pulsanti azione
        button_layout = QHBoxLayout()
        
        # Aggiungi dispositivo
        add_device_btn = QPushButton("Aggiungi Dispositivo")
        add_device_btn.clicked.connect(self._add_device)
        add_device_btn.setStyleSheet(self.button_style)
        button_layout.addWidget(add_device_btn)
        
        # Apri interfaccia web
        web_ui_btn = QPushButton("Apri Interfaccia Web")
        web_ui_btn.clicked.connect(lambda: self._open_web_ui())
        web_ui_btn.setStyleSheet(self.button_style)
        button_layout.addWidget(web_ui_btn)
        
        # Riavvia Syncthing
        restart_btn = QPushButton("Riavvia Syncthing")
        restart_btn.clicked.connect(self._restart_syncthing)
        restart_btn.setStyleSheet(self.button_style)
        button_layout.addWidget(restart_btn)
        
        syncthing_layout.addLayout(button_layout)
        
        # Aggiungi descrizione
        desc_label = QLabel(
            "Syncthing permette di sincronizzare automaticamente il database "
            "tra più dispositivi in modo sicuro e privato, senza dipendere da servizi cloud di terze parti."
        )
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666; font-size: 11px;")
        syncthing_layout.addWidget(desc_label)
        
        syncthing_group.setLayout(syncthing_layout)
        layout.addWidget(syncthing_group)
        
        cloud_tab.setLayout(layout)
        return cloud_tab

    def _update_syncthing_status(self):
        """Aggiorna lo stato di Syncthing"""
        try:
            if hasattr(self.parent, 'syncthing_manager'):
                # Ottieni lo stato
                status = self.parent.syncthing_manager.get_status()
                self.status_value.setText(status['state'])
                
                # Ottieni l'ID del dispositivo
                device_id = self.parent.syncthing_manager.get_device_id()
                self.device_id.setText(device_id)
                
                # Ottieni il percorso della cartella
                folder_path = self.parent.syncthing_manager.get_folder_path()
                self.folder_path.setText(folder_path)
            else:
                self.status_value.setText("Syncthing non inizializzato")
                
        except Exception as e:
            logger.error(f"Errore nell'aggiornamento dello stato Syncthing: {str(e)}")
            self.status_value.setText("Errore")

    def _copy_to_clipboard(self, text):
        """Copia il testo negli appunti"""
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        self.parent.status_manager.show_message("ID copiato negli appunti", 2000)

    def _add_device(self):
        """Mostra il dialog per aggiungere un nuovo dispositivo"""
        device_id, ok = QInputDialog.getText(
            self,
            "Aggiungi Dispositivo",
            "Inserisci l'ID del dispositivo da aggiungere:"
        )
        if ok and device_id:
            try:
                self.parent.syncthing_manager.add_device(device_id)
                QMessageBox.information(
                    self,
                    "Successo",
                    "Dispositivo aggiunto correttamente"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Errore",
                    f"Errore nell'aggiunta del dispositivo:\n{str(e)}"
                )

    def _open_web_ui(self):
        """Apre l'interfaccia web di Syncthing"""
        import webbrowser
        webbrowser.open("http://localhost:8384")

    def _restart_syncthing(self):
        """Riavvia il servizio Syncthing"""
        try:
            if hasattr(self.parent, 'syncthing_manager'):
                self.parent.syncthing_manager.restart()
                QMessageBox.information(
                    self,
                    "Successo",
                    "Syncthing riavviato correttamente"
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Errore",
                f"Errore nel riavvio di Syncthing:\n{str(e)}"
            )

    def init_saving_tab(self):
        saving_tab = QWidget()
        layout = QVBoxLayout()
        
        # Auto-save group
        autosave_group = QGroupBox("Salvataggio Automatico")
        autosave_layout = QVBoxLayout()

        self.autosave_check = QCheckBox("Abilita salvataggio automatico")
        self.autosave_check.setChecked(self.settings.value("autosave_enabled", False, type=bool))
        autosave_layout.addWidget(self.autosave_check)

        # Interval group dentro autosave_group
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("Salvataggio automatico ogni:"))
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 60)
        self.interval_spin.setValue(self.settings.value("autosave_interval", 5, type=int))
        interval_layout.addWidget(self.interval_spin)
        interval_layout.addWidget(QLabel("minuti"))
        interval_layout.addStretch()
        
        # Aggiungi interval_layout a autosave_layout
        autosave_layout.addLayout(interval_layout)
        
        # Imposta il layout per autosave_group
        autosave_group.setLayout(autosave_layout)
        
        # Aggiungi il gruppo al layout principale
        layout.addWidget(autosave_group)
        layout.addStretch()
        
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

    def save_settings(self):
        """Salva tutte le impostazioni e chiude il dialog"""
        try:
            # Salva le impostazioni generali
            self.settings.setValue("theme", self.theme_combo.currentText())
            self.settings.setValue("cloud_service", self.cloud_service.currentText())
            self.settings.setValue("cloud_path", self.path_edit.text())
            self.settings.setValue("autosave_enabled", self.autosave_check.isChecked())
            self.settings.setValue("autosave_interval", self.interval_spin.value())
            
            # Trova la MainWindow
            main_window = None
            current = self.parent  # Usa la proprietà parent invece del metodo
            while current:
                if isinstance(current, QMainWindow):
                    main_window = current
                    break
                current = current.parent  # Usa la proprietà parent
            
            # Aggiorna l'interfaccia principale se disponibile
            if main_window:
                if hasattr(main_window, 'theme_manager'):
                    main_window.theme_manager.apply_theme()
                if hasattr(main_window, 'calendar_manager'):
                    main_window.calendar_manager.highlight_donation_dates()
                if hasattr(main_window, 'autosave_manager'):
                    main_window.autosave_manager.setup_autosave()
            
            self.accept()  # Chiude il dialog dopo il salvataggio
            
        except Exception as e:
            logger.error(f"Errore durante il salvataggio delle impostazioni: {str(e)}")
            QMessageBox.critical(self, "Errore", f"Errore durante il salvataggio: {str(e)}")

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
                    if hasattr(self.parent, 'calendar_manager'):
                        self.parent.calendar_manager.highlight_donation_dates()
                
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
        
        # Lista anni esistenti
        existing_group = QGroupBox("Anni Esistenti")
        existing_layout = QVBoxLayout()
        
        # Aggiungi label informativa
        info_label = QLabel("Anni presenti nel sistema:")
        info_label.setStyleSheet("font-weight: bold;")
        existing_layout.addWidget(info_label)
        
        # Lista con gli anni
        self.years_list = QListWidget()
        self.years_list.setMinimumHeight(200)
        self.load_existing_years()
        existing_layout.addWidget(self.years_list)
        
        # Aggiungi pulsante refresh
        refresh_btn = QPushButton("Aggiorna Lista")
        refresh_btn.clicked.connect(self.load_existing_years)
        existing_layout.addWidget(refresh_btn)
        
        existing_group.setLayout(existing_layout)
        layout.addWidget(existing_group)
        
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
        
        years_tab.setLayout(layout)
        return years_tab

    def load_existing_years(self):
        """Carica la lista degli anni esistenti"""
        try:
            self.years_list.clear()
            
            # Ottieni il percorso base
            settings = QSettings('Hemodos', 'DatabaseSettings')
            service = settings.value("cloud_service", "Locale")
            
            if service == "Locale":
                base_path = os.path.expanduser("~/Documents/Hemodos")
            else:
                cloud_path = settings.value("cloud_path", "")
                base_path = os.path.join(cloud_path, "Hemodos")
            
            if os.path.exists(base_path):
                years = []
                for item in os.listdir(base_path):
                    item_path = os.path.join(base_path, item)
                    if os.path.isdir(item_path):
                        try:
                            year = int(item)
                            years.append(year)
                        except ValueError:
                            continue
                
                # Ordina gli anni in ordine decrescente
                years.sort(reverse=True)
                
                # Aggiungi gli anni alla lista
                for year in years:
                    item = QListWidgetItem(f"Anno {year}")
                    item.setTextAlignment(Qt.AlignCenter)
                    self.years_list.addItem(item)
                    
                if not years:
                    self.years_list.addItem("Nessun anno presente")
            else:
                self.years_list.addItem("Directory Hemodos non trovata")
                
        except Exception as e:
            logger.error(f"Errore nel caricamento degli anni: {str(e)}")
            self.years_list.addItem("Errore nel caricamento degli anni")

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
        self.load_donation_dates_for_year(year)

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

    def _init_year_group(self):
        """Inizializza il gruppo delle impostazioni dell'anno"""
        year_group = QGroupBox("Gestione Anno")
        layout = QVBoxLayout()
        
        # Aggiungi pulsante per creare struttura
        create_structure_btn = QPushButton("Crea Struttura Anno")
        create_structure_btn.clicked.connect(self._create_year_structure)
        layout.addWidget(create_structure_btn)
        
        year_group.setLayout(layout)
        return year_group

    def _create_year_structure(self):
        """Crea la struttura dell'anno corrente"""
        try:
            year = int(self.year_combo.currentText())  # Usa l'anno selezionato
            if self.main_window.year_manager.create_year_structure(year):
                QMessageBox.information(
                    self,
                    "Successo",
                    f"Struttura anno {year} creata correttamente"
                )
                # Aggiorna la lista delle date
                self.load_donation_dates_for_year(year)
            else:
                QMessageBox.critical(
                    self,
                    "Errore",
                    f"Errore nella creazione della struttura anno {year}"
                )
        except Exception as e:
            logger.error(f"Errore nella creazione struttura anno: {str(e)}")
            QMessageBox.critical(self, "Errore", str(e))