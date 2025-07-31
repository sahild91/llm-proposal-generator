"""
Project Creation Dialog
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext


class ProjectDialog:
    """Dialog for creating new projects"""
    
    def __init__(self, parent, title="New Project", app=None):
        self.result = None
        self.parent = parent
        self.app = app
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x700")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        self.dialog.wait_window()
    
    def create_widgets(self):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Project name
        ttk.Label(main_frame, text="Project Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.project_name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.project_name_var, width=40).grid(
            row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Client name
        ttk.Label(main_frame, text="Client Name:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.client_name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.client_name_var, width=40).grid(
            row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Project type
        ttk.Label(main_frame, text="Project Type:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.project_type_var = tk.StringVar(value="Software")
        type_combo = ttk.Combobox(main_frame, textvariable=self.project_type_var, 
                                  values=["Software", "Hardware", "Hybrid"], width=37)
        type_combo.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Expected duration
        ttk.Label(main_frame, text="Expected Duration:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.duration_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.duration_var, width=40).grid(
            row=3, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Requirements
        ttk.Label(main_frame, text="Requirements:").grid(row=4, column=0, sticky=tk.NW, pady=5)
        self.requirements_text = scrolledtext.ScrolledText(main_frame, width=50, height=10)
        self.requirements_text.grid(row=4, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Hardware components
        ttk.Label(main_frame, text="Hardware Components:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.hardware_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.hardware_var, width=40).grid(
            row=5, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        ttk.Label(main_frame, text="(comma-separated)", font=('Arial', 8)).grid(
            row=6, column=1, sticky=tk.W, padx=(10, 0))
        
        # Software modules
        ttk.Label(main_frame, text="Software Modules:").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.software_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.software_var, width=40).grid(
            row=7, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        ttk.Label(main_frame, text="(comma-separated)", font=('Arial', 8)).grid(
            row=8, column=1, sticky=tk.W, padx=(10, 0))
        
        # Document Author
        ttk.Label(main_frame, text="Document Author:").grid(row=9, column=0, sticky=tk.W, pady=5)
        self.author_var = tk.StringVar()
        author_combo = ttk.Combobox(main_frame, textvariable=self.author_var, width=37)
        author_combo.grid(row=9, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Get authors from app config if available
        if self.app and hasattr(self.app, 'config'):
            authors = ["Default"] + self.app.config.get('company', {}).get('authors', [])
        else:
            authors = ["Default", "Project Manager", "Technical Lead", "Senior Architect"]
        
        author_combo['values'] = authors
        author_combo.set(authors[0] if authors else 'Default')
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=10, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Create", command=self.create_project).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.LEFT, padx=5)
    
    def create_project(self):
        """Create the project"""
        if not self.project_name_var.get().strip():
            messagebox.showerror("Error", "Project name is required")
            return
        
        # Parse hardware components and software modules
        hardware_components = [comp.strip() for comp in self.hardware_var.get().split(',') if comp.strip()]
        software_modules = [mod.strip() for mod in self.software_var.get().split(',') if mod.strip()]
        
        self.result = {
            'project_name': self.project_name_var.get().strip(),
            'client_name': self.client_name_var.get().strip(),
            'project_type': self.project_type_var.get(),
            'expected_duration': self.duration_var.get().strip(),
            'requirements': self.requirements_text.get(1.0, tk.END + "-1c").strip(),
            'hardware_components': hardware_components,
            'software_modules': software_modules,
            'author': self.author_var.get() if self.author_var.get() != 'Default' else ''
        }
        
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel dialog"""
        self.dialog.destroy()