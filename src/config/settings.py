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

class SettingsDialog(HemodosDialog):
    def __init__(self, parent=None):
        super().__init__(parent, "Impostazioni")
        self.settings = QSettings('Hemodos', 'DatabaseSettings')
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        # Create tab widget
        tab_widget = QTabWidget()
        
        # Generali tab (Date di donazione)
        general_tab = self.init_general_tab()
        tab_widget.addTab(general_tab, "Generali")
        
        # Cloud Storage tab
        cloud_tab = self.init_cloud_tab()
        tab_widget.addTab(cloud_tab, "Cloud Storage")
        
        # Appearance tab
        appearance_tab = self.init_appearance_tab()
        tab_widget.addTab(appearance_tab, "Aspetto")
        
        # Saving Options tab
        saving_tab = self.init_saving_tab()
        tab_widget.addTab(saving_tab, "Salvataggio")
        
        # Print tab
        print_tab = self.init_print_tab()
        tab_widget.addTab(print_tab, "Stampa")

        # Aggiornamento tab
        update_tab = self.init_update_tab()
        tab_widget.addTab(update_tab, "Aggiornamento")

        self.content_layout.addWidget(tab_widget)
        
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
        
        theme_group = QGroupBox("Tema")
        theme_layout = QFormLayout()
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Scuro", "Chiaro"])
        self.theme_combo.setCurrentText(self.settings.value("theme", "Scuro"))
        theme_layout.addRow("Seleziona tema:", self.theme_combo)
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)
        
        appearance_tab.setLayout(layout)
        return appearance_tab

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
        general_tab = QWidget()
        layout = QVBoxLayout()

        # Anno corrente (in base al database aperto o alla data)
        self.current_year = self.get_current_year()
        year_label = QLabel(f"Anno: {self.current_year}")
        year_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(year_label)

        # Date di donazione
        dates_group = QGroupBox(f"Date di Donazione {self.current_year}")
        dates_layout = QHBoxLayout()

        # Calendario
        calendar_layout = QVBoxLayout()
        self.donation_calendar = QCalendarWidget()
        self.donation_calendar.setGridVisible(True)
        
        # Evidenzia le date già salvate nel calendario
        self.highlight_saved_dates()
        
        calendar_layout.addWidget(self.donation_calendar)
        dates_layout.addLayout(calendar_layout)

        # Lista e pulsanti
        list_layout = QVBoxLayout()
        
        list_label = QLabel("Date selezionate:")
        list_layout.addWidget(list_label)
        
        self.donation_dates_list = QListWidget()
        list_layout.addWidget(self.donation_dates_list)

        # Pulsanti
        btn_layout = QHBoxLayout()
        add_date_btn = QPushButton("Aggiungi Data")
        add_date_btn.clicked.connect(self.add_donation_date)
        remove_date_btn = QPushButton("Rimuovi Data")
        remove_date_btn.clicked.connect(self.remove_donation_date)
        
        btn_layout.addWidget(add_date_btn)
        btn_layout.addWidget(remove_date_btn)
        list_layout.addLayout(btn_layout)

        dates_layout.addLayout(list_layout)
        dates_group.setLayout(dates_layout)
        layout.addWidget(dates_group)

        general_tab.setLayout(layout)
        
        # Carica le date esistenti nella lista
        self.load_donation_dates_for_year(self.current_year)
        
        return general_tab

    def highlight_saved_dates(self):
        """Evidenzia le date salvate nel calendario della tab Generali"""
        donation_format = QTextCharFormat()
        donation_format.setBackground(QColor("#c2fc03"))  # Verde lime
        donation_format.setForeground(QColor("#000000"))  # Testo nero
        
        dates = get_donation_dates(self.current_year)
        for date_str in dates:
            date = QDate.fromString(date_str, "yyyy-MM-dd")
            if date.isValid():
                self.donation_calendar.setDateTextFormat(date, donation_format)

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
        selected_date = self.donation_calendar.selectedDate()
        
        # Verifica che la data sia dell'anno corrente
        if selected_date.year() != self.current_year:
            QMessageBox.warning(self, "Errore", 
                              f"Puoi aggiungere solo date dell'anno {self.current_year}")
            return

        date_str = selected_date.toString("yyyy-MM-dd")
        
        if add_donation_date(self.current_year, date_str):
            # Aggiorna solo le visualizzazioni delle date di donazione
            self.load_donation_dates_for_year(self.current_year)
            self.highlight_saved_dates()
            if self.parent:
                # Aggiorna solo il formato delle date nel calendario principale
                self.parent.update_donation_dates_format()
        else:
            QMessageBox.warning(self, "Errore", "Impossibile aggiungere la data selezionata")

    def remove_donation_date(self):
        current_item = self.donation_dates_list.currentItem()
        
        if current_item:
            date_str = current_item.text()
            if delete_donation_date(self.current_year, date_str):
                # Aggiorna sia la lista che il calendario
                self.load_donation_dates_for_year(self.current_year)
                # Resetta e riapplica l'evidenziazione
                self.donation_calendar.setDateTextFormat(QDate(), QTextCharFormat())
                self.highlight_saved_dates()
                if self.parent:
                    self.parent.highlight_donation_dates()
            else:
                QMessageBox.warning(self, "Errore", "Impossibile rimuovere la data selezionata")

    def load_donation_dates_for_year(self, year):
        """Carica le date nella lista della tab Generali"""
        self.donation_dates_list.clear()
        dates = get_donation_dates(year)
        for date in sorted(dates):
            self.donation_dates_list.addItem(date)

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