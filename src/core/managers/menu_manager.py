from PyQt5.QtWidgets import QMenuBar, QMenu, QAction, QStatusBar, QLabel, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from gui.dialogs.daily_reservations_dialog import DailyReservationsDialog
import os
import json

class MenuManager:
    def __init__(self, main_window):
        self.main_window = main_window

    def create_menu_bar(self, main_window):
        """Crea la barra dei menu"""
        menubar = main_window.menuBar()

        # Menu File
        file_menu = menubar.addMenu('File')
        
        # Database dialog
        database_action = QAction(QIcon('src/assets/refresh_data.png'), 'Gestione Database', main_window)
        database_action.setShortcut('Ctrl+D')
        database_action.triggered.connect(main_window.show_database_dialog)
        file_menu.addAction(database_action)
        
        # Save action
        save_action = QAction(QIcon('src/assets/diskette.png'), 'Salva tutto', main_window)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(main_window.save_current)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()

        # Export action
        export_action = QAction(QIcon('src/assets/doc.png'), 'Esporta in Word (.docx)', main_window)
        export_action.setShortcut('Ctrl+W')
        export_action.triggered.connect(self.main_window.export_manager.export_to_docx)
        file_menu.addAction(export_action)

        # Print action
        print_action = QAction(QIcon('src/assets/printer.png'), 'Stampa', main_window)
        print_action.setShortcut('Ctrl+P')
        print_action.triggered.connect(self.main_window.export_manager.print_table)
        file_menu.addAction(print_action)
        
        file_menu.addSeparator()
       
        
        # Exit action
        exit_action = QAction(QIcon('src/assets/exit_64px.png'), 'Esci', main_window)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(main_window.close)
        file_menu.addAction(exit_action)

        # Menu Tools
        tools_menu = menubar.addMenu('Strumenti')
        
        # History action
        history_action = QAction(QIcon('src/assets/history.png'), 'Cronologia', main_window)
        history_action.triggered.connect(main_window.show_history)
        tools_menu.addAction(history_action)
        
        # Delete action
        delete_action = QAction(QIcon('src/assets/trash.png'), 'Elimina Database...', main_window)
        delete_action.triggered.connect(main_window.show_delete_dialog)
        tools_menu.addAction(delete_action)
        
        tools_menu.addSeparator()
        
        # Statistics action
        statistics_action = QAction(QIcon('src/assets/stats.png'), 'Statistiche', main_window)
        statistics_action.triggered.connect(main_window.show_statistics)
        tools_menu.addAction(statistics_action)

        # Menu Settings
        settings_menu = menubar.addMenu('Impostazioni')
        
        # Preferences action
        preferences_action = QAction(QIcon('src/assets/cogwheel.png'), 'Preferenze', main_window)
        preferences_action.triggered.connect(main_window.show_settings)
        settings_menu.addAction(preferences_action)
        
        # HemodosAdmin action (solo per admin)
        admin_action = QAction(QIcon('src/assets/cogwheel.png'), 'HemodosAdmin', main_window)
        admin_action.triggered.connect(self._show_admin)
        settings_menu.addAction(admin_action)
        
        # Verifica se l'utente è admin
        users_file = os.path.join(main_window.settings.value("cloud_path", ""), ".hemodos_users")
        if os.path.exists(users_file):
            with open(users_file, 'r') as f:
                users = json.load(f)
                current_user = main_window.settings.value("current_user")
                if current_user not in users or not users[current_user].get('is_admin', False):
                    admin_action.setEnabled(False)

        # Menu Info
        info_menu = menubar.addMenu('Info')
        
        # Manual action
        manual_action = QAction(QIcon('src/assets/user_guide.png'), 'Manuale', main_window)
        manual_action.setShortcut('F1')
        manual_action.triggered.connect(main_window.show_manual)
        info_menu.addAction(manual_action)
        
        # Aggiornamenti
        updates_action = QAction(QIcon('src/assets/update.png'), 'Controlla Aggiornamenti', main_window)
        updates_action.setShortcut('Ctrl+U')
        updates_action.triggered.connect(self._show_updates)
        info_menu.addAction(updates_action)

        # About action
        about_action = QAction('Informazioni su Hemodos', main_window)
        about_action.triggered.connect(main_window.show_info)
        info_menu.addAction(about_action)

    def _save_current_reservations(self):
        """Salva le prenotazioni della finestra corrente"""
        dialog = self.main_window.findChild(DailyReservationsDialog)
        if dialog:
            dialog.save_reservations()
        else:
            QMessageBox.warning(
                self.main_window,
                "Attenzione",
                "Apri prima una finestra delle prenotazioni"
            )

    def _show_updates(self):
        """Mostra il dialog degli aggiornamenti"""
        from gui.dialogs.update_dialog import UpdateDialog
        dialog = UpdateDialog(self.main_window)
        dialog.exec_()

    def _show_manual(self):
        """Mostra il manuale"""
        from gui.dialogs.manual_dialog import ManualDialog
        dialog = ManualDialog(self.main_window)
        dialog.exec_()

    def _show_info(self):
        """Mostra le informazioni"""
        from gui.dialogs.info_dialog import InfoDialog
        dialog = InfoDialog(self.main_window)
        dialog.exec_()

    def _show_admin(self):
        """Mostra la finestra di amministrazione"""
        from gui.admin.hemodos_admin import HemodosAdmin
        dialog = HemodosAdmin(self.main_window)
        dialog.exec_()