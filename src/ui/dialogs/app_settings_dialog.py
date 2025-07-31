"""
Application Settings Dialog
"""

import tkinter as tk
from tkinter import ttk, messagebox


class AppSettingsDialog:
    """Dialog for application settings"""
    
    def __init__(self, parent, current_config):
        self.result = None
        self.current_config = current_config.copy()
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Application Settings")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        self.load_current_settings()
        self.dialog.wait_window()
    
    def create_widgets(self):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Auto-save settings
        self._create_autosave_section(main_frame)
        
        # Export settings
        self._create_export_section(main_frame)
        
        # Backup settings
        self._create_backup_section(main_frame)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(button_frame, text="Save", command=self.save_settings).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.RIGHT)
    
    def _create_autosave_section(self, parent):
        """Create auto-save settings section"""
        autosave_frame = ttk.LabelFrame(parent, text="Auto-save Settings", padding=15)
        autosave_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.auto_save_var = tk.BooleanVar()
        ttk.Checkbutton(autosave_frame, text="Enable auto-save", 
                        variable=self.auto_save_var).pack(anchor=tk.W)
        
        interval_frame = ttk.Frame(autosave_frame)
        interval_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(interval_frame, text="Auto-save interval (seconds):").pack(side=tk.LEFT)
        self.interval_var = tk.StringVar(value="30")
        ttk.Entry(interval_frame, textvariable=self.interval_var, width=10).pack(side=tk.LEFT, padx=(10, 0))
    
    def _create_export_section(self, parent):
        """Create export settings section"""
        export_frame = ttk.LabelFrame(parent, text="Export Settings", padding=15)
        export_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(export_frame, text="Default export format:").pack(anchor=tk.W)
        self.export_format_var = tk.StringVar(value="pdf")
        format_frame = ttk.Frame(export_frame)
        format_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Radiobutton(format_frame, text="PDF", variable=self.export_format_var, value="pdf").pack(side=tk.LEFT)
        ttk.Radiobutton(format_frame, text="DOCX", variable=self.export_format_var, value="docx").pack(side=tk.LEFT, padx=(10, 0))
        ttk.Radiobutton(format_frame, text="HTML", variable=self.export_format_var, value="html").pack(side=tk.LEFT, padx=(10, 0))
        ttk.Radiobutton(format_frame, text="Markdown", variable=self.export_format_var, value="markdown").pack(side=tk.LEFT, padx=(10, 0))
    
    def _create_backup_section(self, parent):
        """Create backup settings section"""
        backup_frame = ttk.LabelFrame(parent, text="Backup Settings", padding=15)
        backup_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.backup_enabled_var = tk.BooleanVar()
        ttk.Checkbutton(backup_frame, text="Enable automatic backups", 
                        variable=self.backup_enabled_var).pack(anchor=tk.W)
        
        versions_frame = ttk.Frame(backup_frame)
        versions_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(versions_frame, text="Maximum versions to keep:").pack(side=tk.LEFT)
        self.max_versions_var = tk.StringVar(value="10")
        ttk.Entry(versions_frame, textvariable=self.max_versions_var, width=10).pack(side=tk.LEFT, padx=(10, 0))
    
    def load_current_settings(self):
        """Load current settings into the dialog"""
        if self.current_config:
            self.auto_save_var.set(self.current_config.get('auto_save', True))
            self.interval_var.set(str(self.current_config.get('auto_save_interval', 30)))
            self.export_format_var.set(self.current_config.get('default_export_format', 'pdf'))
            self.backup_enabled_var.set(self.current_config.get('backup_enabled', True))
            self.max_versions_var.set(str(self.current_config.get('max_versions', 10)))
    
    def save_settings(self):
        """Save the settings"""
        try:
            interval = int(self.interval_var.get())
            max_versions = int(self.max_versions_var.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for interval and max versions")
            return
        
        self.result = {
            'auto_save': self.auto_save_var.get(),
            'auto_save_interval': interval,
            'default_export_format': self.export_format_var.get(),
            'backup_enabled': self.backup_enabled_var.get(),
            'max_versions': max_versions,
            'theme': self.current_config.get('theme', 'default')
        }
        
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel dialog"""
        self.dialog.destroy()