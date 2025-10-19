"""
Unreal Connector - Unreal Engine project integration
Handles C++ class creation and project management
"""

import os
from pathlib import Path
import json
from datetime import datetime

class UnrealConnector:
    def __init__(self, project_path):
        self.project_path = Path(project_path)
        
        uproject_files = list(self.project_path.glob('*.uproject'))
        if not uproject_files:
            raise ValueError(f"Not a valid Unreal project: {project_path}")
        
        self.project_file = uproject_files[0]
        self.project_name = self.project_file.stem
        
        self.source_path = self.project_path / "Source" / self.project_name
        self.content_path = self.project_path / "Content"
        
        self.source_path.mkdir(parents=True, exist_ok=True)
        self.log_file = Path('logs/unreal_actions.json')
        self.log_file.parent.mkdir(exist_ok=True)
    
    def get_project_structure(self):
        structure = {
            "project_name": self.project_name,
            "cpp_classes": [],
            "blueprints": [],
            "maps": []
        }
        
        if self.source_path.exists():
            for root, dirs, files in os.walk(self.source_path):
                rel_path = Path(root).relative_to(self.source_path)
                for file in files:
                    if file.endswith(('.h', '.cpp')):
                        structure["cpp_classes"].append(str(rel_path / file))
        
        if self.content_path.exists():
            for root, dirs, files in os.walk(self.content_path):
                for file in files:
                    if file.endswith('.uasset'):
                        if 'Blueprint' in file:
                            structure["blueprints"].append(file)
                        elif 'Map' in file or 'Level' in file:
                            structure["maps"].append(file)
        
        return structure
    
    def create_cpp_class(self, class_name, header_content, source_content):
        header_path = self.source_path / f"{class_name}.h"
        source_path = self.source_path / f"{class_name}.cpp"
        
        try:
            if header_path.exists():
                backup = header_path.with_suffix('.h.bak')
                header_path.rename(backup)
            header_path.write_text(header_content, encoding='utf-8')
            
            if source_path.exists():
                backup = source_path.with_suffix('.cpp.bak')
                source_path.rename(backup)
            source_path.write_text(source_content, encoding='utf-8')
            
            self.log_action('create', f"{class_name}.h/.cpp", "C++ class created")
            
            return {
                "success": True,
                "header": str(header_path.relative_to(self.project_path)),
                "source": str(source_path.relative_to(self.project_path)),
                "message": f"C++ class created: {class_name}"
            }
        
        except Exception as e:
            self.log_action('error', class_name, str(e))
            return {"success": False, "error": str(e)}
    
    def list_cpp_classes(self):
        classes = []
        
        if self.source_path.exists():
            for root, dirs, files in os.walk(self.source_path):
                for file in files:
                    if file.endswith('.h'):
                        full_path = Path(root) / file
                        rel_path = full_path.relative_to(self.source_path)
                        classes.append({
                            "name": file,
                            "path": str(rel_path),
                            "size": full_path.stat().st_size,
                            "modified": datetime.fromtimestamp(
                                full_path.stat().st_mtime
                            ).strftime("%Y-%m-%d %H:%M")
                        })
        
        return classes
    
    def log_action(self, action_type, target, details):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action_type,
            "target": target,
            "details": details
        }
        
        if self.log_file.exists():
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
        else:
            logs = []
        
        logs.append(log_entry)
        
        with open(self.log_file, 'w') as f:
            json.dump(logs[-500:], f, indent=2)