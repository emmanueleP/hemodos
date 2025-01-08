from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtGui import QTextDocument, QFont
from PyQt5.QtCore import Qt, QSettings
import os

class PrintManager:
    def __init__(self, main_window):
        self.main_window = main_window

    def print_reservations(self, dialog):
        """Stampa le prenotazioni del giorno selezionato"""
        try:
            printer = QPrinter(QPrinter.HighResolution)
            printer.setPageSize(QPrinter.A4)
            
            print_dialog = QPrintDialog(printer, dialog)
            if print_dialog.exec_() == QPrintDialog.Accepted:
                # Crea il documento
                document = QTextDocument()
                
                # Ottieni il logo dalle impostazioni
                settings = QSettings('Hemodos', 'DatabaseSettings')
                logo_path = settings.value("print_logo", '')
                
                # Ottieni i dati dalla tabella
                data = dialog._collect_table_data()
                date = dialog.selected_date.toString("dd/MM/yyyy")
                
                if data:
                    # Crea l'HTML per il documento
                    html = f"""
                    <html>
                    <head>
                        <style>
                            body {{ font-family: Arial; }}
                            .title {{ 
                                color: red; 
                                font-size: 24pt; 
                                text-align: center;
                                font-weight: bold;
                                margin-bottom: 20px;
                            }}
                            .date {{
                                font-size: 12pt;
                                text-align: center;
                                font-weight: bold;
                                margin: 10px 0;
                            }}
                            table {{
                                width: 100%;
                                border-collapse: collapse;
                                margin-top: 20px;
                            }}
                            th {{
                                background-color: #E0E0E0;
                                padding: 5px;
                                border: 1px solid black;
                                font-weight: bold;
                            }}
                            td {{
                                padding: 5px;
                                border: 1px solid black;
                            }}
                            .footer {{
                                margin-top: 20px;
                                text-align: right;
                                font-size: 8pt;
                                color: #808080;
                            }}
                        </style>
                    </head>
                    <body>
                        <div class="title">Prenotazioni</div>
                        <div class="date">Data: {date}</div>
                        <table>
                            <tr>
                                <th width="15%">Orario</th>
                                <th width="30%">Nome</th>
                                <th width="30%">Cognome</th>
                                <th width="25%">Prima Donazione</th>
                            </tr>
                    """
                    
                    for time, name, surname, first_donation, _ in data:
                        first_donation_text = "Sì" if first_donation == "Sì" else ""
                        html += f"""
                            <tr>
                                <td>{time}</td>
                                <td>{name}</td>
                                <td>{surname}</td>
                                <td>{first_donation_text}</td>
                            </tr>
                        """
                    
                    # Aggiungi il footer
                    from datetime import datetime
                    current_time = datetime.now().strftime("%d/%m/%Y alle %H:%M:%S")
                    html += f"""
                        </table>
                        <div class="footer">
                            Creato da Hemodos il {current_time}
                        </div>
                    </body>
                    </html>
                    """
                    
                    document.setHtml(html)
                    document.print_(printer)
                    dialog.show_status_message("Stampa completata", 3000)
                else:
                    dialog.show_status_message("Nessun dato da stampare", 3000)
                    
        except Exception as e:
            dialog.show_status_message(f"Errore durante la stampa: {str(e)}", 3000)

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