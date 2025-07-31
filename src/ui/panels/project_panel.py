"""
Project Management Panel
"""

import tkinter as tk
from tkinter import ttk, messagebox


class ProjectPanel:
    """Panel for managing projects"""
    
    def __init__(self, parent_frame, main_window):
        self.parent_frame = parent_frame
        self.main_window = main_window
        self.app = main_window.app
        
        self.setup_panel()
        self.create_context_menu()
    
    def setup_panel(self):
        """Setup the project panel"""
        # Project panel frame
        self.project_frame = ttk.Frame(self.parent_frame)
        self.parent_frame.add(self.project_frame, weight=1)
        
        # Project list header
        self._create_header()
        
        # Project list with scrollbar
        self._create_project_list()
        
        # Project details
        self._create_project_details()
    
    def _create_header(self):
        """Create the panel header"""
        header_frame = ttk.Frame(self.project_frame)
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(header_frame, text="Projects", font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
        
        # New project button
        ttk.Button(header_frame, text="New", command=self.main_window.new_project, 
                  width=8).pack(side=tk.RIGHT, padx=(5, 0))
    
    def _create_project_list(self):
        """Create the project list treeview"""
        list_frame = ttk.Frame(self.project_frame)
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
        
        # Bind events
        self.project_tree.bind('<<TreeviewSelect>>', self.on_project_select)
        self.project_tree.bind('<Double-1>', self.on_project_double_click)
        self.project_tree.bind('<Button-3>', self.show_context_menu)
    
    def _create_project_details(self):
        """Create project details section"""
        details_frame = ttk.LabelFrame(self.project_frame, text="Project Details", padding=10)
        details_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.project_details_text = tk.Text(details_frame, height=6, wrap=tk.WORD, state=tk.DISABLED)
        self.project_details_text.pack(fill=tk.BOTH, expand=True)
    
    def create_context_menu(self):
        """Create context menu for project list"""
        self.context_menu = tk.Menu(self.main_window.root, tearoff=0)
        self.context_menu.add_command(label="Open", command=self.on_project_double_click)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Add Asset", command=self.add_asset)
        self.context_menu.add_command(label="View Assets", command=self.view_assets)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Export Project", command=self.export_project)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Delete", command=self.delete_project)
    
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
            self.main_window.load_project(project_name)
    
    def show_context_menu(self, event):
        """Show context menu for project list"""
        item = self.project_tree.identify_row(event.y)
        if item:
            self.project_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
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
    
    def delete_project(self):
        """Delete the selected project"""
        selection = self.project_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        project_name = self.project_tree.item(item, 'text')
        
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to delete project '{project_name}'?\n\nThis action cannot be undone."):
            if self.app.project_manager.delete_project(project_name):
                self.refresh_project_list()
                if self.main_window.current_project == project_name:
                    self.main_window.current_project = None
                    self.main_window.editor_panel.clear_editor()
                    self.main_window.update_window_title()
                self.main_window.set_status(f"Project '{project_name}' deleted")
            else:
                messagebox.showerror("Error", "Failed to delete project")
    
    def add_asset(self):
        """Add asset to project (placeholder)"""
        messagebox.showinfo("Info", "Add asset feature coming soon!")
    
    def view_assets(self):
        """View project assets (placeholder)"""
        messagebox.showinfo("Info", "View assets feature coming soon!")
    
    def export_project(self):
        """Export project (placeholder)"""
        messagebox.showinfo("Info", "Export project feature coming soon!")
    
    def get_selected_project(self):
        """Get the currently selected project name"""
        selection = self.project_tree.selection()
        if selection:
            item = selection[0]
            return self.project_tree.item(item, 'text')
        return None