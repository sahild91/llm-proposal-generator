"""
Document Editor Panel
"""

from datetime import datetime
import tkinter as tk
from tkinter import ttk, scrolledtext
from tkinter import messagebox
import threading


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
        """Create the editor toolbar with dynamic template selection"""
        toolbar_frame = ttk.Frame(self.editor_frame)
        toolbar_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Template selection section
        ttk.Label(toolbar_frame, text="Industry:").pack(side=tk.LEFT)
        
        self.industry_var = tk.StringVar()
        self.industry_combo = ttk.Combobox(toolbar_frame, textvariable=self.industry_var, 
                                        state="readonly", width=15)
        self.industry_combo.pack(side=tk.LEFT, padx=(5, 15))
        self.industry_combo.bind('<<ComboboxSelected>>', self.on_industry_change)
        
        ttk.Label(toolbar_frame, text="Template:").pack(side=tk.LEFT)
        
        self.template_var = tk.StringVar()
        self.template_combo = ttk.Combobox(toolbar_frame, textvariable=self.template_var,
                                        state="readonly", width=25)
        self.template_combo.pack(side=tk.LEFT, padx=(5, 15))
        self.template_combo.bind('<<ComboboxSelected>>', self.on_template_change)
        
        # Editor action buttons
        ttk.Button(toolbar_frame, text="Generate", command=self.generate_current_document).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_frame, text="Save", command=self.main_window.save_current).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_frame, text="Preview", command=self.preview_template).pack(side=tk.LEFT, padx=2)
        
        # Template info section
        info_frame = ttk.Frame(toolbar_frame)
        info_frame.pack(side=tk.RIGHT, padx=5)
        
        self.template_info_label = ttk.Label(info_frame, text="No template selected", font=('Arial', 8))
        self.template_info_label.pack(side=tk.RIGHT)
        
        # Initialize template data
        self.current_template_id = None
        self.load_template_data()

    def load_template_data(self):
        """Load template data including user templates - ENHANCED VERSION"""
        try:
            if hasattr(self.app, 'template_manager') and self.app.template_manager:
                # Reload templates to include any new user templates
                self.app.template_manager.reload_templates()
                
                # Load industries and format them properly
                industries = self.app.template_manager.get_available_industries()
                formatted_industries = [self.format_industry_name(industry) for industry in industries]
                
                # Set industry dropdown with "Select Industry" as default
                self.industry_combo['values'] = ['Select Industry'] + formatted_industries
                self.industry_var.set('Select Industry')
                
                # Create mapping from formatted names to original names
                self.industry_name_map = {'Select Industry': None}
                for original, formatted in zip(industries, formatted_industries):
                    self.industry_name_map[formatted] = original
                
                # Disable template dropdown initially
                self.template_combo['state'] = 'disabled'
                self.template_combo['values'] = ['Select Template']
                self.template_var.set('Select Template')
                
                # Show count including user templates
                total_templates = len(self.app.template_manager.get_all_templates())
                self.template_info_label.config(text=f"{total_templates} templates available (including custom)")
                
            else:
                # Fallback to original hard-coded types if template manager not available
                self.industry_combo['values'] = ['Select Industry', 'Technology', 'Business', 'Services']
                self.industry_var.set('Select Industry')
                self.template_combo['values'] = ['Select Template']
                self.template_combo['state'] = 'disabled'
                self.template_info_label.config(text="Using fallback document types")
                
        except Exception as e:
            print(f"Error loading template data: {e}")
            # Fallback to safe defaults
            self.industry_combo['values'] = ['Select Industry', 'Technology']
            self.industry_var.set('Select Industry')
            self.template_combo['values'] = ['Select Template']
            self.template_combo['state'] = 'disabled'
            self.template_info_label.config(text="Template loading error")

    def format_industry_name(self, industry_name):
        """Format industry name from folder name to display name"""
        # Convert snake_case to Title Case
        formatted = industry_name.replace('_', ' ').title()
        
        # Handle special cases for better presentation
        formatting_map = {
            'Technology': 'Technology',
            'Manufacturing': 'Manufacturing', 
            'Services': 'Professional Services',
            'Business': 'Business & Strategy',
            'Healthcare': 'Healthcare & Medical',
            'Education': 'Education & Training',
            'Retail': 'Retail & E-commerce',
            'Logistics': 'Logistics & Transportation',
            'Finance': 'Financial Services',
            'Legal': 'Legal & Compliance'
        }
        
        return formatting_map.get(formatted, formatted)

    def load_templates_for_industry(self, selected_industry):
        """Load templates for selected industry including user templates - ENHANCED VERSION"""
        try:
            if not hasattr(self.app, 'template_manager') or not self.app.template_manager:
                return
            
            # Load templates for specific industry
            templates = self.app.template_manager.get_templates_by_industry(selected_industry)
            
            # Separate system and user templates
            system_templates = []
            user_templates = []
            
            for template in templates:
                if template.category == 'user_custom':
                    user_templates.append(template)
                else:
                    system_templates.append(template)
            
            # Create template display list
            template_options = ['Select Template']  # Default option at top
            self.template_id_map = {'Select Template': None}  # Map display names to template IDs
            
            # Add system templates first
            if system_templates:
                for template in system_templates:
                    display_name = f"{template.name} ({template.document_type.value.title()})"
                    template_options.append(display_name)
                    self.template_id_map[display_name] = template.template_id
            
            # Add separator and user templates
            if user_templates:
                template_options.append("--- Custom Templates ---")
                self.template_id_map["--- Custom Templates ---"] = None
                
                for template in user_templates:
                    display_name = f"🎨 {template.name} (Custom {template.document_type.value.title()})"
                    template_options.append(display_name)
                    self.template_id_map[display_name] = template.template_id
            
            # Update template combo
            self.template_combo['values'] = template_options
            self.template_var.set('Select Template')  # Set to default
            
            template_count = len(system_templates) + len(user_templates)
            custom_count = len(user_templates)
            
            if template_count > 0:
                info_text = f"{template_count} templates available"
                if custom_count > 0:
                    info_text += f" ({custom_count} custom)"
                self.template_info_label.config(text=info_text)
            else:
                self.template_info_label.config(text=f"No templates in {selected_industry}")
            
            # Clear current selection
            self.current_template_id = None
                
        except Exception as e:
            print(f"Error loading templates for industry {selected_industry}: {e}")
            self.template_combo['values'] = ['Select Template']
            self.template_var.set('Select Template')
            self.template_info_label.config(text="Error loading templates")

    def on_industry_change(self, event=None):
        """Handle industry selection change"""
        selected_formatted = self.industry_var.get()
        
        if selected_formatted == 'Select Industry':
            # Disable template dropdown when no industry selected
            self.template_combo['state'] = 'disabled'
            self.template_combo['values'] = ['Select Template']
            self.template_var.set('Select Template')
            self.current_template_id = None
            self.template_info_label.config(text="Select an industry first")
        else:
            # Enable template dropdown and load templates
            self.template_combo['state'] = 'readonly'
            
            # Get original industry name
            original_industry = self.industry_name_map.get(selected_formatted)
            if original_industry:
                self.load_templates_for_industry(original_industry)
            else:
                self.template_combo['values'] = ['Select Template']
                self.template_var.set('Select Template')
                self.template_info_label.config(text="No templates available")

    def on_template_change(self, event=None):
        """Handle template selection change"""
        selected_display_name = self.template_var.get()
        
        if selected_display_name == 'Select Template' or not selected_display_name:
            # No template selected
            self.current_template_id = None
            industry_name = self.industry_var.get()
            if industry_name != 'Select Industry':
                # Show available count if industry is selected
                template_count = len(self.template_combo['values']) - 1  # Subtract "Select Template"
                self.template_info_label.config(text=f"{template_count} templates available")
            else:
                self.template_info_label.config(text="Select an industry first")
        else:
            # Template selected
            if hasattr(self, 'template_id_map'):
                template_id = self.template_id_map.get(selected_display_name)
                
                if template_id:
                    self.current_template_id = template_id
                    self.update_template_info(template_id)
                    
                    # Notify main window of template change
                    if hasattr(self.main_window, 'on_template_selected'):
                        self.main_window.on_template_selected(template_id)

    def update_template_info(self, template_id):
        """Update the template info display"""
        try:
            if hasattr(self.app, 'get_template_preview'):
                preview = self.app.get_template_preview(template_id)
                if preview:
                    info_text = f"{preview['complexity_level'].title()} • {preview['estimated_time_minutes']}min • {len(preview['sections'])} sections"
                    self.template_info_label.config(text=info_text)
                    return
            
            # Fallback to basic template info
            if hasattr(self.app, 'template_manager') and self.app.template_manager:
                template = self.app.template_manager.get_template(template_id)
                if template:
                    info_text = f"{template.complexity_level.value.title()} • {len(template.sections)} sections"
                    self.template_info_label.config(text=info_text)
                    return
            
            self.template_info_label.config(text="Template selected")
            
        except Exception as e:
            print(f"Error updating template info: {e}")
            self.template_info_label.config(text="Template info unavailable")

    def preview_template(self):
        """Show template preview dialog"""
        # Check if industry is selected
        if self.industry_var.get() == 'Select Industry':
            messagebox.showwarning("No Industry Selected", "Please select an industry first")
            return
        
        # Check if template is selected 
        if not self.current_template_id or self.template_var.get() == 'Select Template':
            messagebox.showwarning("No Template Selected", "Please select a template to preview")
            return
        
        try:
            # Get template preview
            preview = None
            if hasattr(self.app, 'get_template_preview'):
                preview = self.app.get_template_preview(self.current_template_id)
            
            if preview:
                self.show_template_preview_dialog(preview)
            else:
                messagebox.showinfo("Preview", f"Template: {self.current_template_id}\nPreview not available")
                
        except Exception as e:
            messagebox.showerror("Preview Error", f"Could not preview template: {e}")

    def show_template_preview_dialog(self, preview):
        """Show detailed template preview with customization options - Enhanced"""
        dialog = tk.Toplevel(self.main_window.root)
        dialog.title(f"Template Preview: {preview['name']}")
        dialog.geometry("800x700") 
        dialog.resizable(True, True)
        dialog.transient(self.main_window.root)
        dialog.grab_set()
        
        # Store dialog reference for child dialogs
        self._preview_dialog = dialog
        
        # Center dialog on screen  
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"800x700+{x}+{y}")
        # Create main container with proper scrolling
        container = ttk.Frame(dialog)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(container)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Tab 1: Template Overview
        overview_frame = ttk.Frame(notebook)
        notebook.add(overview_frame, text="Overview")
        
        # Template info section
        info_frame = ttk.LabelFrame(overview_frame, text="Template Information", padding=10)
        info_frame.pack(fill=tk.X, pady=(10, 10))
        
        info_text = f"""Name: {preview['name']}
    Industry: {preview['industry'].title()}
    Document Type: {preview['document_type'].title()}
    Complexity: {preview['complexity_level'].title()}
    Estimated Time: {preview['estimated_time_minutes']} minutes
    Total Sections: {len(preview['sections'])}"""
        
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack(anchor=tk.W)
        
        # Quick sections overview
        sections_overview_frame = ttk.LabelFrame(overview_frame, text="Sections Overview", padding=10)
        sections_overview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        overview_text = "Sections in this template:\n"
        for i, section in enumerate(preview['sections'], 1):
            required_mark = "✓" if section['required'] else "○"
            overview_text += f"{i}. {required_mark} {section['title']}\n"
        
        ttk.Label(sections_overview_frame, text=overview_text, justify=tk.LEFT).pack(anchor=tk.W)
        
        # Tab 2: Customize Template
        customize_frame = ttk.Frame(notebook)
        notebook.add(customize_frame, text="Customize")
        
        # Create scrollable area for customization
        canvas = tk.Canvas(customize_frame)
        scrollbar = ttk.Scrollbar(customize_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Custom template name
        name_frame = ttk.LabelFrame(scrollable_frame, text="Custom Template Name", padding=10)
        name_frame.pack(fill=tk.X, pady=(10, 10))
        
        custom_name_var = tk.StringVar(value=f"{preview['name']} (Custom)")
        ttk.Label(name_frame, text="Template Name:").pack(anchor=tk.W)
        ttk.Entry(name_frame, textvariable=custom_name_var, width=50).pack(fill=tk.X, pady=(5, 0))
        
        # Section customization
        sections_custom_frame = ttk.LabelFrame(scrollable_frame, text="Customize Sections", padding=10)
        sections_custom_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Store section customization data
        section_vars = {}
        section_desc_vars = {}
        
        # Instructions
        ttk.Label(sections_custom_frame, 
                text="Customize which sections to include and modify their descriptions:",
                font=('Arial', 9, 'bold')).pack(anchor=tk.W, pady=(0, 10))
        
        # Create customization widgets for each section
        for section in preview['sections']:
            section_frame = ttk.LabelFrame(sections_custom_frame, text=f"Section {section['order']}: {section['title']}", padding=8)
            section_frame.pack(fill=tk.X, pady=(0, 5))
            
            # Include checkbox
            include_var = tk.BooleanVar(value=section['required'])
            section_vars[section['id']] = include_var
            
            checkbox_frame = ttk.Frame(section_frame)
            checkbox_frame.pack(fill=tk.X, pady=(0, 5))
            
            ttk.Checkbutton(checkbox_frame, text="Include this section", 
                        variable=include_var).pack(side=tk.LEFT)
            
            if section['required']:
                ttk.Label(checkbox_frame, text="(Originally Required)", 
                        font=('Arial', 8), foreground='blue').pack(side=tk.LEFT, padx=(10, 0))
            
            # Description customization
            ttk.Label(section_frame, text="Section Description:").pack(anchor=tk.W, pady=(5, 2))
            
            desc_var = tk.StringVar(value=section['description'])
            section_desc_vars[section['id']] = desc_var
            
            desc_entry = tk.Text(section_frame, height=3, wrap=tk.WORD)
            desc_entry.insert(1.0, section['description'])
            desc_entry.pack(fill=tk.X, pady=(0, 5))
            
            # Store text widget reference for later retrieval
            section_desc_vars[section['id']] = desc_entry
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Button frame (outside notebook)
        button_frame = ttk.Frame(container)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        
        # Buttons - FIXED: Pass dialog reference correctly
        ttk.Button(button_frame, text="Use Original Template", 
                command=lambda: self.use_template_from_preview(dialog, preview)).pack(side=tk.LEFT)
        
        ttk.Button(button_frame, text="Save Custom Template", 
                command=lambda: self.save_custom_template(dialog, preview, custom_name_var, 
                                                        section_vars, section_desc_vars)).pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Button(button_frame, text="Preview Custom", 
                command=lambda: self.preview_custom_template(preview, section_vars, section_desc_vars)).pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Button(button_frame, text="Close", 
                command=lambda: self.close_preview_dialog(dialog, canvas)).pack(side=tk.RIGHT)
        
        # FIXED: Handle dialog cleanup properly
        def on_dialog_close():
            try:
                canvas.unbind_all("<MouseWheel>")
            except:
                pass
            try:
                dialog.grab_release()
            except:
                pass
            dialog.destroy()
            if hasattr(self, '_preview_dialog'):
                delattr(self, '_preview_dialog')
        
        dialog.protocol("WM_DELETE_WINDOW", on_dialog_close)

    def close_preview_dialog(self, dialog, canvas):
        """Clean up and close preview dialog - FIXED"""
        try:
            if canvas:
                canvas.unbind_all("<MouseWheel>")
        except:
            pass
        
        # Release modal grab before closing
        try:
            dialog.grab_release()
        except:
            pass
        
        dialog.destroy()
        
        # Clean up reference
        if hasattr(self, '_preview_dialog'):
            delattr(self, '_preview_dialog')

    def close_preview_dialog(self, dialog, canvas):
        """Clean up and close preview dialog"""
        try:
            canvas.unbind_all("<MouseWheel>")
        except:
            pass
        dialog.destroy()
    
    def preview_custom_template(self, original_preview, section_vars, section_desc_vars):
        """Preview the customized template - Fixed z-order and modal behavior"""
        try:
            # Create preview of customized template
            included_sections = []
            for section in original_preview['sections']:
                if section_vars[section['id']].get():  # If section is included
                    # Get custom description
                    desc_widget = section_desc_vars[section['id']]
                    custom_desc = desc_widget.get(1.0, tk.END + "-1c").strip()
                    
                    custom_section = section.copy()
                    custom_section['description'] = custom_desc
                    custom_section['required'] = section_vars[section['id']].get()
                    included_sections.append(custom_section)
            
            if not included_sections:
                messagebox.showwarning("No Sections", "Please select at least one section to include")
                return
            
            # FIXED: Get the parent preview dialog reference
            parent_dialog = getattr(self, '_preview_dialog', self.main_window.root)
            
            # Create preview dialog - FIXED: Set proper parent and modal behavior
            preview_dialog = tk.Toplevel(parent_dialog)
            preview_dialog.title("Custom Template Preview")
            preview_dialog.geometry("600x400")
            
            # CRITICAL FIX: Set transient to parent dialog, not main window
            preview_dialog.transient(parent_dialog)
            
            # CRITICAL FIX: Use grab_set() to make it modal to parent
            preview_dialog.grab_set()
            
            # CRITICAL FIX: Ensure it stays on top of parent
            preview_dialog.lift()
            preview_dialog.focus_force()
            
            # Position relative to parent dialog
            parent_dialog.update_idletasks()  # Ensure parent geometry is updated
            x = parent_dialog.winfo_x() + 50
            y = parent_dialog.winfo_y() + 50
            preview_dialog.geometry(f"600x400+{x}+{y}")
            
            main_frame = ttk.Frame(preview_dialog, padding=10)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(main_frame, text=f"Custom Template Preview", 
                    font=('Arial', 12, 'bold')).pack(pady=(0, 10))
            
            ttk.Label(main_frame, text=f"Sections to be included: {len(included_sections)}", 
                    font=('Arial', 10)).pack(pady=(0, 10))
            
            # Sections list
            tree = ttk.Treeview(main_frame, columns=('Description',), show='tree headings', height=12)
            tree.heading('#0', text='Section Title')
            tree.heading('Description', text='Custom Description')
            tree.column('#0', width=200)
            tree.column('Description', width=350)
            
            for section in included_sections:
                desc = section['description'][:100] + "..." if len(section['description']) > 100 else section['description']
                tree.insert('', tk.END, text=section['title'], values=(desc,))
            
            tree.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
            
            # FIXED: Close button with proper grab handling
            def close_custom_preview():
                preview_dialog.grab_release()
                preview_dialog.destroy()
            
            ttk.Button(main_frame, text="Close", command=close_custom_preview).pack()
            
            # FIXED: Handle window close button (X)
            preview_dialog.protocol("WM_DELETE_WINDOW", close_custom_preview)
            
        except Exception as e:
            messagebox.showerror("Preview Error", f"Could not preview custom template: {e}")

    def save_custom_template(self, dialog, original_preview, custom_name_var, section_vars, section_desc_vars):
        """Save the customized template as a user template"""
        try:
            custom_name = custom_name_var.get().strip()
            if not custom_name:
                messagebox.showerror("Invalid Name", "Please enter a name for your custom template")
                return
            
            # Collect included sections with custom descriptions
            custom_sections = []
            for section in original_preview['sections']:
                if section_vars[section['id']].get():  # If section is included
                    # Get custom description
                    desc_widget = section_desc_vars[section['id']]
                    custom_desc = desc_widget.get(1.0, tk.END + "-1c").strip()
                    
                    if not custom_desc:
                        custom_desc = section['description']  # Fallback to original
                    
                    custom_section = {
                        'id': section['id'],
                        'title': section['title'],
                        'required': True,  # All included sections become required in custom template
                        'order': len(custom_sections) + 1,  # Reorder sequentially
                        'prompt_template': custom_desc
                    }
                    custom_sections.append(custom_section)
            
            if not custom_sections:
                messagebox.showerror("No Sections", "Please select at least one section to include")
                return
            
            # Create custom template data
            custom_template_data = {
                'template_id': self.generate_custom_template_id(custom_name, original_preview['industry']),
                'name': custom_name,
                'description': f"Custom template based on {original_preview['name']}",
                'version': '1.0',
                'industry': original_preview['industry'],
                'category': 'user_custom',
                'document_type': original_preview['document_type'],
                'company_sizes': ['startup', 'small', 'medium', 'large', 'enterprise'],  # Support all sizes
                'tone': 'startup_agile',
                'structure': {
                    'sections': custom_sections
                },
                'estimated_time_minutes': len(custom_sections) * 5,  # 5 min per section estimate
                'complexity_level': 'medium',
                'prerequisites': ['Custom template - review sections before use'],
                'variants': [],
                'compliance_requirements': [],
                'usage_stats': {
                    'created_date': datetime.now().strftime('%Y-%m-%d'),
                    'last_modified': datetime.now().strftime('%Y-%m-%d'),
                    'usage_count': 0,
                    'success_rate': 0.0
                }
            }
            
            # Save the custom template
            if self.save_user_template(custom_template_data):
                messagebox.showinfo("Template Saved", 
                                f"Custom template '{custom_name}' saved successfully!\n\n"
                                f"You can find it in the {original_preview['industry'].title()} → User Custom category.")
                
                # Refresh template data to show the new template
                self.refresh_template_data()
                
                # Close the dialog
                self.close_preview_dialog(dialog, None)
            else:
                messagebox.showerror("Save Failed", "Could not save custom template. Please try again.")
        
        except Exception as e:
            messagebox.showerror("Save Error", f"Error saving custom template: {e}")

    def generate_custom_template_id(self, template_name, industry):
        """Generate a unique ID for custom template"""
        import re
        from datetime import datetime
        
        # Clean template name
        clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', template_name.lower())
        clean_name = re.sub(r'\s+', '_', clean_name.strip())
        
        # Add timestamp for uniqueness
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        return f"custom_{industry}_{clean_name}_{timestamp}"

    def save_user_template(self, template_data):
        """Save custom template to user templates directory"""
        try:
            import yaml
            from datetime import datetime
            
            # Create user templates directory structure
            user_templates_dir = self.app.templates_dir / "user_templates" / template_data['industry'] / "user_custom"
            user_templates_dir.mkdir(parents=True, exist_ok=True)
            
            # Save template file
            template_file = user_templates_dir / f"{template_data['template_id']}.yaml"
            
            with open(template_file, 'w', encoding='utf-8') as f:
                yaml.dump(template_data, f, default_flow_style=False, indent=2)
            
            # Log the creation
            if hasattr(self.app, 'logger'):
                self.app.logger.info(f"Custom template saved: {template_file}")
            
            return True
            
        except Exception as e:
            print(f"Error saving user template: {e}")
            if hasattr(self.app, 'logger'):
                self.app.logger.error(f"Failed to save custom template: {e}")
            return False

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
        """Generate document using the currently selected template"""
        # Check if industry is selected
        if self.industry_var.get() == 'Select Industry':
            messagebox.showwarning("No Industry Selected", "Please select an industry first")
            return
        
        # Check if template is selected
        if not self.current_template_id or self.template_var.get() == 'Select Template':
            messagebox.showwarning("No Template Selected", "Please select a template first")
            return
        
        if not self.main_window.current_project:
            messagebox.showwarning("No Project", "Please create or load a project first")
            return
        
        try:
            # Get project data
            project_data = self.main_window.app.project_manager.get_project_metadata(self.main_window.current_project)
            
            if not project_data:
                messagebox.showerror("Error", "Could not load project data")
                return
            
            # Show generation progress
            self.main_window.status_manager.start_operation("Generating document from template...")
            
            # Generate using template system
            def generate():
                try:
                    if hasattr(self.main_window.app, 'generate_document_from_template'):
                        content = self.main_window.app.generate_document_from_template(
                            self.current_template_id, 
                            project_data
                        )
                        self.main_window.root.after(0, lambda: self.handle_generation_result(content))
                    else:
                        # Fallback to original generation
                        content = self.main_window.app.llm_client.generate_proposal(project_data)
                        self.main_window.root.after(0, lambda: self.handle_generation_result(content))
                except Exception as e:
                    self.main_window.root.after(0, lambda: self.handle_generation_error(str(e)))
            
            # Run generation in thread
            import threading
            thread = threading.Thread(target=generate, daemon=True)
            thread.start()
            
        except Exception as e:
            self.main_window.status_manager.end_operation("Generation failed")
            messagebox.showerror("Generation Error", f"Failed to generate document: {e}")

    def handle_generation_result(self, content):
        """Handle successful document generation"""
        self.main_window.status_manager.end_operation("Document generated successfully")
        
        # Load content into editor
        self.set_content(content)
        self.main_window.unsaved_changes = True
        self.main_window.current_document_type = "template_generated"
        self.main_window.update_window_title()
        
        # Update version info
        template_name = self.template_var.get().split(' (')[0] if self.template_var.get() else "Template"
        self.update_version_label(f"Generated from {template_name}")

    def handle_generation_error(self, error_message):
        """Handle document generation error"""
        self.main_window.status_manager.end_operation("Generation failed")
        messagebox.showerror("Generation Error", f"Document generation failed:\n\n{error_message}")

    def get_current_template_id(self):
        """Get the currently selected template ID"""
        return self.current_template_id
    
    def use_template_from_preview(self, dialog, preview):
        """Use the original template from preview without customization"""
        try:
            # Set the template selection in the UI
            template_id = preview['template_id']
            
            # Find and set the industry
            industry_formatted = self.format_industry_name(preview['industry'])
            if industry_formatted in self.industry_combo['values']:
                self.industry_var.set(industry_formatted)
                self.on_industry_change()
            
            # Find and set the template
            template_display_name = f"{preview['name']} ({preview['document_type'].title()})"
            if template_display_name in self.template_combo['values']:
                self.template_var.set(template_display_name)
                self.on_template_change()
            
            # Close the preview dialog
            self.close_preview_dialog(dialog, None)
            
            # Notify user
            self.main_window.set_status(f"Selected template: {preview['name']}")
            
        except Exception as e:
            messagebox.showerror("Template Selection Error", f"Could not select template: {e}")
    
    def refresh_template_data(self):
        """Refresh template data (useful after template library updates)"""
        try:
            current_industry = self.industry_var.get()
            current_template = self.template_var.get()
            
            # Reload template data
            self.load_template_data()
            
            # Try to restore selections if they were valid (not default selections)
            if current_industry != 'Select Industry' and current_industry in self.industry_combo['values']:
                self.industry_var.set(current_industry)
                self.on_industry_change()  # This will load templates and enable dropdown
                
                if current_template != 'Select Template' and current_template in self.template_combo['values']:
                    self.template_var.set(current_template)
                    self.on_template_change()
            
            print("Template data refreshed successfully")
            
        except Exception as e:
            print(f"Error refreshing template data: {e}")
    
    def load_document(self, project_name: str, doc_type: str, content: str = None):
        """Load document content into the editor (updated for new template selection)"""
        # If doc_type looks like a template ID, handle it specially
        if hasattr(self.app, 'template_manager') and self.app.template_manager:
            template = self.app.template_manager.get_template(doc_type)
            if template:
                # This is a template-based document
                self.current_template_id = doc_type
                
                # Set industry selection (this will enable template dropdown)
                formatted_industry = self.format_industry_name(template.industry.value)
                if formatted_industry in self.industry_combo['values']:
                    self.industry_var.set(formatted_industry)
                    self.on_industry_change()  # This loads templates and enables dropdown
                    
                    # Set template selection
                    template_display_name = f"{template.name} ({template.document_type.value.title()})"
                    if template_display_name in self.template_combo['values']:
                        self.template_var.set(template_display_name)
                        self.on_template_change()
        
        # Clear editor
        self.text_editor.delete(1.0, tk.END)
        
        if content:
            self.text_editor.insert(1.0, content)
            
            # Update version info
            if self.current_template_id:
                template_name = self.template_var.get().split(' (')[0] if self.template_var.get() != 'Select Template' else "Template"
                self.version_label.config(text=f"Generated from {template_name}")
            else:
                self.version_label.config(text=f"Document loaded")
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
        if hasattr(self, 'version_label'):
            self.version_label.config(text=version_text)
        else:
            # Create version label if it doesn't exist
            self._create_version_label(version_text)

    def _create_version_label(self, initial_text: str = "No document loaded"):
        """Create version label if it doesn't exist"""
        try:
            # Find appropriate parent frame to add version label
            if hasattr(self, 'editor_frame'):
                version_frame = ttk.Frame(self.editor_frame)
                version_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=2)
                
                self.version_label = ttk.Label(version_frame, text=initial_text, 
                                            font=('Arial', 8), foreground='gray')
                self.version_label.pack(side=tk.LEFT)
        except Exception as e:
            print(f"Could not create version label: {e}")
    
    def get_current_document_type(self) -> str:
        """Get the current document type"""
        if hasattr(self, 'current_template_id') and self.current_template_id:
            return self.current_template_id
        return "proposal"