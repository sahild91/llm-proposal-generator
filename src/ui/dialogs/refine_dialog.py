"""
Document Refinement Dialog
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext


class RefineDialog:
    """Dialog for refining documents"""
    
    def __init__(self, parent):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Refine Document")
        self.dialog.geometry("500x350")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        self.dialog.wait_window()
    
    def create_widgets(self):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Instructions
        instruction_label = ttk.Label(
            main_frame, 
            text="Please describe what you want to refine in the document:", 
            font=('Arial', 10)
        )
        instruction_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Text input
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
            "Add cost breakdown details",
            "Include more implementation details",
            "Enhance the executive summary section"
        ]
        
        for example in examples:
            example_label = ttk.Label(
                example_frame, 
                text=f"• {example}", 
                font=('Arial', 9)
            )
            example_label.pack(anchor=tk.W, pady=1)
        
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