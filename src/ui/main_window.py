"""
Main Window UI for the LLM Proposal Generator
Simplified and modular version
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Any, Optional
import threading
import sys
import os
import subprocess
from pathlib import Path
from datetime import datetime

# Import modular components
from .dialogs import (
    ProjectDialog, RefineDialog, CompanySettingsDialog, 
    LLMSettingsDialog, AppSettingsDialog
)
from .panels import ProjectPanel, EditorPanel
from .utils import StatusManager, run_in_thread


class MainWindow:
    """Main application window - simplified and modular"""
    
    def __init__(self, root: tk.Tk, app):
        self.root = root
        self.app = app
        self.current_project = None
        self.current_document_type = None
        self.unsaved_changes = False
        
        self.setup_ui()
        self.project_panel.refresh_project_list()
    
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
        self._create_file_menu(menubar)
        
        # Edit menu
        self._create_edit_menu(menubar)
        
        # LLM menu
        self._create_llm_menu(menubar)
        
        # Settings menu
        self._create_settings_menu(menubar)
        
        # Help menu
        self._create_help_menu(menubar)
        
        # Bind keyboard shortcuts
        self._bind_shortcuts()
    
    def _create_file_menu(self, menubar):
        """Create the File menu"""
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
    
    def _create_edit_menu(self, menubar):
        """Create the Edit menu"""
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Find", command=self.find_text, accelerator="Ctrl+F")
        edit_menu.add_command(label="Replace", command=self.replace_text, accelerator="Ctrl+H")
    
    def _create_llm_menu(self, menubar):
        """Create the LLM menu"""
        llm_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="LLM", menu=llm_menu)
        
        llm_menu.add_command(label="Generate Proposal", command=self.generate_proposal)
        llm_menu.add_command(label="Generate Feasibility", command=self.generate_feasibility)
        llm_menu.add_command(label="Refine Document", command=self.refine_document)
        llm_menu.add_separator()
        llm_menu.add_command(label="Test Connection", command=self.test_llm_connection)
    
    def _create_settings_menu(self, menubar):
        """Create the Settings menu"""
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        
        settings_menu.add_command(label="LLM Settings", command=self.show_llm_settings)
        settings_menu.add_command(label="Company Settings", command=self.show_company_settings)
        settings_menu.add_separator()
        settings_menu.add_command(label="Application Settings", command=self.show_app_settings)
    
    def _create_help_menu(self, menubar):
        """Create the Help menu"""
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def _bind_shortcuts(self):
        """Bind keyboard shortcuts"""
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
        
        # Create panels
        self.project_panel = ProjectPanel(main_paned, self)
        self.editor_panel = EditorPanel(main_paned, self)
    
    def create_status_bar(self):
        """Create the status bar"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = ttk.Label(self.status_bar, text="Ready")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        self.progress_bar = ttk.Progressbar(self.status_bar, mode='indeterminate')
        self.progress_bar.pack(side=tk.RIGHT, padx=5)
        
        # Create status manager
        self.status_manager = StatusManager(self.status_label, self.progress_bar, self.root)
    
    # Project management methods
    def new_project(self):
        """Create a new project"""
        dialog = ProjectDialog(self.root, "New Project", self.app)
        if dialog.result:
            project_data = dialog.result
            if self.app.project_manager.create_project(project_data):
                self.project_panel.refresh_project_list()
                self.load_project(project_data['project_name'])
                self.status_manager.set_status("Project created successfully")
            else:
                messagebox.showerror("Error", "Failed to create project")
    
    def load_project(self, project_name: str):
        """Load a project for editing"""
        if self.check_unsaved_changes():
            self.current_project = project_name
            self.load_document()
            self.update_window_title()
            self.status_manager.set_status(f"Loaded project: {project_name}")
    
    def load_document(self):
        """Load the current document type for the current project"""
        if not self.current_project:
            return
        
        doc_type = self.editor_panel.get_current_document_type()
        content = self.app.project_manager.load_document(self.current_project, doc_type)
        
        self.editor_panel.load_document(self.current_project, doc_type, content)
        
        self.unsaved_changes = False
        self.current_document_type = doc_type
        self.update_window_title()
    
    def save_current(self):
        """Save the current document"""
        if not self.current_project or not self.current_document_type:
            messagebox.showwarning("Warning", "No project or document loaded")
            return
        
        content = self.editor_panel.get_content()
        changelog = f"Saved on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        if self.app.project_manager.save_document(self.current_project, self.current_document_type, content, changelog):
            self.unsaved_changes = False
            self.update_window_title()
            self.status_manager.set_status("Document saved successfully")
        else:
            messagebox.showerror("Error", "Failed to save document")
    
    # LLM operations
    def generate_proposal(self):
        """Generate a proposal using LLM"""
        if not self.current_project:
            messagebox.showwarning("Warning", "No project selected")
            return
        
        self.status_manager.start_operation("Generating proposal...")
        
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
        
        run_in_thread(generate)
    
    def generate_feasibility(self):
        """Generate a feasibility analysis using LLM"""
        if not self.current_project:
            messagebox.showwarning("Warning", "No project selected")
            return
        
        self.status_manager.start_operation("Generating feasibility analysis...")
        
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
        
        run_in_thread(generate)
    
    def refine_document(self):
        """Refine the current document using LLM"""
        if not self.current_project or not self.current_document_type:
            messagebox.showwarning("Warning", "No document loaded")
            return
        
        dialog = RefineDialog(self.root)
        if not dialog.result:
            return
        
        refinement_request = dialog.result
        current_content = self.editor_panel.get_content()
        
        self.status_manager.start_operation("Refining document...")
        
        def refine():
            try:
                refined_content = self.app.llm_client.refine_document(current_content, refinement_request)
                self.root.after(0, lambda: self.handle_llm_result(refined_content, self.current_document_type))
            except Exception as e:
                self.root.after(0, lambda: self.handle_llm_error(str(e)))
        
        run_in_thread(refine)
    
    def test_llm_connection(self):
        """Test LLM connection"""
        self.status_manager.start_operation("Testing LLM connection...")
        
        def test():
            try:
                success = self.app.llm_client.test_connection()
                self.root.after(0, lambda: self.handle_connection_test(success))
            except Exception as e:
                self.root.after(0, lambda: self.handle_llm_error(str(e)))
        
        run_in_thread(test)
    
    def handle_llm_result(self, content: str, doc_type: str):
        """Handle successful LLM result"""
        self.status_manager.end_operation("Generation completed successfully")
        
        if doc_type == self.editor_panel.get_current_document_type():
            self.editor_panel.set_content(content)
            self.unsaved_changes = True
            self.update_window_title()
    
    def handle_llm_error(self, error_message: str):
        """Handle LLM operation error"""
        self.status_manager.end_operation("Operation failed")
        messagebox.showerror("LLM Error", f"LLM operation failed:\n\n{error_message}")
    
    def handle_connection_test(self, success: bool):
        """Handle connection test result"""
        self.status_manager.end_operation("LLM connection test completed")
        
        if success:
            messagebox.showinfo("Connection Test", "LLM connection successful!")
        else:
            messagebox.showerror("Connection Test", "LLM connection failed. Please check your settings.")
    
    # Export functionality
    def export_document(self, format_type: str):
        """Export current document to specified format"""
        if not self.current_project or not self.current_document_type:
            messagebox.showwarning("Warning", "No document loaded to export")
            return
        
        # Get file extension
        extensions = {'pdf': '.pdf', 'docx': '.docx', 'html': '.html', 'markdown': '.md'}
        extension = extensions.get(format_type, '.txt')
        
        # Get save location
        default_filename = f"{self.current_project}_{self.current_document_type}{extension}"
        file_path = filedialog.asksaveasfilename(
            title=f"Export as {format_type.upper()}",
            defaultextension=extension,
            filetypes=[(f"{format_type.upper()} files", f"*{extension}"), ("All files", "*.*")],
            initialfile=default_filename
        )
        
        if not file_path:
            return
        
        self.status_manager.start_operation(f"Exporting to {format_type.upper()}...")
        
        def export():
            try:
                content = self.editor_panel.get_content()
                project_metadata = self.app.project_manager.get_project_metadata(self.current_project)
                
                # Add version info
                versions = self.app.project_manager.get_document_versions(self.current_project, self.current_document_type)
                if versions:
                    project_metadata['version'] = f"v{versions[0]['version']}"
                
                success = self.app.document_exporter.export_document(
                    content, project_metadata, format_type, file_path
                )
                
                self.root.after(0, lambda: self.handle_export_result(success, file_path, format_type))
                
            except Exception as e:
                self.root.after(0, lambda: self.handle_export_error(str(e)))
        
        run_in_thread(export)
    
    def handle_export_result(self, success: bool, file_path: str, format_type: str):
        """Handle export operation result"""
        self.status_manager.end_operation(f"Export completed" if success else "Export failed")
        
        if success:
            if messagebox.askyesno("Export Complete", 
                                   f"Document exported successfully!\n\nDo you want to open the exported file?"):
                try:
                    if sys.platform == "win32":
                        os.startfile(file_path)
                    elif sys.platform == "darwin":
                        subprocess.run(["open", file_path])
                    else:
                        subprocess.run(["xdg-open", file_path])
                except Exception as e:
                    messagebox.showwarning("Open File", f"Could not open file automatically: {e}")
        else:
            messagebox.showerror("Export Error", f"Failed to export document to {format_type.upper()}")
    
    def handle_export_error(self, error_message: str):
        """Handle export operation error"""
        self.status_manager.end_operation("Export failed")
        messagebox.showerror("Export Error", f"Export failed:\n\n{error_message}")
    
    # Settings dialogs
    def show_llm_settings(self):
        """Show LLM settings dialog"""
        dialog = LLMSettingsDialog(self.root, self.app.config.get('llm', {}))
        if dialog.result:
            self.app.config['llm'] = dialog.result
            self.app.save_config()
            self.app.llm_client = self.app.llm_client.__class__(dialog.result, self.app.config.get('company', {}))
            messagebox.showinfo("Settings", "LLM settings updated successfully!")
    
    def show_company_settings(self):
        """Show company settings dialog"""
        dialog = CompanySettingsDialog(self.root, self.app.config.get('company', {}))
        if dialog.result:
            self.app.config['company'] = dialog.result
            self.app.save_config()
            
            # Update LLM client and document exporter
            from document_exporter import DocumentExporter
            self.app.llm_client = self.app.llm_client.__class__(self.app.config.get('llm', {}), dialog.result)
            self.app.document_exporter = DocumentExporter(dialog.result)
            
            messagebox.showinfo("Settings", "Company settings updated successfully!")
    
    def show_app_settings(self):
        """Show application settings dialog"""
        dialog = AppSettingsDialog(self.root, self.app.config.get('app', {}))
        if dialog.result:
            self.app.config['app'] = dialog.result
            self.app.save_config()
            messagebox.showinfo("Settings", "Application settings updated successfully!")
    
    # Event handlers
    def on_text_modified(self, event=None):
        """Handle text editor modification"""
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
        self.status_manager.set_status(message)
    
    def save_current_work(self):
        """Save current work before closing"""
        if self.unsaved_changes and self.current_project:
            self.save_current()
    
    # Placeholder methods for menu items
    def save_as(self):
        """Save document with a new name/location"""
        if not self.current_project or not self.current_document_type:
            messagebox.showwarning("Warning", "No document loaded")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save Document As",
            defaultextension=".md",
            filetypes=[("Markdown files", "*.md"), ("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"{self.current_project}_{self.current_document_type}.md"
        )
        
        if file_path:
            try:
                content = self.editor_panel.get_content()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Success", f"Document saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save document: {e}")
    
    def undo(self):
        """Undo text edit"""
        try:
            self.editor_panel.text_editor.edit_undo()
        except tk.TclError:
            pass
    
    def redo(self):
        """Redo text edit"""
        try:
            self.editor_panel.text_editor.edit_redo()
        except tk.TclError:
            pass
    
    def find_text(self):
        """Find text (placeholder)"""
        messagebox.showinfo("Info", "Find feature coming soon!")
    
    def replace_text(self):
        """Replace text (placeholder)"""
        messagebox.showinfo("Info", "Replace feature coming soon!")
    
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About", 
                           "LLM Proposal Generator v1.0\n\n"
                           "A desktop application for generating professional project proposals "
                           "using Large Language Models.\n\n"
                           "Features:\n"
                           "• AI-powered document generation\n"
                           "• Multi-format export (PDF, DOCX, HTML, Markdown)\n"
                           "• Company branding and customization\n"
                           "• Project management and version control")