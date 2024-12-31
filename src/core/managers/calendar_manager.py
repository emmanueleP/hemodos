from PyQt5.QtWidgets import QCalendarWidget
from PyQt5.QtGui import QTextCharFormat, QColor
from PyQt5.QtCore import QDate
from core.database import get_donation_dates
from core.logger import logger

class CalendarManager:
    def __init__(self, main_window):
        self.main_window = main_window

    def init_calendar(self, parent):
        """Inizializza il widget calendario"""
        calendar = QCalendarWidget(parent)
        calendar.setGridVisible(True)
        calendar.selectionChanged.connect(self.main_window.database_manager.on_date_changed)
        return calendar

    def highlight_donation_dates(self):
        """Evidenzia le date di donazione nel calendario"""
        try:
            self.main_window.calendar.setDateTextFormat(QDate(), QTextCharFormat())
            current_year = self.main_window.calendar.yearShown()
            
            donation_format = QTextCharFormat()
            donation_format.setBackground(QColor("#c2fc03"))
            donation_format.setForeground(QColor("#000000"))
            
            dates = get_donation_dates(current_year)
            for date_str in dates:
                date = QDate.fromString(date_str, "yyyy-MM-dd")
                if date.isValid():
                    self.main_window.calendar.setDateTextFormat(date, donation_format)
                
        except Exception as e:
            self.main_window._handle_error("l'evidenziazione delle date", e, show_dialog=False)

    def go_to_next_donation(self):
        """Va alla prossima data di donazione"""
        try:
            current_date = self.main_window.calendar.selectedDate()
            current_year = current_date.year()
            
            donation_dates = get_donation_dates(current_year)
            if not donation_dates:
                self.main_window.statusBar.showMessage("Nessuna data di donazione trovata", 3000)
                return
            
            dates = [QDate.fromString(d, "yyyy-MM-dd") for d in donation_dates if QDate.fromString(d, "yyyy-MM-dd").isValid()]
            dates.sort()
            
            next_date = next((d for d in dates if d > current_date), None)
            
            if not next_date:
                next_year_dates = get_donation_dates(current_year + 1)
                if next_year_dates:
                    next_date = QDate.fromString(min(next_year_dates), "yyyy-MM-dd")
            
            if next_date and next_date.isValid():
                self.main_window.calendar.setSelectedDate(next_date)
                self.main_window.statusBar.showMessage(
                    f"Prossima donazione: {next_date.toString('dd/MM/yyyy')}", 
                    3000
                )
            else:
                self.main_window.statusBar.showMessage(
                    "Nessuna data di donazione successiva trovata", 
                    3000
                )
            
        except Exception as e:
            self.main_window._handle_error("il passaggio alla donazione successiva", e) 