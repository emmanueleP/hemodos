def closeEvent(self, event):
    """Gestisce la chiusura dell'applicazione"""
    from core.sync_manager import CloudSync
    
    # Esegui la sincronizzazione
    sync_manager = CloudSync(self.paths_manager)
    if not sync_manager.sync_on_exit(self):
        event.ignore()
        return
        
    # Procedi con la chiusura
    event.accept() 