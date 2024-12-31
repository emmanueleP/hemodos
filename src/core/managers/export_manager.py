from PyQt5.QtWidgets import QMessageBox, QFileDialog
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from core.utils import export_to_docx, print_data
from core.logger import logger
from gui.dialogs.daily_reservations_dialog import DailyReservationsDialog

class ExportManager:
    def __init__(self, main_window):
        self.main_window = main_window

    def export_to_docx(self, reservations_widget=None):
        """Esporta le prenotazioni in formato docx"""
        try:
            # Se non viene passato un widget specifico, usa quello della finestra corrente
            if not reservations_widget:
                dialog = self.main_window.findChild(DailyReservationsDialog)
                if dialog:
                    reservations_widget = dialog.reservations_widget
                    date = dialog.selected_date.toString("yyyy-MM-dd")
                else:
                    QMessageBox.warning(self.main_window, "Attenzione", "Apri prima una finestra delle prenotazioni")
                    return
            else:
                # Se il widget è stato passato, ottieni la data dal dialog parent
                dialog = reservations_widget.parent()
                date = dialog.selected_date.toString("yyyy-MM-dd")

            table = reservations_widget.get_table()
            if table.rowCount() == 0:
                QMessageBox.warning(self.main_window, "Attenzione", "Non ci sono dati da esportare")
                return

            # Apri dialog per scegliere dove salvare
            default_name = f"prenotazioni_{date}.docx"
            file_path, _ = QFileDialog.getSaveFileName(
                self.main_window,
                "Salva File",
                default_name,
                "Documenti Word (*.docx)"
            )
            
            if file_path:
                # Raccogli i dati dalla tabella
                data = self._collect_table_data(table)
                
                # Esporta
                if export_to_docx(date, data, file_path, logo_path=None):
                    QMessageBox.information(
                        self.main_window,
                        "Esportazione Completata",
                        f"File salvato in:\n{file_path}"
                    )
                
        except Exception as e:
            self.main_window._handle_error("l'esportazione", e)

    def print_table(self, reservations_widget=None):
        """Stampa la tabella delle prenotazioni"""
        try:
            if not reservations_widget:
                dialog = self.main_window.findChild(DailyReservationsDialog)
                if dialog:
                    reservations_widget = dialog.reservations_widget
                else:
                    QMessageBox.warning(self.main_window, "Attenzione", "Apri prima una finestra delle prenotazioni")
                    return

            printer = QPrinter(QPrinter.HighResolution)
            dialog = QPrintDialog(printer, self.main_window)
            
            if dialog.exec_() == QPrintDialog.Accepted:
                table = reservations_widget.get_table()
                data = self._collect_table_data(table)
                print_data(printer, data)
                
        except Exception as e:
            self.main_window._handle_error("la stampa", e)

    def _collect_table_data(self, table):
        """Raccoglie i dati dalla tabella"""
        data = []
        for row in range(table.rowCount()):
            time = table.item(row, 0).text()
            name = table.item(row, 1).text() if table.item(row, 1) else ""
            surname = table.item(row, 2).text() if table.item(row, 2) else ""
            first_donation = table.cellWidget(row, 3).currentText()
            stato = table.cellWidget(row, 4).currentText()
            
            if name.strip() or surname.strip():
                data.append([time, name, surname, first_donation, stato])
        
        return data 