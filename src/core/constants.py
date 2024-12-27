from enum import Enum

class DonationStatus(Enum):
    NOT_DONE = "Non effettuata"
    DONE = "Sì"
    CANCELLED = "Annullata"
    POSTPONED = "Rimandata"

class CloudService(Enum):
    LOCAL = "Locale"
    ONEDRIVE = "OneDrive"
    GDRIVE = "Google Drive"

# Configurazioni temporali
TIME_RANGE = {
    'START': '07:50',
    'END': '12:10',
    'FIRST_DONATION_LIMIT': '10:00',
    'INTERVAL': 5  # minuti
}

# Configurazioni UI
UI_COLORS = {
    'PRIMARY': '#004d4d',
    'SECONDARY': '#006666',
    'SUCCESS': '#00cc66',
    'WARNING': '#ff9933',
    'DANGER': '#ff4444',
    'LIGHT': '#f8f9fa',
    'DARK': '#343a40'
}

# Percorsi predefiniti
DEFAULT_PATHS = {
    'DOCUMENTS': '~/Documents/Hemodos',
    'ONEDRIVE': '~/OneDrive/Hemodos',
    'GDRIVE': '~/Google Drive/Hemodos'
}

# Formati file
FILE_FORMATS = {
    'DATABASE': '.db',
    'EXPORT': '.docx',
    'LOG': '.log',
    'CONFIG': '.json'
} 