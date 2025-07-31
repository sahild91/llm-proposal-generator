"""
Company Settings Dialog
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog


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
        self._create_company_info_section(main_frame)
        
        # Contact Information Section
        self._create_contact_info_section(main_frame)
        
        # Specializations Section
        self._create_specializations_section(main_frame)
        
        # Legal Information Section
        self._create_legal_info_section(main_frame)
        
        # Document Authors Section
        self._create_authors_section(main_frame)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(button_frame, text="Save", command=self.save_settings).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.RIGHT)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _create_company_info_section(self, parent):
        """Create company information section"""
        company_frame = ttk.LabelFrame(parent, text="Company Information", padding=15)
        company_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Company Name
        ttk.Label(company_frame, text="Company Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.company_name_var = tk.StringVar()
        ttk.Entry(company_frame, textvariable=self.company_name_var, width=50).grid(
            row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Tagline
        ttk.Label(company_frame, text="Tagline:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.tagline_var = tk.StringVar()
        ttk.Entry(company_frame, textvariable=self.tagline_var, width=50).grid(
            row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Industry
        ttk.Label(company_frame, text="Industry:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.industry_var = tk.StringVar()
        ttk.Entry(company_frame, textvariable=self.industry_var, width=50).grid(
            row=2, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Logo Path
        ttk.Label(company_frame, text="Logo Path:").grid(row=3, column=0, sticky=tk.W, pady=5)
        logo_frame = ttk.Frame(company_frame)
        logo_frame.grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        self.logo_path_var = tk.StringVar()
        ttk.Entry(logo_frame, textvariable=self.logo_path_var, width=40).pack(side=tk.LEFT)
        ttk.Button(logo_frame, text="Browse", command=self.browse_logo, width=8).pack(side=tk.LEFT, padx=(5, 0))
    
    def _create_contact_info_section(self, parent):
        """Create contact information section"""
        contact_frame = ttk.LabelFrame(parent, text="Contact Information", padding=15)
        contact_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Website
        ttk.Label(contact_frame, text="Website:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.website_var = tk.StringVar()
        ttk.Entry(contact_frame, textvariable=self.website_var, width=50).grid(
            row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Email
        ttk.Label(contact_frame, text="Email:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.email_var = tk.StringVar()
        ttk.Entry(contact_frame, textvariable=self.email_var, width=50).grid(
            row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Phone
        ttk.Label(contact_frame, text="Phone:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.phone_var = tk.StringVar()
        ttk.Entry(contact_frame, textvariable=self.phone_var, width=50).grid(
            row=2, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Address
        ttk.Label(contact_frame, text="Address:").grid(row=3, column=0, sticky=tk.NW, pady=5)
        self.address_text = scrolledtext.ScrolledText(contact_frame, width=50, height=4)
        self.address_text.grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=5)
    
    def _create_specializations_section(self, parent):
        """Create specializations section"""
        spec_frame = ttk.LabelFrame(parent, text="Specializations", padding=15)
        spec_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(spec_frame, text="Specializations:").grid(row=0, column=0, sticky=tk.NW, pady=5)
        self.specializations_text = scrolledtext.ScrolledText(spec_frame, width=50, height=6)
        self.specializations_text.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        ttk.Label(spec_frame, text="(one per line)", font=('Arial', 8)).grid(
            row=1, column=1, sticky=tk.W, padx=(10, 0))
    
    def _create_legal_info_section(self, parent):
        """Create legal information section"""
        legal_frame = ttk.LabelFrame(parent, text="Legal Information", padding=15)
        legal_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Registration Number
        ttk.Label(legal_frame, text="Registration Number:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.reg_number_var = tk.StringVar()
        ttk.Entry(legal_frame, textvariable=self.reg_number_var, width=50).grid(
            row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Tax ID
        ttk.Label(legal_frame, text="Tax ID:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.tax_id_var = tk.StringVar()
        ttk.Entry(legal_frame, textvariable=self.tax_id_var, width=50).grid(
            row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
    
    def _create_authors_section(self, parent):
        """Create document authors section"""
        authors_frame = ttk.LabelFrame(parent, text="Document Authors", padding=15)
        authors_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Default Author
        ttk.Label(authors_frame, text="Default Author:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.default_author_var = tk.StringVar()
        ttk.Entry(authors_frame, textvariable=self.default_author_var, width=50).grid(
            row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Available Authors
        ttk.Label(authors_frame, text="Available Authors:").grid(row=1, column=0, sticky=tk.NW, pady=5)
        self.authors_text = scrolledtext.ScrolledText(authors_frame, width=50, height=4)
        self.authors_text.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        ttk.Label(authors_frame, text="(one per line, e.g., 'John Smith - Senior Project Manager')", 
                  font=('Arial', 8)).grid(row=2, column=1, sticky=tk.W, padx=(10, 0))
    
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
            'authors': authors
        }
        
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel dialog"""
        self.dialog.destroy()