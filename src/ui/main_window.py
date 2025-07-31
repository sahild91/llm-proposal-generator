"""
Main Window UI for the LLM Proposal Generator
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from typing import Dict, Any, Optional
import threading
import json
import sys
import os
import subprocess
from pathlib import Path
from datetime import datetime

from src.llm_client import LLMClient

class MainWindow:
    """Main application window"""
    
    def __init__(self, root: tk.Tk, app):
        self.root = root
        self.app = app
        self.current_project = None
        self.current_document_type = None
        self.unsaved_changes = False
        
        self.setup_ui()
        self.refresh_project_list()
    
    def setup_ui(self):
        """Setup the main UI components"""
        # Create main menu
        self.create_menu()
        
        # Create main layout
        self.create_main_layout()
        
        # Setup status bar
        self.create_status_bar()
    
    def create_menu(self):
        """Create the main menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Project", command=self.new_project, accelerator="Ctrl+N")
        file_menu.add_separator()
        file_menu.add_command(label="Save", command=self.save_current, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.save_as)
        file_menu.add_separator()
        
        # Export submenu
        export_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Export", menu=export_menu)
        export_menu.add_command(label="Export as PDF", command=lambda: self.export_document('pdf'))
        export_menu.add_command(label="Export as DOCX", command=lambda: self.export_document('docx'))
        export_menu.add_command(label="Export as HTML", command=lambda: self.export_document('html'))
        export_menu.add_command(label="Export as Markdown", command=lambda: self.export_document('markdown'))
        
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.app.on_closing)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Find", command=self.find_text, accelerator="Ctrl+F")
        edit_menu.add_command(label="Replace", command=self.replace_text, accelerator="Ctrl+H")
        
        # LLM menu
        llm_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="LLM", menu=llm_menu)
        llm_menu.add_command(label="Generate Proposal", command=self.generate_proposal)
        llm_menu.add_command(label="Generate Feasibility", command=self.generate_feasibility)
        llm_menu.add_command(label="Refine Document", command=self.refine_document)
        llm_menu.add_separator()
        llm_menu.add_command(label="Test Connection", command=self.test_llm_connection)
        llm_menu.add_command(label="Settings", command=self.show_llm_settings)
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="LLM Settings", command=self.show_llm_settings)
        settings_menu.add_command(label="Company Settings", command=self.show_company_settings)
        settings_menu.add_separator()
        settings_menu.add_command(label="Application Settings", command=self.show_app_settings)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-n>', lambda e: self.new_project())
        self.root.bind('<Control-s>', lambda e: self.save_current())
        self.root.bind('<Control-z>', lambda e: self.undo())
        self.root.bind('<Control-y>', lambda e: self.redo())
        self.root.bind('<Control-f>', lambda e: self.find_text())
        self.root.bind('<Control-h>', lambda e: self.replace_text())
    
    def create_main_layout(self):
        """Create the main layout with panels"""
        # Create main paned window
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Project list
        self.create_project_panel(main_paned)
        
        # Right panel - Document editor
        self.create_editor_panel(main_paned)
    
    def create_project_panel(self, parent):
        """Create the project list panel"""
        # Project panel frame
        project_frame = ttk.Frame(parent)
        parent.add(project_frame, weight=1)
        
        # Project list header
        header_frame = ttk.Frame(project_frame)
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(header_frame, text="Projects", font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
        
        # New project button
        ttk.Button(header_frame, text="New", command=self.new_project, width=8).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Project list with scrollbar
        list_frame = ttk.Frame(project_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview for project list
        columns = ('Client', 'Type', 'Status', 'Modified')
        self.project_tree = ttk.Treeview(list_frame, columns=columns, show='tree headings', height=15)
        
        # Configure columns
        self.project_tree.heading('#0', text='Project Name')
        self.project_tree.column('#0', width=150, minwidth=100)
        
        for col in columns:
            self.project_tree.heading(col, text=col)
            self.project_tree.column(col, width=80, minwidth=60)
        
        # Scrollbars for treeview
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.project_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.project_tree.xview)
        self.project_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.project_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Bind selection event
        self.project_tree.bind('<<TreeviewSelect>>', self.on_project_select)
        self.project_tree.bind('<Double-1>', self.on_project_double_click)
        
        # Context menu for project list
        self.create_project_context_menu()
        
        # Project details frame
        details_frame = ttk.LabelFrame(project_frame, text="Project Details", padding=10)
        details_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.project_details_text = tk.Text(details_frame, height=6, wrap=tk.WORD, state=tk.DISABLED)
        self.project_details_text.pack(fill=tk.BOTH, expand=True)
    
    def create_editor_panel(self, parent):
        """Create the document editor panel"""
        # Editor panel frame
        editor_frame = ttk.Frame(parent)
        parent.add(editor_frame, weight=3)
        
        # Editor toolbar
        toolbar_frame = ttk.Frame(editor_frame)
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
        ttk.Button(toolbar_frame, text="Save", command=self.save_current).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_frame, text="Refine", command=self.refine_document).pack(side=tk.LEFT, padx=2)
        
        # Version info
        self.version_label = ttk.Label(toolbar_frame, text="No document loaded")
        self.version_label.pack(side=tk.RIGHT)
        
        # Editor notebook for different views
        self.editor_notebook = ttk.Notebook(editor_frame)
        self.editor_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Markdown editor tab
        editor_tab = ttk.Frame(self.editor_notebook)
        self.editor_notebook.add(editor_tab, text="Editor")
        
        # Text editor with scrollbar
        text_frame = ttk.Frame(editor_tab)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.text_editor = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, undo=True, maxundo=50)
        self.text_editor.pack(fill=tk.BOTH, expand=True)
        self.text_editor.bind('<KeyRelease>', self.on_text_modified)
        self.text_editor.bind('<Button-1>', self.on_text_modified)
        self.text_editor.bind('<Control-v>', self.on_text_modified)
        
        # Preview tab (placeholder for future markdown preview)
        preview_tab = ttk.Frame(self.editor_notebook)
        self.editor_notebook.add(preview_tab, text="Preview")
        
        self.preview_text = scrolledtext.ScrolledText(preview_tab, wrap=tk.WORD, state=tk.DISABLED)
        self.preview_text.pack(fill=tk.BOTH, expand=True)
    
    def create_project_context_menu(self):
        """Create context menu for project list"""
        self.project_context_menu = tk.Menu(self.root, tearoff=0)
        self.project_context_menu.add_command(label="Open", command=self.on_project_double_click)
        self.project_context_menu.add_separator()
        self.project_context_menu.add_command(label="Add Asset", command=self.add_asset)
        self.project_context_menu.add_command(label="View Assets", command=self.view_assets)
        self.project_context_menu.add_separator()
        self.project_context_menu.add_command(label="Export", command=self.export_project)
        self.project_context_menu.add_separator()
        self.project_context_menu.add_command(label="Delete", command=self.delete_project)
        
        self.project_tree.bind('<Button-3>', self.show_project_context_menu)
    
    def create_status_bar(self):
        """Create the status bar"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = ttk.Label(self.status_bar, text="Ready")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        self.progress_bar = ttk.Progressbar(self.status_bar, mode='indeterminate')
        self.progress_bar.pack(side=tk.RIGHT, padx=5)
    
    # Event handlers
    def on_project_select(self, event):
        """Handle project selection"""
        selection = self.project_tree.selection()
        if selection:
            item = selection[0]
            project_name = self.project_tree.item(item, 'text')
            self.load_project_details(project_name)
    
    def on_project_double_click(self, event=None):
        """Handle project double-click"""
        selection = self.project_tree.selection()
        if selection:
            item = selection[0]
            project_name = self.project_tree.item(item, 'text')
            self.load_project(project_name)
    
    def on_document_type_change(self, event):
        """Handle document type change"""
        if self.current_project and self.check_unsaved_changes():
            self.load_document()
    
    def on_text_modified(self, event=None):
        """Handle text editor modification"""
        # Use a simple flag to track changes
        if not hasattr(self, '_text_modified_flag'):
            self._text_modified_flag = False
        
        if not self._text_modified_flag:
            self._text_modified_flag = True
            self.unsaved_changes = True
            self.update_window_title()
            
            # Reset flag after a short delay
            self.root.after(100, self._reset_modified_flag)

    def _reset_modified_flag(self):
        """Reset the modified flag"""
        if hasattr(self, '_text_modified_flag'):
            self._text_modified_flag = False
    
    def show_project_context_menu(self, event):
        """Show context menu for project list"""
        item = self.project_tree.identify_row(event.y)
        if item:
            self.project_tree.selection_set(item)
            self.project_context_menu.post(event.x_root, event.y_root)
    
    # Project management methods
    def new_project(self):
        """Create a new project"""
        dialog = ProjectDialog(self.root, "New Project")
        if dialog.result:
            project_data = dialog.result
            if self.app.project_manager.create_project(project_data):
                self.refresh_project_list()
                self.load_project(project_data['project_name'])
                self.set_status("Project created successfully")
            else:
                messagebox.showerror("Error", "Failed to create project")
    
    def load_project(self, project_name: str):
        """Load a project for editing"""
        if self.check_unsaved_changes():
            self.current_project = project_name
            self.load_document()
            self.update_window_title()
            self.set_status(f"Loaded project: {project_name}")
    
    def load_project_details(self, project_name: str):
        """Load project details in the details panel"""
        metadata = self.app.project_manager.get_project_metadata(project_name)
        if metadata:
            details = f"Client: {metadata.get('client_name', 'N/A')}\n"
            details += f"Type: {metadata.get('project_type', 'N/A')}\n"
            details += f"Duration: {metadata.get('expected_duration', 'N/A')}\n"
            details += f"Status: {metadata.get('status', 'N/A')}\n\n"
            details += f"Description:\n{metadata.get('description', 'N/A')}"
            
            self.project_details_text.config(state=tk.NORMAL)
            self.project_details_text.delete(1.0, tk.END)
            self.project_details_text.insert(1.0, details)
            self.project_details_text.config(state=tk.DISABLED)
    
    def load_document(self):
        """Load the current document type for the current project"""
        if not self.current_project:
            return
        
        doc_type = self.doc_type_var.get()
        content = self.app.project_manager.load_document(self.current_project, doc_type)
        
        self.text_editor.delete(1.0, tk.END)
        if content:
            self.text_editor.insert(1.0, content)
            versions = self.app.project_manager.get_document_versions(self.current_project, doc_type)
            if versions:
                self.version_label.config(text=f"Version {versions[0]['version']}")
            else:
                self.version_label.config(text="Version 1")
        else:
            self.version_label.config(text="New document")
        
        self.unsaved_changes = False
        self.current_document_type = doc_type
        self.update_window_title()
    
    def save_current(self):
        """Save the current document"""
        if not self.current_project or not self.current_document_type:
            messagebox.showwarning("Warning", "No project or document loaded")
            return
        
        content = self.text_editor.get(1.0, tk.END + "-1c")
        changelog = f"Saved on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        if self.app.project_manager.save_document(self.current_project, self.current_document_type, content, changelog):
            self.unsaved_changes = False
            self.update_window_title()
            self.set_status("Document saved successfully")
        else:
            messagebox.showerror("Error", "Failed to save document")
    
    def refresh_project_list(self):
        """Refresh the project list"""
        # Clear existing items
        for item in self.project_tree.get_children():
            self.project_tree.delete(item)
        
        # Load projects
        projects = self.app.project_manager.get_project_list()
        for project in projects:
            modified_date = project['modified_date'][:10] if project['modified_date'] else 'N/A'
            self.project_tree.insert('', tk.END, text=project['name'],
                                   values=(project['client_name'], project['project_type'], 
                                          project['status'], modified_date))
    
    def delete_project(self):
        """Delete the selected project"""
        selection = self.project_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        project_name = self.project_tree.item(item, 'text')
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete project '{project_name}'?\n\nThis action cannot be undone."):
            if self.app.project_manager.delete_project(project_name):
                self.refresh_project_list()
                if self.current_project == project_name:
                    self.current_project = None
                    self.text_editor.delete(1.0, tk.END)
                    self.update_window_title()
                self.set_status(f"Project '{project_name}' deleted")
            else:
                messagebox.showerror("Error", "Failed to delete project")
    
    # LLM operations
    def generate_current_document(self):
        """Generate the current document type"""
        if self.doc_type_var.get() == "proposal":
            self.generate_proposal()
        elif self.doc_type_var.get() == "feasibility":
            self.generate_feasibility()
    
    def generate_proposal(self):
        """Generate a proposal using LLM"""
        if not self.current_project:
            messagebox.showwarning("Warning", "No project selected")
            return
        
        self.start_llm_operation("Generating proposal...")
        
        def generate():
            try:
                metadata = self.app.project_manager.get_project_metadata(self.current_project)
                if metadata:
                    proposal = self.app.llm_client.generate_proposal(metadata)
                    self.root.after(0, lambda: self.handle_llm_result(proposal, "proposal"))
                else:
                    self.root.after(0, lambda: self.handle_llm_error("Failed to load project metadata"))
            except Exception as e:
                self.root.after(0, lambda: self.handle_llm_error(str(e)))
        
        threading.Thread(target=generate, daemon=True).start()
    
    def generate_feasibility(self):
        """Generate a feasibility analysis using LLM"""
        if not self.current_project:
            messagebox.showwarning("Warning", "No project selected")
            return
        
        self.start_llm_operation("Generating feasibility analysis...")
        
        def generate():
            try:
                metadata = self.app.project_manager.get_project_metadata(self.current_project)
                if metadata:
                    feasibility = self.app.llm_client.generate_feasibility(metadata)
                    self.root.after(0, lambda: self.handle_llm_result(feasibility, "feasibility"))
                else:
                    self.root.after(0, lambda: self.handle_llm_error("Failed to load project metadata"))
            except Exception as e:
                self.root.after(0, lambda: self.handle_llm_error(str(e)))
        
        threading.Thread(target=generate, daemon=True).start()
    
    def refine_document(self):
        """Refine the current document using LLM"""
        if not self.current_project or not self.current_document_type:
            messagebox.showwarning("Warning", "No document loaded")
            return
        
        # Get refinement request from user
        dialog = RefineDialog(self.root)
        if not dialog.result:
            return
        
        refinement_request = dialog.result
        current_content = self.text_editor.get(1.0, tk.END + "-1c")
        
        self.start_llm_operation("Refining document...")
        
        def refine():
            try:
                refined_content = self.app.llm_client.refine_document(current_content, refinement_request)
                self.root.after(0, lambda: self.handle_llm_result(refined_content, self.current_document_type))
            except Exception as e:
                self.root.after(0, lambda: self.handle_llm_error(str(e)))
        
        threading.Thread(target=refine, daemon=True).start()
    
    def test_llm_connection(self):
        """Test LLM connection"""
        self.start_llm_operation("Testing LLM connection...")
        
        def test():
            try:
                success = self.app.llm_client.test_connection()
                self.root.after(0, lambda: self.handle_connection_test(success))
            except Exception as e:
                self.root.after(0, lambda: self.handle_llm_error(str(e)))
        
        threading.Thread(target=test, daemon=True).start()
    
    def start_llm_operation(self, message: str):
        """Start an LLM operation with progress indication"""
        self.set_status(message)
        self.progress_bar.start()
        self.root.config(cursor="wait")
    
    def handle_llm_result(self, content: str, doc_type: str):
        """Handle successful LLM result"""
        self.progress_bar.stop()
        self.root.config(cursor="")
        
        if doc_type == self.doc_type_var.get():
            self.text_editor.delete(1.0, tk.END)
            self.text_editor.insert(1.0, content)
            self.unsaved_changes = True
            self.update_window_title()
        
        self.set_status("Generation completed successfully")
    
    def handle_llm_error(self, error_message: str):
        """Handle LLM operation error"""
        self.progress_bar.stop()
        self.root.config(cursor="")
        self.set_status("Operation failed")
        messagebox.showerror("LLM Error", f"LLM operation failed:\n\n{error_message}")
    
    def handle_connection_test(self, success: bool):
        """Handle connection test result"""
        self.progress_bar.stop()
        self.root.config(cursor="")
        
        if success:
            self.set_status("LLM connection successful")
            messagebox.showinfo("Connection Test", "LLM connection successful!")
        else:
            self.set_status("LLM connection failed")
            messagebox.showerror("Connection Test", "LLM connection failed. Please check your settings.")
    
    # Utility methods
    def check_unsaved_changes(self) -> bool:
        """Check for unsaved changes and prompt user"""
        if self.unsaved_changes:
            result = messagebox.askyesnocancel("Unsaved Changes", 
                                               "You have unsaved changes. Do you want to save them?")
            if result is True:  # Save
                self.save_current()
                return True
            elif result is False:  # Don't save
                return True
            else:  # Cancel
                return False
        return True
    
    def update_window_title(self):
        """Update the window title"""
        title = "LLM Proposal Generator"
        if self.current_project:
            title += f" - {self.current_project}"
            if self.current_document_type:
                title += f" ({self.current_document_type})"
            if self.unsaved_changes:
                title += " *"
        self.root.title(title)
    
    def set_status(self, message: str):
        """Set status bar message"""
        self.status_label.config(text=message)
    
    def save_current_work(self):
        """Save current work before closing"""
        if self.unsaved_changes and self.current_project:
            self.save_current()
    
    # Export functionality
    def export_document(self, format_type: str):
        """Export current document to specified format"""
        if not self.current_project or not self.current_document_type:
            messagebox.showwarning("Warning", "No document loaded to export")
            return
        
        # Get file extension based on format
        extensions = {
            'pdf': '.pdf',
            'docx': '.docx', 
            'html': '.html',
            'markdown': '.md'
        }
        
        extension = extensions.get(format_type, '.txt')
        
        # Get save location
        default_filename = f"{self.current_project}_{self.current_document_type}{extension}"
        file_path = filedialog.asksaveasfilename(
            title=f"Export as {format_type.upper()}",
            defaultextension=extension,
            filetypes=[
                (f"{format_type.upper()} files", f"*{extension}"),
                ("All files", "*.*")
            ],
            initialfile=default_filename
        )
        
        if not file_path:
            return
        
        # Start export operation
        self.start_export_operation(f"Exporting to {format_type.upper()}...")
        
        def export():
            try:
                content = self.text_editor.get(1.0, tk.END + "-1c")
                project_metadata = self.app.project_manager.get_project_metadata(self.current_project)
                
                # Add version info to project data
                versions = self.app.project_manager.get_document_versions(self.current_project, self.current_document_type)
                if versions:
                    project_metadata['version'] = f"v{versions[0]['version']}"
                
                success = self.app.document_exporter.export_document(
                    content, project_metadata, format_type, file_path
                )
                
                self.root.after(0, lambda: self.handle_export_result(success, file_path, format_type))
                
            except Exception as e:
                self.root.after(0, lambda: self.handle_export_error(str(e)))
        
        threading.Thread(target=export, daemon=True).start()
    
    def start_export_operation(self, message: str):
        """Start an export operation with progress indication"""
        self.set_status(message)
        self.progress_bar.start()
        self.root.config(cursor="wait")
    
    def handle_export_result(self, success: bool, file_path: str, format_type: str):
        """Handle export operation result"""
        self.progress_bar.stop()
        self.root.config(cursor="")
        
        if success:
            self.set_status(f"Document exported successfully to {format_type.upper()}")
            
            # Ask if user wants to open the file
            if messagebox.askyesno("Export Complete", 
                                   f"Document exported successfully!\n\nDo you want to open the exported file?"):
                try:
                    if sys.platform == "win32":
                        os.startfile(file_path)
                    elif sys.platform == "darwin":  # macOS
                        subprocess.run(["open", file_path])
                    else:  # Linux
                        subprocess.run(["xdg-open", file_path])
                except Exception as e:
                    messagebox.showwarning("Open File", f"Could not open file automatically: {e}")
        else:
            self.set_status("Export failed")
            messagebox.showerror("Export Error", f"Failed to export document to {format_type.upper()}")
    
    def handle_export_error(self, error_message: str):
        """Handle export operation error"""
        self.progress_bar.stop()
        self.root.config(cursor="")
        self.set_status("Export failed")
        messagebox.showerror("Export Error", f"Export failed:\n\n{error_message}")
    
    def show_company_settings(self):
        """Show company settings dialog"""
        dialog = CompanySettingsDialog(self.root, self.app.config.get('company', {}))
        if dialog.result:
            self.app.config['company'] = dialog.result
            self.app.save_config()
            
            # Update LLM client with new company config
            self.app.llm_client = LLMClient(self.app.config.get('llm', {}), dialog.result)
            
            # Update document exporter
            from document_exporter import DocumentExporter
            self.app.document_exporter = DocumentExporter(dialog.result)
            
            messagebox.showinfo("Settings", "Company settings updated successfully!")
    
    def show_app_settings(self):
        """Show application settings dialog"""
        dialog = AppSettingsDialog(self.root, self.app.config.get('app', {}))
        if dialog.result:
            self.app.config['app'] = dialog.result
            self.app.save_config()
            messagebox.showinfo("Settings", "Application settings updated successfully!")
    
    # Placeholder methods for menu items
    def save_as(self):
        """Save document with a new name/location"""
        if not self.current_project or not self.current_document_type:
            messagebox.showwarning("Warning", "No document loaded")
            return
        
        # Get save location
        file_path = filedialog.asksaveasfilename(
            title="Save Document As",
            defaultextension=".md",
            filetypes=[
                ("Markdown files", "*.md"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ],
            initialfile=f"{self.current_project}_{self.current_document_type}.md"
        )
        
        if file_path:
            try:
                content = self.text_editor.get(1.0, tk.END + "-1c")
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Success", f"Document saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save document: {e}")
    
    def export_pdf(self):
        self.export_document('pdf')
    
    def undo(self):
        try:
            self.text_editor.edit_undo()
        except tk.TclError:
            pass
    
    def redo(self):
        try:
            self.text_editor.edit_redo()
        except tk.TclError:
            pass
    
    def find_text(self):
        messagebox.showinfo("Info", "Find feature coming soon!")
    
    def replace_text(self):
        messagebox.showinfo("Info", "Replace feature coming soon!")
    
    def show_llm_settings(self):
        dialog = LLMSettingsDialog(self.root, self.app.config.get('llm', {}))
        if dialog.result:
            self.app.config['llm'] = dialog.result
            self.app.save_config()
            self.app.llm_client = self.app.llm_client.__class__(dialog.result)
            messagebox.showinfo("Settings", "LLM settings updated successfully!")
    
    def add_asset(self):
        messagebox.showinfo("Info", "Add asset feature coming soon!")
    
    def view_assets(self):
        messagebox.showinfo("Info", "View assets feature coming soon!")
    
    def export_project(self):
        messagebox.showinfo("Info", "Export project feature coming soon!")
    
    def show_about(self):
        messagebox.showinfo("About", "LLM Proposal Generator v1.0\n\nA desktop application for generating professional project proposals using Large Language Models.")


# Dialog classes
class ProjectDialog:
    """Dialog for creating new projects"""
    
    def __init__(self, parent, title):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x600")
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
        ttk.Entry(main_frame, textvariable=self.project_name_var, width=40).grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Client name
        ttk.Label(main_frame, text="Client Name:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.client_name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.client_name_var, width=40).grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Project type
        ttk.Label(main_frame, text="Project Type:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.project_type_var = tk.StringVar(value="Software")
        type_combo = ttk.Combobox(main_frame, textvariable=self.project_type_var, 
                                  values=["Software", "Hardware", "Hybrid"], width=37)
        type_combo.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Expected duration
        ttk.Label(main_frame, text="Expected Duration:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.duration_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.duration_var, width=40).grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Requirements
        ttk.Label(main_frame, text="Requirements:").grid(row=4, column=0, sticky=tk.NW, pady=5)
        self.requirements_text = scrolledtext.ScrolledText(main_frame, width=50, height=10)
        self.requirements_text.grid(row=4, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Hardware components
        ttk.Label(main_frame, text="Hardware Components:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.hardware_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.hardware_var, width=40).grid(row=5, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        ttk.Label(main_frame, text="(comma-separated)", font=('Arial', 8)).grid(row=6, column=1, sticky=tk.W, padx=(10, 0))
        
        # Software modules
        ttk.Label(main_frame, text="Software Modules:").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.software_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.software_var, width=40).grid(row=7, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        ttk.Label(main_frame, text="(comma-separated)", font=('Arial', 8)).grid(row=8, column=1, sticky=tk.W, padx=(10, 0))

        # Document Author
        ttk.Label(main_frame, text="Document Author:").grid(row=9, column=0, sticky=tk.W, pady=5)
        self.author_var = tk.StringVar()
        author_combo = ttk.Combobox(main_frame, textvariable=self.author_var, width=37)
        author_combo.grid(row=9, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        author_combo['values'] = ["Project Manager", "Technical Lead", "Senior Architect", "Business Analyst"]
        author_combo.set("Project Manager")
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=10, column=0, columnspan=2, pady=20)  # Update row number

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
            'author': self.author_var.get() if self.author_var.get() != 'Default' else '',
        }
        
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel dialog"""
        self.dialog.destroy()


class RefineDialog:
    """Dialog for refining documents"""
    
    def __init__(self, parent):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Refine Document")
        self.dialog.geometry("500x300")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        self.dialog.wait_window()
    
    def create_widgets(self):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Please describe what you want to refine in the document:", 
                  font=('Arial', 10)).pack(anchor=tk.W, pady=(0, 10))
        
        self.refinement_text = scrolledtext.ScrolledText(main_frame, width=60, height=10)
        self.refinement_text.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Example prompts
        example_frame = ttk.LabelFrame(main_frame, text="Example prompts:", padding=10)
        example_frame.pack(fill=tk.X, pady=(0, 20))
        
        examples = [
            "Make the technical details more comprehensive",
            "Add more specific timeline milestones",
            "Improve the risk assessment section",
            "Make the language more formal/professional",
            "Add cost breakdown details"
        ]
        
        for example in examples:
            ttk.Label(example_frame, text=f"• {example}", 
                      font=('Arial', 9)).pack(anchor=tk.W, pady=1)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Refine", command=self.refine).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.RIGHT)
    
    def refine(self):
        """Process refinement request"""
        request = self.refinement_text.get(1.0, tk.END + "-1c").strip()
        if not request:
            messagebox.showerror("Error", "Please enter a refinement request")
            return
        
        self.result = request
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel dialog"""
        self.dialog.destroy()


class CompanySettingsDialog:
    """Dialog for company settings configuration"""
    
    def __init__(self, parent, current_config):
        self.result = None
        self.current_config = current_config.copy()
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Company Settings")
        self.dialog.geometry("700x800")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        self.load_current_settings()
        self.dialog.wait_window()
    
    def create_widgets(self):
        """Create dialog widgets"""
        # Create scrollable frame
        canvas = tk.Canvas(self.dialog)
        scrollbar = ttk.Scrollbar(self.dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        main_frame = ttk.Frame(scrollable_frame, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Company Information Section
        company_frame = ttk.LabelFrame(main_frame, text="Company Information", padding=15)
        company_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Company Name
        ttk.Label(company_frame, text="Company Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.company_name_var = tk.StringVar()
        ttk.Entry(company_frame, textvariable=self.company_name_var, width=50).grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Tagline
        ttk.Label(company_frame, text="Tagline:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.tagline_var = tk.StringVar()
        ttk.Entry(company_frame, textvariable=self.tagline_var, width=50).grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Industry
        ttk.Label(company_frame, text="Industry:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.industry_var = tk.StringVar()
        ttk.Entry(company_frame, textvariable=self.industry_var, width=50).grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Logo Path
        ttk.Label(company_frame, text="Logo Path:").grid(row=3, column=0, sticky=tk.W, pady=5)
        logo_frame = ttk.Frame(company_frame)
        logo_frame.grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        self.logo_path_var = tk.StringVar()
        ttk.Entry(logo_frame, textvariable=self.logo_path_var, width=40).pack(side=tk.LEFT)
        ttk.Button(logo_frame, text="Browse", command=self.browse_logo, width=8).pack(side=tk.LEFT, padx=(5, 0))
        
        # Contact Information Section
        contact_frame = ttk.LabelFrame(main_frame, text="Contact Information", padding=15)
        contact_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Website
        ttk.Label(contact_frame, text="Website:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.website_var = tk.StringVar()
        ttk.Entry(contact_frame, textvariable=self.website_var, width=50).grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Email
        ttk.Label(contact_frame, text="Email:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.email_var = tk.StringVar()
        ttk.Entry(contact_frame, textvariable=self.email_var, width=50).grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Phone
        ttk.Label(contact_frame, text="Phone:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.phone_var = tk.StringVar()
        ttk.Entry(contact_frame, textvariable=self.phone_var, width=50).grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Address
        ttk.Label(contact_frame, text="Address:").grid(row=3, column=0, sticky=tk.NW, pady=5)
        self.address_text = scrolledtext.ScrolledText(contact_frame, width=50, height=4)
        self.address_text.grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Specializations Section
        spec_frame = ttk.LabelFrame(main_frame, text="Specializations", padding=15)
        spec_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(spec_frame, text="Specializations:").grid(row=0, column=0, sticky=tk.NW, pady=5)
        self.specializations_text = scrolledtext.ScrolledText(spec_frame, width=50, height=6)
        self.specializations_text.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        ttk.Label(spec_frame, text="(one per line)", font=('Arial', 8)).grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        
        # Legal Information Section
        legal_frame = ttk.LabelFrame(main_frame, text="Legal Information", padding=15)
        legal_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Registration Number
        ttk.Label(legal_frame, text="Registration Number:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.reg_number_var = tk.StringVar()
        ttk.Entry(legal_frame, textvariable=self.reg_number_var, width=50).grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Tax ID
        ttk.Label(legal_frame, text="Tax ID:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.tax_id_var = tk.StringVar()
        ttk.Entry(legal_frame, textvariable=self.tax_id_var, width=50).grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)

        # Document Authors Section
        authors_frame = ttk.LabelFrame(main_frame, text="Document Authors", padding=15)
        authors_frame.pack(fill=tk.X, pady=(0, 15))

        # Default Author
        ttk.Label(authors_frame, text="Default Author:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.default_author_var = tk.StringVar()
        ttk.Entry(authors_frame, textvariable=self.default_author_var, width=50).grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)

        # Available Authors
        ttk.Label(authors_frame, text="Available Authors:").grid(row=1, column=0, sticky=tk.NW, pady=5)
        self.authors_text = scrolledtext.ScrolledText(authors_frame, width=50, height=4)
        self.authors_text.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        ttk.Label(authors_frame, text="(one per line, e.g., 'John Smith - Senior Project Manager')", 
                font=('Arial', 8)).grid(row=2, column=1, sticky=tk.W, padx=(10, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(button_frame, text="Save", command=self.save_settings).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.RIGHT)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def browse_logo(self):
        """Browse for logo file"""
        file_path = filedialog.askopenfilename(
            title="Select Company Logo",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.logo_path_var.set(file_path)
    
    def load_current_settings(self):
        """Load current settings into the dialog"""
        if self.current_config:
            self.company_name_var.set(self.current_config.get('name', ''))
            self.tagline_var.set(self.current_config.get('tagline', ''))
            self.industry_var.set(self.current_config.get('industry', ''))
            self.logo_path_var.set(self.current_config.get('logo_path', ''))
            self.website_var.set(self.current_config.get('website', ''))
            self.email_var.set(self.current_config.get('email', ''))
            self.phone_var.set(self.current_config.get('phone', ''))
            
            # Address
            address = self.current_config.get('address', '')
            if address:
                self.address_text.insert(1.0, address)
            
            # Specializations
            specializations = self.current_config.get('specializations', [])
            if specializations:
                self.specializations_text.insert(1.0, '\n'.join(specializations))
            
            self.reg_number_var.set(self.current_config.get('registration_number', ''))
            self.tax_id_var.set(self.current_config.get('tax_id', ''))
            self.default_author_var.set(self.current_config.get('default_author', ''))

            # Authors
            authors = self.current_config.get('authors', [])
            if authors:
                self.authors_text.insert(1.0, '\n'.join(authors))
    
    def save_settings(self):
        """Save the settings"""
        if not self.company_name_var.get().strip():
            messagebox.showerror("Error", "Company name is required")
            return
        
        # Parse specializations
        spec_text = self.specializations_text.get(1.0, tk.END + "-1c").strip()
        specializations = [line.strip() for line in spec_text.split('\n') if line.strip()]

        # Parse authors
        authors_text = self.authors_text.get(1.0, tk.END + "-1c").strip()
        authors = [line.strip() for line in authors_text.split('\n') if line.strip()]
        
        self.result = {
            'name': self.company_name_var.get().strip(),
            'tagline': self.tagline_var.get().strip(),
            'industry': self.industry_var.get().strip(),
            'logo_path': self.logo_path_var.get().strip(),
            'website': self.website_var.get().strip(),
            'email': self.email_var.get().strip(),
            'phone': self.phone_var.get().strip(),
            'address': self.address_text.get(1.0, tk.END + "-1c").strip(),
            'specializations': specializations,
            'registration_number': self.reg_number_var.get().strip(),
            'tax_id': self.tax_id_var.get().strip(),
            'default_author': self.default_author_var.get().strip(),
            'authors': authors,
        }
        
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel dialog"""
        self.dialog.destroy()


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
        autosave_frame = ttk.LabelFrame(main_frame, text="Auto-save Settings", padding=15)
        autosave_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.auto_save_var = tk.BooleanVar()
        ttk.Checkbutton(autosave_frame, text="Enable auto-save", 
                        variable=self.auto_save_var).pack(anchor=tk.W)
        
        interval_frame = ttk.Frame(autosave_frame)
        interval_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(interval_frame, text="Auto-save interval (seconds):").pack(side=tk.LEFT)
        self.interval_var = tk.StringVar(value="30")
        ttk.Entry(interval_frame, textvariable=self.interval_var, width=10).pack(side=tk.LEFT, padx=(10, 0))
        
        # Export settings
        export_frame = ttk.LabelFrame(main_frame, text="Export Settings", padding=15)
        export_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(export_frame, text="Default export format:").pack(anchor=tk.W)
        self.export_format_var = tk.StringVar(value="pdf")
        format_frame = ttk.Frame(export_frame)
        format_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Radiobutton(format_frame, text="PDF", variable=self.export_format_var, value="pdf").pack(side=tk.LEFT)
        ttk.Radiobutton(format_frame, text="DOCX", variable=self.export_format_var, value="docx").pack(side=tk.LEFT, padx=(10, 0))
        ttk.Radiobutton(format_frame, text="HTML", variable=self.export_format_var, value="html").pack(side=tk.LEFT, padx=(10, 0))
        ttk.Radiobutton(format_frame, text="Markdown", variable=self.export_format_var, value="markdown").pack(side=tk.LEFT, padx=(10, 0))
        
        # Backup settings
        backup_frame = ttk.LabelFrame(main_frame, text="Backup Settings", padding=15)
        backup_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.backup_enabled_var = tk.BooleanVar()
        ttk.Checkbutton(backup_frame, text="Enable automatic backups", 
                        variable=self.backup_enabled_var).pack(anchor=tk.W)
        
        versions_frame = ttk.Frame(backup_frame)
        versions_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(versions_frame, text="Maximum versions to keep:").pack(side=tk.LEFT)
        self.max_versions_var = tk.StringVar(value="10")
        ttk.Entry(versions_frame, textvariable=self.max_versions_var, width=10).pack(side=tk.LEFT, padx=(10, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(button_frame, text="Save", command=self.save_settings).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.RIGHT)
    
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
    """Dialog for LLM settings configuration"""
    
    def __init__(self, parent, current_config):
        self.result = None
        self.current_config = current_config.copy()
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("LLM Settings")
        self.dialog.geometry("600x500")
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
        
        # Provider selection
        provider_frame = ttk.LabelFrame(main_frame, text="LLM Provider", padding=10)
        provider_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.provider_var = tk.StringVar(value="openai")
        
        ttk.Radiobutton(provider_frame, text="OpenAI", variable=self.provider_var, 
                        value="openai", command=self.on_provider_change).pack(anchor=tk.W)
        ttk.Radiobutton(provider_frame, text="Anthropic (Claude)", variable=self.provider_var, 
                        value="anthropic", command=self.on_provider_change).pack(anchor=tk.W)
        ttk.Radiobutton(provider_frame, text="Local LLM", variable=self.provider_var, 
                        value="local", command=self.on_provider_change).pack(anchor=tk.W)
        
        # Configuration frame
        config_frame = ttk.LabelFrame(main_frame, text="Configuration", padding=10)
        config_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # API Key
        ttk.Label(config_frame, text="API Key:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.api_key_var = tk.StringVar()
        api_key_entry = ttk.Entry(config_frame, textvariable=self.api_key_var, width=50, show="*")
        api_key_entry.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Model
        ttk.Label(config_frame, text="Model:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.model_var = tk.StringVar()
        self.model_combo = ttk.Combobox(config_frame, textvariable=self.model_var, width=47)
        self.model_combo.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Endpoint
        ttk.Label(config_frame, text="Endpoint:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.endpoint_var = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.endpoint_var, width=50).grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Advanced settings
        advanced_frame = ttk.LabelFrame(config_frame, text="Advanced Settings", padding=10)
        advanced_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W+tk.E, pady=15)
        
        # Max tokens
        ttk.Label(advanced_frame, text="Max Tokens:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.max_tokens_var = tk.StringVar(value="4000")
        ttk.Entry(advanced_frame, textvariable=self.max_tokens_var, width=20).grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Temperature
        ttk.Label(advanced_frame, text="Temperature:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.temperature_var = tk.StringVar(value="0.7")
        ttk.Entry(advanced_frame, textvariable=self.temperature_var, width=20).grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Test Connection", command=self.test_connection).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Save", command=self.save_settings).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.RIGHT)
    
    def on_provider_change(self):
        """Handle provider selection change"""
        provider = self.provider_var.get()
        
        # Update model options
        if provider == "openai":
            models = ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]
            default_endpoint = "https://api.openai.com/v1/chat/completions"
        elif provider == "anthropic":
            models = ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"]
            default_endpoint = "https://api.anthropic.com/v1/messages"
        else:  # local
            models = ["llama-2-7b", "llama-2-13b", "custom"]
            default_endpoint = "http://localhost:8080/completion"
        
        self.model_combo['values'] = models
        if not self.model_var.get() or self.model_var.get() not in models:
            self.model_var.set(models[0])
        
        if not self.endpoint_var.get():
            self.endpoint_var.set(default_endpoint)
    
    def load_current_settings(self):
        """Load current settings into the dialog"""
        if self.current_config:
            self.provider_var.set(self.current_config.get('provider', 'openai'))
            self.api_key_var.set(self.current_config.get('api_key', ''))
            self.model_var.set(self.current_config.get('model', ''))
            self.endpoint_var.set(self.current_config.get('endpoint', ''))
            self.max_tokens_var.set(str(self.current_config.get('max_tokens', 4000)))
            self.temperature_var.set(str(self.current_config.get('temperature', 0.7)))
        
        self.on_provider_change()
    
    def test_connection(self):
        """Test the connection with current settings"""
        config = self.get_config_from_dialog()
        
        # Import here to avoid circular imports
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from llm_client import LLMClient
        
        try:
            client = LLMClient(config)
            if client.test_connection():
                messagebox.showinfo("Success", "Connection successful!")
            else:
                messagebox.showerror("Error", "Connection failed. Please check your settings.")
        except Exception as e:
            messagebox.showerror("Error", f"Connection test failed:\n{str(e)}")
    
    def get_config_from_dialog(self):
        """Get configuration from dialog fields"""
        try:
            max_tokens = int(self.max_tokens_var.get())
            temperature = float(self.temperature_var.get())
        except ValueError:
            max_tokens = 4000
            temperature = 0.7
        
        return {
            'provider': self.provider_var.get(),
            'api_key': self.api_key_var.get(),
            'model': self.model_var.get(),
            'endpoint': self.endpoint_var.get(),
            'max_tokens': max_tokens,
            'temperature': temperature
        }
    
    def save_settings(self):
        """Save the settings"""
        if not self.api_key_var.get().strip() and self.provider_var.get() != 'local':
            messagebox.showerror("Error", "API key is required")
            return
        
        if not self.model_var.get().strip():
            messagebox.showerror("Error", "Model is required")
            return
        
        self.result = self.get_config_from_dialog()
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel dialog"""
        self.dialog.destroy()


class LLMSettingsDialog:
    """Dialog for LLM settings configuration"""
    
    def __init__(self, parent, current_config):
        self.result = None
        self.current_config = current_config.copy()
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("LLM Settings")
        self.dialog.geometry("600x500")
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
        
        # Provider selection
        provider_frame = ttk.LabelFrame(main_frame, text="LLM Provider", padding=10)
        provider_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.provider_var = tk.StringVar(value="openai")
        
        ttk.Radiobutton(provider_frame, text="OpenAI", variable=self.provider_var, 
                        value="openai", command=self.on_provider_change).pack(anchor=tk.W)
        ttk.Radiobutton(provider_frame, text="Anthropic (Claude)", variable=self.provider_var, 
                        value="anthropic", command=self.on_provider_change).pack(anchor=tk.W)
        ttk.Radiobutton(provider_frame, text="Local LLM", variable=self.provider_var, 
                        value="local", command=self.on_provider_change).pack(anchor=tk.W)
        
        # Configuration frame
        config_frame = ttk.LabelFrame(main_frame, text="Configuration", padding=10)
        config_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # API Key
        ttk.Label(config_frame, text="API Key:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.api_key_var = tk.StringVar()
        api_key_entry = ttk.Entry(config_frame, textvariable=self.api_key_var, width=50, show="*")
        api_key_entry.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Model
        ttk.Label(config_frame, text="Model:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.model_var = tk.StringVar()
        self.model_combo = ttk.Combobox(config_frame, textvariable=self.model_var, width=47)
        self.model_combo.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Endpoint
        ttk.Label(config_frame, text="Endpoint:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.endpoint_var = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.endpoint_var, width=50).grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Advanced settings
        advanced_frame = ttk.LabelFrame(config_frame, text="Advanced Settings", padding=10)
        advanced_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W+tk.E, pady=15)
        
        # Max tokens
        ttk.Label(advanced_frame, text="Max Tokens:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.max_tokens_var = tk.StringVar(value="4000")
        ttk.Entry(advanced_frame, textvariable=self.max_tokens_var, width=20).grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Temperature
        ttk.Label(advanced_frame, text="Temperature:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.temperature_var = tk.StringVar(value="0.7")
        ttk.Entry(advanced_frame, textvariable=self.temperature_var, width=20).grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Test Connection", command=self.test_connection).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Save", command=self.save_settings).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.RIGHT)
    
    def on_provider_change(self):
        """Handle provider selection change"""
        provider = self.provider_var.get()
        
        # Update model options
        if provider == "openai":
            models = ["gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]
            default_endpoint = "https://api.openai.com/v1/chat/completions"
        elif provider == "anthropic":
            models = ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"]
            default_endpoint = "https://api.anthropic.com/v1/messages"
        else:  # local
            models = ["llama-2-7b", "llama-2-13b", "custom"]
            default_endpoint = "http://localhost:8080/completion"
        
        self.model_combo['values'] = models
        if not self.model_var.get() or self.model_var.get() not in models:
            self.model_var.set(models[0])
        
        if not self.endpoint_var.get():
            self.endpoint_var.set(default_endpoint)
    
    def load_current_settings(self):
        """Load current settings into the dialog"""
        if self.current_config:
            self.provider_var.set(self.current_config.get('provider', 'openai'))
            self.api_key_var.set(self.current_config.get('api_key', ''))
            self.model_var.set(self.current_config.get('model', ''))
            self.endpoint_var.set(self.current_config.get('endpoint', ''))
            self.max_tokens_var.set(str(self.current_config.get('max_tokens', 4000)))
            self.temperature_var.set(str(self.current_config.get('temperature', 0.7)))
        
        self.on_provider_change()
    
    def test_connection(self):
        """Test the connection with current settings"""
        config = self.get_config_from_dialog()
        
        # Import here to avoid circular imports
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from llm_client import LLMClient
        
        try:
            client = LLMClient(config)
            if client.test_connection():
                messagebox.showinfo("Success", "Connection successful!")
            else:
                messagebox.showerror("Error", "Connection failed. Please check your settings.")
        except Exception as e:
            messagebox.showerror("Error", f"Connection test failed:\n{str(e)}")
    
    def get_config_from_dialog(self):
        """Get configuration from dialog fields"""
        try:
            max_tokens = int(self.max_tokens_var.get())
            temperature = float(self.temperature_var.get())
        except ValueError:
            max_tokens = 4000
            temperature = 0.7
        
        return {
            'provider': self.provider_var.get(),
            'api_key': self.api_key_var.get(),
            'model': self.model_var.get(),
            'endpoint': self.endpoint_var.get(),
            'max_tokens': max_tokens,
            'temperature': temperature
        }
    
    def save_settings(self):
        """Save the settings"""
        if not self.api_key_var.get().strip() and self.provider_var.get() != 'local':
            messagebox.showerror("Error", "API key is required")
            return
        
        if not self.model_var.get().strip():
            messagebox.showerror("Error", "Model is required")
            return
        
        self.result = self.get_config_from_dialog()
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel dialog"""
        self.dialog.destroy()