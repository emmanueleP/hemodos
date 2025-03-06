class SettingsDialog(HemodosDialog):
    def init_ui(self):
        # ... existing code ...
        
        # Icone delle impostazioni
        theme_button.setIcon(QIcon(self.paths_manager.get_asset_path('theme_64px.png')))
        backup_button.setIcon(QIcon(self.paths_manager.get_asset_path('backup_64px.png'))) 