class HemodosError(Exception):
    """Classe base per le eccezioni di Hemodos"""
    pass

class DatabaseError(HemodosError):
    """Errore nelle operazioni del database"""
    pass

class ConfigError(HemodosError):
    """Errore nella gestione della configurazione"""
    pass

class CloudError(HemodosError):
    """Errore nella sincronizzazione cloud"""
    pass

class ValidationError(HemodosError):
    """Errore nella validazione dei dati"""
    pass

class FileOperationError(HemodosError):
    """Errore nelle operazioni sui file"""
    pass

class UpdateError(HemodosError):
    """Errore durante l'aggiornamento"""
    pass 