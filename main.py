#!/usr/bin/env python3
"""
LLM-Powered Project Proposal Generator
Main Application Entry Point
"""

import sys
import os
import logging
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
        self.setup_logging()
        self.load_config()
        self.init_database()
        
        # NEW: Initialize Template Manager
        self.init_template_manager()
        
        # Initialize LLM clients (both original and universal)
        self.init_llm_clients()
        
        # Initialize project manager
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
        self.templates_dir = self.base_dir / "templates"
        self.projects_dir = self.base_dir / "Projects"
        self.config_dir = self.base_dir / "config"
        self.db_path = self.base_dir / "meta.db"
        
        # Create directories
        self.projects_dir.mkdir(exist_ok=True)
        self.config_dir.mkdir(exist_ok=True)
        self.templates_dir.mkdir(exist_ok=True)
    
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

    def init_template_manager(self):
        """Initialize the Template Manager"""
        try:
            from template_manager import TemplateManager
            
            # Template directory setup
            self.templates_dir = self.base_dir / "templates"
            
            # Create templates directory if it doesn't exist
            if not self.templates_dir.exists():
                self.templates_dir.mkdir(exist_ok=True)
                self.logger.warning(f"Created templates directory: {self.templates_dir}")
                
                # Create a basic template structure
                self._create_default_template_structure()
            
            # Initialize template manager
            self.template_manager = TemplateManager(self.templates_dir)
            
            # Log template loading results
            template_count = len(self.template_manager)
            self.logger.info(f"Template Manager initialized with {template_count} templates")
            
            if template_count == 0:
                self.logger.warning("No templates loaded. Application will use fallback generation methods.")
            
            # Get template statistics for logging
            stats = self.template_manager.get_template_statistics()
            if stats['load_errors'] > 0:
                self.logger.warning(f"Template loading errors: {stats['load_errors']}")
                for error in self.template_manager.get_load_errors()[:3]:
                    self.logger.warning(f"  - {error}")
        
        except Exception as e:
            self.logger.error(f"Failed to initialize Template Manager: {e}")
            self.template_manager = None

    def init_llm_clients(self):
        """Initialize both original and universal LLM clients"""
        try:
            # Initialize original LLM client (for backward compatibility)
            self.llm_client = LLMClient(self.config.get('llm', {}), self.config.get('company', {}))
            
            # Initialize Universal LLM client (new template-based client)
            from universal_llm_client import UniversalLLMClient
            self.universal_llm_client = UniversalLLMClient(
                self.config.get('llm', {}), 
                self.config.get('company', {}),
                self.template_manager
            )
            
            self.logger.info("LLM clients initialized successfully")
            
            # Test LLM connection if template manager is available
            if self.template_manager and len(self.template_manager) > 0:
                try:
                    # Test with a simple template preview (no actual LLM call)
                    first_template = self.template_manager.get_all_templates()[0]
                    preview = self.universal_llm_client.get_template_preview(first_template.template_id)
                    self.logger.info(f"Universal LLM Client ready - tested with template: {preview['name']}")
                except Exception as e:
                    self.logger.warning(f"Universal LLM Client test failed: {e}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize LLM clients: {e}")
            # Fallback to original client only
            try:
                self.llm_client = LLMClient(self.config.get('llm', {}), self.config.get('company', {}))
                self.universal_llm_client = None
                self.logger.info("Fallback: Using original LLM client only")
            except Exception as fallback_error:
                self.logger.error(f"Failed to initialize even original LLM client: {fallback_error}")
                self.llm_client = None
                self.universal_llm_client = None

    def _create_default_template_structure(self):
        """Create default template directory structure"""
        try:
            # Create industry directories
            industries = ['technology', 'business', 'services', 'manufacturing']
            
            for industry in industries:
                industry_dir = self.templates_dir / industry
                industry_dir.mkdir(exist_ok=True)
                
                # Create category subdirectories
                if industry == 'technology':
                    categories = ['software_development', 'hardware_development', 'product_management']
                elif industry == 'business':
                    categories = ['strategic_planning', 'financial_analysis', 'operations']
                elif industry == 'services':
                    categories = ['consulting', 'client_services', 'professional_services']
                else:  # manufacturing
                    categories = ['engineering', 'quality_control', 'supply_chain']
                
                for category in categories:
                    category_dir = industry_dir / category
                    category_dir.mkdir(exist_ok=True)
            
            self.logger.info("Created default template directory structure")
            
            # Create a sample template file if none exist
            self._create_sample_template()
            
        except Exception as e:
            self.logger.error(f"Failed to create default template structure: {e}")

    def _create_sample_template(self):
        """Create a sample template file for demonstration"""
        try:
            import yaml
            
            sample_template = {
                'template_id': 'sample_business_proposal',
                'name': 'Sample Business Proposal',
                'description': 'A sample template for business project proposals',
                'version': '1.0',
                'industry': 'business',
                'category': 'strategic_planning',
                'document_type': 'proposal',
                'company_sizes': ['startup', 'small'],
                'tone': 'startup_agile',
                'structure': {
                    'sections': [
                        {
                            'id': 'executive_summary',
                            'title': 'Executive Summary',
                            'required': True,
                            'order': 1,
                            'prompt_template': 'Create a compelling executive summary that captures the project\'s value proposition and business impact.'
                        },
                        {
                            'id': 'project_overview',
                            'title': 'Project Overview',
                            'required': True,
                            'order': 2,
                            'prompt_template': 'Provide a detailed project overview including objectives, scope, and success criteria.'
                        },
                        {
                            'id': 'implementation_plan',
                            'title': 'Implementation Plan',
                            'required': True,
                            'order': 3,
                            'prompt_template': 'Detail the implementation approach, timeline, and key milestones.'
                        }
                    ]
                },
                'estimated_time_minutes': 30,
                'complexity_level': 'medium',
                'prerequisites': ['Project requirements defined', 'Stakeholder approval obtained'],
                'usage_stats': {
                    'created_date': '2024-01-01',
                    'last_modified': '2024-01-01',
                    'usage_count': 0,
                    'success_rate': 0.0
                }
            }
            
            # Save sample template
            sample_file = self.templates_dir / 'business' / 'strategic_planning' / 'sample_business_proposal.yaml'
            with open(sample_file, 'w', encoding='utf-8') as f:
                yaml.dump(sample_template, f, default_flow_style=False, indent=2)
            
            self.logger.info(f"Created sample template: {sample_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to create sample template: {e}")

    def get_available_templates(self, filters=None):
        """Get available templates for UI components"""
        if self.template_manager:
            return self.template_manager.get_available_templates(filters)
        return []

    def get_template_preview(self, template_id):
        """Get template preview for UI"""
        if self.universal_llm_client:
            try:
                return self.universal_llm_client.get_template_preview(template_id)
            except Exception as e:
                self.logger.error(f"Failed to get template preview: {e}")
        return None

    def generate_document_from_template(self, template_id, project_data, selected_sections=None):
        """Generate document using template system"""
        if self.universal_llm_client:
            try:
                return self.universal_llm_client.generate_from_template(
                    template_id, 
                    project_data, 
                    selected_sections
                )
            except Exception as e:
                self.logger.error(f"Template-based generation failed: {e}")
                # Fallback to original generation method
                return self._fallback_generation(project_data)
        else:
            return self._fallback_generation(project_data)

    def _fallback_generation(self, project_data):
        """Fallback to original generation method"""
        if self.llm_client:
            try:
                # Use original proposal generation as fallback
                return self.llm_client.generate_proposal(project_data)
            except Exception as e:
                self.logger.error(f"Fallback generation failed: {e}")
                return "# Document Generation Failed\n\nPlease check your LLM configuration and try again."
        else:
            return "# LLM Client Not Available\n\nPlease configure your LLM settings in the application."

    def get_suitable_templates_for_project(self, project_data):
        """Get templates suitable for a specific project"""
        if self.universal_llm_client:
            try:
                return self.universal_llm_client.list_suitable_templates(project_data)
            except Exception as e:
                self.logger.error(f"Failed to get suitable templates: {e}")
        return []

    def validate_template_for_project(self, template_id, project_data):
        """Validate template compatibility with project"""
        if self.universal_llm_client:
            try:
                return self.universal_llm_client.validate_template_compatibility(template_id, project_data)
            except Exception as e:
                self.logger.error(f"Template validation failed: {e}")
        return {'compatible': False, 'score': 0, 'issues': ['Template validation not available']}
    
    def setup_logging(self):
        """Setup application logging to file only"""
        import logging
        from datetime import datetime
        
        # Create logs directory if it doesn't exist
        logs_dir = self.base_dir / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        # Create session-based log file name
        session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = logs_dir / f"app_session_{session_timestamp}.log"
        
        # Configure logging to file only (no console output)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8')
                # Removed StreamHandler() to disable console output
            ],
            force=True  # Override any existing logging configuration
        )
        
        self.logger = logging.getLogger(__name__)
        self.log_file_path = log_file  # Store log file path for reference
        
        # Log session start
        self.logger.info("="*60)
        self.logger.info(f"APPLICATION SESSION STARTED")
        self.logger.info(f"Session ID: {session_timestamp}")
        self.logger.info(f"Log file: {log_file}")
        self.logger.info("="*60)

    def reload_templates(self):
        """Reload templates from disk"""
        if self.template_manager:
            try:
                self.template_manager.reload_templates()
                self.logger.info("Templates reloaded successfully")
                return True
            except Exception as e:
                self.logger.error(f"Failed to reload templates: {e}")
                return False
        return False

    def get_template_statistics(self):
        """Get template system statistics"""
        if self.template_manager:
            return self.template_manager.get_template_statistics()
        return {'total_templates': 0, 'by_industry': {}, 'by_document_type': {}, 'load_errors': 0}

    def export_template_catalog(self, output_path):
        """Export template catalog for sharing"""
        if self.template_manager:
            try:
                self.template_manager.export_template_catalog(Path(output_path))
                self.logger.info(f"Template catalog exported to: {output_path}")
                return True
            except Exception as e:
                self.logger.error(f"Failed to export template catalog: {e}")
                return False
        return False

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