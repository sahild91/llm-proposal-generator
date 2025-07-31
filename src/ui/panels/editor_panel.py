"""
Document Editor Panel
"""

import tkinter as tk
from tkinter import ttk, scrolledtext


class EditorPanel:
    """Panel for document editing"""
    
    def __init__(self, parent_frame, main_window):
        self.parent_frame = parent_frame
        self.main_window = main_window
        self.app = main_window.app
        
        self.setup_panel()
    
    def setup_panel(self):
        """Setup the editor panel"""
        # Editor panel frame
        self.editor_frame = ttk.Frame(self.parent_frame)
        self.parent_frame.add(self.editor_frame, weight=3)
        
        # Editor toolbar
        self._create_toolbar()
        
        # Editor notebook for different views
        self._create_editor_notebook()
    
    def _create_toolbar(self):
        """Create the editor toolbar"""
        toolbar_frame = ttk.Frame(self.editor_frame)
        toolbar_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Document type selector
        ttk.Label(toolbar_frame, text="Document:").pack(side=tk.LEFT)
        
        self.doc_type_var = tk.StringVar(value="proposal")
        doc_type_combo = ttk.Combobox(toolbar_frame, textvariable=self.doc_type_var, 
                                      values=["proposal", "feasibility"], state="readonly", width=12)
        doc_type_combo.pack(side=tk.LEFT, padx=(5, 15))
        doc_type_combo.bind('<<ComboboxSelected>>', self.on_document_type_change)
        
        # Editor buttons
        ttk.Button(toolbar_frame, text="Generate", command=self.generate_current_document).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_frame, text="Save", command=self.main_window.save_current).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_frame, text="Refine", command=self.main_window.refine_document).pack(side=tk.LEFT, padx=2)
        
        # Version info
        self.version_label = ttk.Label(toolbar_frame, text="No document loaded")
        self.version_label.pack(side=tk.RIGHT)
    
    def _create_editor_notebook(self):
        """Create the editor notebook with tabs"""
        self.editor_notebook = ttk.Notebook(self.editor_frame)
        self.editor_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Markdown editor tab
        self._create_editor_tab()
        
        # Preview tab (placeholder for future markdown preview)
        self._create_preview_tab()
    
    def _create_editor_tab(self):
        """Create the main editor tab"""
        editor_tab = ttk.Frame(self.editor_notebook)
        self.editor_notebook.add(editor_tab, text="Editor")
        
        # Text editor with scrollbar
        text_frame = ttk.Frame(editor_tab)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.text_editor = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, undo=True, maxundo=50)
        self.text_editor.pack(fill=tk.BOTH, expand=True)
        
        # Bind events for change detection
        self.text_editor.bind('<KeyRelease>', self.main_window.on_text_modified)
        self.text_editor.bind('<Button-1>', self.main_window.on_text_modified)
    
    def _create_preview_tab(self):
        """Create the preview tab"""
        preview_tab = ttk.Frame(self.editor_notebook)
        self.editor_notebook.add(preview_tab, text="Preview")
        
        self.preview_text = scrolledtext.ScrolledText(preview_tab, wrap=tk.WORD, state=tk.DISABLED)
        self.preview_text.pack(fill=tk.BOTH, expand=True)
    
    def on_document_type_change(self, event):
        """Handle document type change"""
        if self.main_window.current_project and self.main_window.check_unsaved_changes():
            self.main_window.load_document()
    
    def generate_current_document(self):
        """Generate the current document type"""
        if self.doc_type_var.get() == "proposal":
            self.main_window.generate_proposal()
        elif self.doc_type_var.get() == "feasibility":
            self.main_window.generate_feasibility()
    
    def load_document(self, project_name: str, doc_type: str, content: str = None):
        """Load document content into the editor"""
        self.doc_type_var.set(doc_type)
        
        # Clear editor
        self.text_editor.delete(1.0, tk.END)
        
        if content:
            self.text_editor.insert(1.0, content)
            
            # Update version info
            versions = self.app.project_manager.get_document_versions(project_name, doc_type)
            if versions:
                self.version_label.config(text=f"Version {versions[0]['version']}")
            else:
                self.version_label.config(text="Version 1")
        else:
            self.version_label.config(text="New document")
        
        # Reset unsaved changes flag
        self.main_window.unsaved_changes = False
        self.main_window.current_document_type = doc_type
        self.main_window.update_window_title()
    
    def get_content(self) -> str:
        """Get the current editor content"""
        return self.text_editor.get(1.0, tk.END + "-1c")
    
    def set_content(self, content: str):
        """Set the editor content"""
        self.text_editor.delete(1.0, tk.END)
        self.text_editor.insert(1.0, content)
    
    def clear_editor(self):
        """Clear the editor"""
        self.text_editor.delete(1.0, tk.END)
        self.version_label.config(text="No document loaded")
    
    def update_version_label(self, version_text: str):
        """Update the version label"""
        self.version_label.config(text=version_text)
    
    def get_current_document_type(self) -> str:
        """Get the current document type"""
        return self.doc_type_var.get()