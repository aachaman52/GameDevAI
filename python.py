"""
GameDev AI Assistant - Complete Edition
Main Entry Point - All Phases Integrated
Version: 1.0.0 FINAL
"""

import sys
import json
import logging
from pathlib import Path

def init_logging():
    """Setup application logging"""
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/app.log'),
            logging.StreamHandler()
        ]
    )

def init_directories():
    """Create all necessary directories"""
    dirs = [
        'data', 'logs', 'backups',
        'ai_core/prompt_templates',
        'gui/assets',
        'connectors',
        'tools'
    ]
    
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
    
    logging.info("Directory structure initialized")

def init_config():
    """Initialize configuration file with defaults"""
    config_path = Path('config.json')
    
    if not config_path.exists():
        default_config = {
            "app_name": "GameDev AI Assistant",
            "version": "1.0.0",
            "ai_model": "llama3.2:3b",
            "unity_project_path": "",
            "godot_project_path": "",
            "unreal_project_path": "",
            "current_engine": "unity",
            "max_chat_history": 100,
            "theme": "dark",
            "auto_backup": True,
            "asset_search_enabled": True,
            "memory_enabled": True
        }
        
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        logging.info("Default configuration created")

def check_first_run():
    """Detect first run and perform initial setup"""
    specs_file = Path('data/system_specs.json')
    
    if not specs_file.exists():
        logging.info("First run - detecting hardware")
        print("🔍 Detecting system hardware...")
        
        try:
            from tools.check_specs import SpecsChecker
            checker = SpecsChecker()
            checker.detect_all()
            checker.save_report()
            logging.info("Hardware detection complete")
        except Exception as e:
            logging.error(f"Hardware detection failed: {e}")

def main():
    """Main application entry point"""
    print("=" * 60)
    print("  🎮 GameDev AI Assistant - Complete Edition")
    print("  Version 1.0.0 - All Phases Integrated")
    print("=" * 60)
    print()
    
    init_logging()
    logging.info("Starting GameDev AI Assistant v1.0.0")
    
    init_directories()
    init_config()
    check_first_run()
    
    try:
        from gui.chat_window import ChatWindow
        
        logging.info("Launching GUI")
        print("✅ All systems ready!")
        print("🚀 Launching application...\n")
        
        app = ChatWindow()
        app.run()
        
    except ImportError as e:
        logging.error(f"Import error: {e}")
        print(f"❌ Error: {e}")
        print("\nPlease ensure all files are present and run:")
        print("  python setup.py")
        sys.exit(1)
    
    except Exception as e:
        logging.error(f"Application error: {e}", exc_info=True)
        print(f"❌ Error: {e}")
        sys.exit(1)
    
    logging.info("Application closed")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)