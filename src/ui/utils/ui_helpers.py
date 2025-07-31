"""
UI Helper Functions and Utilities
"""

import tkinter as tk
from tkinter import ttk
import threading
from typing import Callable, Any


def center_window(window: tk.Toplevel, width: int, height: int):
    """Center a window on the screen"""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    
    window.geometry(f"{width}x{height}+{x}+{y}")


def run_in_thread(func: Callable, callback: Callable = None, *args, **kwargs):
    """Run a function in a separate thread with optional callback"""
    def wrapper():
        try:
            result = func(*args, **kwargs)
            if callback:
                callback(result, None)
        except Exception as e:
            if callback:
                callback(None, e)
    
    thread = threading.Thread(target=wrapper, daemon=True)
    thread.start()
    return thread


def create_tooltip(widget, text: str):
    """Create a tooltip for a widget"""
    def on_enter(event):
        tooltip = tk.Toplevel()
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
        
        label = ttk.Label(tooltip, text=text, background="lightyellow", 
                         relief="solid", borderwidth=1, font=("Arial", 9))
        label.pack()
        
        widget.tooltip = tooltip
    
    def on_leave(event):
        if hasattr(widget, 'tooltip'):
            widget.tooltip.destroy()
            del widget.tooltip
    
    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)


def validate_number_entry(value: str, allow_float: bool = False) -> bool:
    """Validate numeric entry input"""
    if not value:
        return True
    
    try:
        if allow_float:
            float(value)
        else:
            int(value)
        return True
    except ValueError:
        return False


def create_scrollable_frame(parent) -> tuple[tk.Canvas, ttk.Frame]:
    """Create a scrollable frame setup"""
    canvas = tk.Canvas(parent)
    scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    return canvas, scrollable_frame, scrollbar


def bind_mousewheel(canvas: tk.Canvas, scrollable_frame: ttk.Frame):
    """Bind mousewheel scrolling to a canvas"""
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def bind_to_mousewheel(event):
        canvas.bind_all("<MouseWheel>", on_mousewheel)
    
    def unbind_from_mousewheel(event):
        canvas.unbind_all("<MouseWheel>")
    
    canvas.bind('<Enter>', bind_to_mousewheel)
    canvas.bind('<Leave>', unbind_from_mousewheel)


class ProgressDialog:
    """Simple progress dialog for long operations"""
    
    def __init__(self, parent, title: str, message: str):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x150")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        center_window(self.dialog, 400, 150)
        
        # Create widgets
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text=message, font=('Arial', 10)).pack(pady=(0, 20))
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, pady=(0, 20))
        
        self.status_label = ttk.Label(main_frame, text="Processing...")
        self.status_label.pack()
        
        self.progress_bar.start()
    
    def update_status(self, status: str):
        """Update the status message"""
        self.status_label.config(text=status)
        self.dialog.update()
    
    def close(self):
        """Close the progress dialog"""
        self.progress_bar.stop()
        self.dialog.destroy()


class StatusManager:
    """Manages status updates for the main window"""
    
    def __init__(self, status_label: ttk.Label, progress_bar: ttk.Progressbar, root: tk.Tk):
        self.status_label = status_label
        self.progress_bar = progress_bar
        self.root = root
        self._operation_count = 0
    
    def set_status(self, message: str):
        """Set status message"""
        self.status_label.config(text=message)
    
    def start_operation(self, message: str):
        """Start a long operation"""
        self._operation_count += 1
        self.set_status(message)
        self.progress_bar.start()
        self.root.config(cursor="wait")
    
    def end_operation(self, message: str = "Ready"):
        """End a long operation"""
        self._operation_count = max(0, self._operation_count - 1)
        
        if self._operation_count == 0:
            self.progress_bar.stop()
            self.root.config(cursor="")
        
        self.set_status(message)


def create_file_type_filters():
    """Get common file type filters for dialogs"""
    return {
        'markdown': [("Markdown files", "*.md"), ("All files", "*.*")],
        'pdf': [("PDF files", "*.pdf"), ("All files", "*.*")],
        'docx': [("Word documents", "*.docx"), ("All files", "*.*")],
        'html': [("HTML files", "*.html"), ("All files", "*.*")],
        'image': [("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"), ("All files", "*.*")],
        'yaml': [("YAML files", "*.yaml *.yml"), ("All files", "*.*")],
        'json': [("JSON files", "*.json"), ("All files", "*.*")]
    }


def show_info_dialog(parent, title: str, message: str, details: str = None):
    """Show an information dialog with optional details"""
    dialog = tk.Toplevel(parent)
    dialog.title(title)
    dialog.geometry("400x300" if details else "300x150")
    dialog.resizable(True, True)
    dialog.transient(parent)
    dialog.grab_set()
    
    center_window(dialog, 400 if details else 300, 300 if details else 150)
    
    main_frame = ttk.Frame(dialog, padding=15)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Message
    ttk.Label(main_frame, text=message, font=('Arial', 10)).pack(pady=(0, 10))
    
    # Details if provided
    if details:
        details_frame = ttk.LabelFrame(main_frame, text="Details", padding=10)
        details_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        details_text = tk.Text(details_frame, wrap=tk.WORD, height=10)
        scrollbar_details = ttk.Scrollbar(details_frame, orient=tk.VERTICAL, command=details_text.yview)
        details_text.configure(yscrollcommand=scrollbar_details.set)
        
        details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_details.pack(side=tk.RIGHT, fill=tk.Y)
        
        details_text.insert(1.0, details)
        details_text.config(state=tk.DISABLED)
    
    # OK button
    ttk.Button(main_frame, text="OK", command=dialog.destroy).pack()


def apply_theme(root: tk.Tk, theme_name: str = "default"):
    """Apply a theme to the application (placeholder for future theming)"""
    # This is a placeholder for future theme implementation
    if theme_name == "dark":
        # Dark theme settings would go here
        pass
    elif theme_name == "light":
        # Light theme settings would go here
        pass
    # Default theme is already applied by tkinter