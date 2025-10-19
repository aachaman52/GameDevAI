"""
GameDev AI Assistant - Automated Setup
Version: 1.0.0 FINAL
"""

import os
import sys
import subprocess
from pathlib import Path
import json

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")

def check_python():
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required. You have {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def create_dirs():
    print("📁 Creating directories...")
    dirs = ['data', 'logs', 'backups', 'ai_core/prompt_templates', 
            'gui/assets', 'connectors', 'tools']
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {d}/")
    return True

def create_inits():
    print("📝 Creating __init__.py files...")
    inits = {
        'gui/__init__.py': 'from .chat_window import ChatWindow\n__all__ = ["ChatWindow"]',
        'ai_core/__init__.py': 'from .model_interface import AIModel\nfrom .memory import ProjectMemory\n__all__ = ["AIModel", "ProjectMemory"]',
        'connectors/__init__.py': 'from .unity_connector import UnityConnector\nfrom .godot_connector import GodotConnector\nfrom .unreal_connector import UnrealConnector\n__all__ = ["UnityConnector", "GodotConnector", "UnrealConnector"]',
        'tools/__init__.py': 'from .check_specs import SpecsChecker\nfrom .file_manager import FileManager\nfrom .logger import ActionLogger, get_logger\nfrom .search_assets import AssetSearcher\n__all__ = ["SpecsChecker", "FileManager", "ActionLogger", "get_logger", "AssetSearcher"]'
    }
    for path, content in inits.items():
        Path(path).write_text(content)
        print(f"   ✅ {path}")
    return True

def install_deps():
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Dependencies installed")
        return True
    except:
        print("⚠️  Dependency installation failed")
        return False

def check_ollama():
    print("🤖 Checking Ollama...")
    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True, timeout=5)
        if result.returncode == 0:
            print("✅ Ollama found")
            return True
    except:
        pass
    print("⚠️  Ollama not found")
    return False

def main():
    print_header("GameDev AI Assistant Setup")
    
    if not check_python():
        return False
    
    create_dirs()
    create_inits()
    install_deps()
    
    ollama_ok = check_ollama()
    
    print_header("Setup Complete!")
    print("✅ Project structure ready")
    print("✅ Dependencies installed")
    
    if ollama_ok:
        print("✅ Ollama ready")
    else:
        print("⚠️  Install Ollama from: https://ollama.ai")
        print("   Then run: ollama pull llama3.2:3b")
    
    print("\n🚀 Start with: python main.py\n")
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Setup cancelled")
        sys.exit(1)