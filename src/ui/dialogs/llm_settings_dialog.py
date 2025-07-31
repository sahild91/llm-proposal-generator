"""
LLM Settings Dialog
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os


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
        self._create_provider_section(main_frame)
        
        # Configuration section
        self._create_config_section(main_frame)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Test Connection", command=self.test_connection).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Save", command=self.save_settings).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.RIGHT)
    
    def _create_provider_section(self, parent):
        """Create provider selection section"""
        provider_frame = ttk.LabelFrame(parent, text="LLM Provider", padding=10)
        provider_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.provider_var = tk.StringVar(value="openai")
        
        ttk.Radiobutton(provider_frame, text="OpenAI", variable=self.provider_var, 
                        value="openai", command=self.on_provider_change).pack(anchor=tk.W)
        ttk.Radiobutton(provider_frame, text="Anthropic (Claude)", variable=self.provider_var, 
                        value="anthropic", command=self.on_provider_change).pack(anchor=tk.W)
        ttk.Radiobutton(provider_frame, text="Local LLM", variable=self.provider_var, 
                        value="local", command=self.on_provider_change).pack(anchor=tk.W)
    
    def _create_config_section(self, parent):
        """Create configuration section"""
        config_frame = ttk.LabelFrame(parent, text="Configuration", padding=10)
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
        ttk.Entry(config_frame, textvariable=self.endpoint_var, width=50).grid(
            row=2, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Advanced settings
        advanced_frame = ttk.LabelFrame(config_frame, text="Advanced Settings", padding=10)
        advanced_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W+tk.E, pady=15)
        
        # Max tokens
        ttk.Label(advanced_frame, text="Max Tokens:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.max_tokens_var = tk.StringVar(value="4000")
        ttk.Entry(advanced_frame, textvariable=self.max_tokens_var, width=20).grid(
            row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Temperature
        ttk.Label(advanced_frame, text="Temperature:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.temperature_var = tk.StringVar(value="0.7")
        ttk.Entry(advanced_frame, textvariable=self.temperature_var, width=20).grid(
            row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
    
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
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
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