#!/usr/bin/env python3
"""
LLM Proposal Generator Installer
Automated setup script for first-time installation
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_banner():
    """Print installation banner"""
    print("=" * 60)
    print("  LLM Proposal Generator - Installation Script")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    print("Checking Python version...")
    if sys.version_info < (3, 7):
        print(f"❌ Python 3.7+ is required. Found Python {sys.version_info.major}.{sys.version_info.minor}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def check_pip():
    """Check if pip is available"""
    print("Checking pip...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, capture_output=True)
        print("✅ pip is available")
        return True
    except subprocess.CalledProcessError:
        print("❌ pip is not available")
        return False

def install_dependencies():
    """Install Python dependencies"""
    print("Installing dependencies...")
    requirements_file = Path("requirements.txt")
    
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    try:
        # Install core dependencies
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True)
        print("✅ Core dependencies installed successfully")
        
        # Test imports
        try:
            import requests
            import yaml
            print("✅ Core imports working")
        except ImportError as e:
            print(f"❌ Core import failed: {e}")
            return False
        
        # Test export dependencies
        export_issues = []
        
        try:
            import reportlab
            print("✅ PDF export support available")
        except ImportError:
            export_issues.append("PDF export (reportlab)")
        
        try:
            import docx
            print("✅ DOCX export support available")
        except ImportError:
            export_issues.append("DOCX export (python-docx)")
        
        try:
            from PIL import Image
            print("✅ Image processing support available")
        except ImportError:
            export_issues.append("Image processing (Pillow)")
        
        if export_issues:
            print(f"⚠️  Some export features may not work: {', '.join(export_issues)}")
            print("   Run 'pip install reportlab python-docx Pillow' to enable all features")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("Creating directories...")
    directories = ["Projects", "config"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def setup_configuration():
    """Setup configuration file"""
    print("Setting up configuration...")
    
    config_dir = Path("config")
    example_config = config_dir / "llm_config.yaml.example"
    config_file = config_dir / "llm_config.yaml"
    
    if example_config.exists() and not config_file.exists():
        shutil.copy2(example_config, config_file)
        print("✅ Created default configuration file")
        print("📝 Please edit config/llm_config.yaml with your API keys")
        return True
    elif config_file.exists():
        print("✅ Configuration file already exists")
        return True
    else:
        print("❌ Configuration template not found")
        return False

def test_installation():
    """Test if installation was successful"""
    print("Testing installation...")
    
    try:
        # Test imports
        import requests
        import yaml
        print("✅ Core dependencies working")
        
        # Test file structure
        required_files = ["main.py", "src/llm_client.py", "src/project_manager.py"]
        for file_path in required_files:
            if not Path(file_path).exists():
                print(f"❌ Missing required file: {file_path}")
                return False
        
        print("✅ File structure is correct")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def create_desktop_shortcuts():
    """Create desktop shortcuts (optional)"""
    print("Creating shortcuts...")
    
    current_dir = Path.cwd().resolve()
    
    # Windows shortcut
    if sys.platform == "win32":
        try:
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            shortcut_path = os.path.join(desktop, "LLM Proposal Generator.lnk")
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = str(current_dir / "run_app.bat")
            shortcut.WorkingDirectory = str(current_dir)
            shortcut.IconLocation = str(current_dir / "main.py")
            shortcut.save()
            
            print("✅ Desktop shortcut created")
        except ImportError:
            print("⚠️  Could not create desktop shortcut (winshell not available)")
        except Exception as e:
            print(f"⚠️  Could not create desktop shortcut: {e}")
    
    # Linux/macOS shortcut placeholder
    else:
        print("⚠️  Desktop shortcuts not implemented for this platform")

def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "=" * 60)
    print("  Installation Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Configure LLM settings:")
    print("   - Edit config/llm_config.yaml with your API keys")
    print("   - Choose your LLM provider (OpenAI, Anthropic, or Local)")
    print()
    print("2. Configure company information:")
    print("   - Run the application and go to Settings → Company Settings")
    print("   - Add your company name, logo, and contact details")
    print("   - This information will appear in all generated proposals")
    print()
    print("3. Run the application:")
    
    if sys.platform == "win32":
        print("   - Double-click run_app.bat")
        print("   - Or run: python main.py")
    else:
        print("   - Run: ./run_app.sh")
        print("   - Or run: python3 main.py")
    
    print()
    print("Features available:")
    print("✅ Project creation and management")
    print("✅ LLM-powered document generation")
    print("✅ Export to PDF, DOCX, HTML, and Markdown")
    print("✅ Company branding in documents")
    print("✅ Version control and backups")
    print()
    print("For help and documentation, see README.md")
    print()

def main():
    """Main installation process"""
    print_banner()
    
    # Check prerequisites
    if not check_python_version():
        return False
    
    if not check_pip():
        return False
    
    # Install components
    if not install_dependencies():
        return False
    
    create_directories()
    
    if not setup_configuration():
        return False
    
    if not test_installation():
        return False
    
    # Optional features
    create_desktop_shortcuts()
    
    print_next_steps()
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ Installation failed. Please check the errors above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during installation: {e}")
        sys.exit(1)