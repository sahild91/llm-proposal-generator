#!/usr/bin/env python3
"""
LLM-Powered Project Proposal Generator
Main Application Entry Point
"""

import sys
import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import yaml
from datetime import datetime
import sqlite3
import threading
from typing import Dict, Any, Optional

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from llm_client import LLMClient
from project_manager import ProjectManager
from ui.main_window import MainWindow

class ProposalGeneratorApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("LLM Proposal Generator")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Initialize core components
        self.setup_directories()
        self.load_config()
        self.init_database()
        
        # Initialize managers
        self.llm_client = LLMClient(self.config.get('llm', {}), self.config.get('company', {}))
        self.project_manager = ProjectManager(self.projects_dir, self.db_path)
        
        # Initialize document exporter
        from document_exporter import DocumentExporter
        self.document_exporter = DocumentExporter(self.config.get('company', {}))
        
        # Initialize UI
        self.main_window = MainWindow(self.root, self)
        
        # Setup window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_directories(self):
        """Create necessary directories if they don't exist"""
        self.base_dir = Path.cwd()
        self.projects_dir = self.base_dir / "Projects"
        self.config_dir = self.base_dir / "config"
        self.db_path = self.base_dir / "meta.db"
        
        # Create directories
        self.projects_dir.mkdir(exist_ok=True)
        self.config_dir.mkdir(exist_ok=True)
    
    def load_config(self):
        """Load configuration from YAML files"""
        llm_config_file = self.config_dir / "llm_config.yaml"
        company_config_file = self.config_dir / "company_config.yaml"
        
        # Load LLM configuration
        if llm_config_file.exists():
            try:
                with open(llm_config_file, 'r', encoding='utf-8') as f:
                    llm_config = yaml.safe_load(f) or {}
            except Exception as e:
                print(f"Error loading LLM config: {e}")
                llm_config = self._get_default_llm_config()
        else:
            llm_config = self._get_default_llm_config()
        
        # Load Company configuration
        if company_config_file.exists():
            try:
                with open(company_config_file, 'r', encoding='utf-8') as f:
                    company_data = yaml.safe_load(f) or {}
                    company_config = company_data.get('company', {})
            except Exception as e:
                print(f"Error loading company config: {e}")
                company_config = self._get_default_company_config()
        else:
            company_config = self._get_default_company_config()
        
        # Combine configurations
        self.config = {
            **llm_config,
            'company': company_config
        }
        
        # Create config files if they don't exist
        if not llm_config_file.exists() or not company_config_file.exists():
            self.save_config()
    
    def save_config(self):
        """Save configuration to separate YAML files"""
        llm_config_file = self.config_dir / "llm_config.yaml"
        company_config_file = self.config_dir / "company_config.yaml"
        
        try:
            # Save LLM config (exclude company data)
            llm_data = {k: v for k, v in self.config.items() if k != 'company'}
            with open(llm_config_file, 'w', encoding='utf-8') as f:
                yaml.dump(llm_data, f, default_flow_style=False, indent=2)
            
            # Save Company config
            company_data = {'company': self.config.get('company', {})}
            with open(company_config_file, 'w', encoding='utf-8') as f:
                yaml.dump(company_data, f, default_flow_style=False, indent=2)
            
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def init_database(self):
        """Initialize SQLite database for metadata tracking"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create projects table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    client_name TEXT,
                    project_type TEXT,
                    description TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'draft'
                )
            ''')
            
            # Create document versions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS document_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER,
                    document_type TEXT,
                    version INTEGER,
                    content TEXT,
                    changelog TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects (id)
                )
            ''')
            
            conn.commit()
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to initialize database: {e}")

    def _get_default_llm_config(self):
        """Get default LLM configuration"""
        return {
            'llm': {
                'provider': 'openai',
                'model': 'gpt-4',
                'api_key': '',
                'endpoint': 'https://api.openai.com/v1/chat/completions',
                'max_tokens': 4000,
                'temperature': 0.7
            },
            'app': {
                'auto_save': True,
                'auto_save_interval': 30,
                'theme': 'default',
                'default_project_type': 'Software',
                'default_export_format': 'pdf',
                'backup_enabled': True,
                'max_versions': 10
            }
        }

    def _get_default_company_config(self):
        """Get default company configuration"""
        return {
            'name': 'Your Company Name',
            'tagline': 'Your trusted partner',
            'industry': 'Technology Solutions',
            'email': '',
            'phone': '',
            'website': '',
            'address': '',
            'logo_path': '',
            'specializations': ['Software Development', 'System Integration'],
            'registration_number': '',
            'tax_id': '',
            'default_author': 'Project Manager',
            'authors': ['Project Manager', 'Technical Lead']
        }
    
    def run(self):
        """Start the application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.on_closing()
    
    def on_closing(self):
        """Handle application closing"""
        # Save any unsaved work
        if hasattr(self, 'main_window'):
            self.main_window.save_current_work()
        
        # Close database connections
        if hasattr(self, 'project_manager'):
            self.project_manager.close()
        
        self.root.destroy()

def main():
    """Main entry point"""
    # Check Python version
    if sys.version_info < (3, 7):
        print("Python 3.7 or higher is required")
        sys.exit(1)
    
    # Create and run application
    app = ProposalGeneratorApp()
    app.run()

if __name__ == "__main__":
    main()