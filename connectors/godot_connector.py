"""
Godot Connector - Godot project integration
Handles GDScript creation and project management
"""

import os
from pathlib import Path
import json
from datetime import datetime

class GodotConnector:
    def __init__(self, project_path):
        self.project_path = Path(project_path)
        self.project_file = self.project_path / "project.godot"
        self.scripts_path = self.project_path / "scripts"
        
        if not self.project_file.exists():
            raise ValueError(f"Not a valid Godot project: {project_path}")
        
        self.scripts_path.mkdir(exist_ok=True)
        self.log_file = Path('logs/godot_actions.json')
        self.log_file.parent.mkdir(exist_ok=True)
    
    def get_project_structure(self):
        structure = {
            "project_name": self.project_path.name,
            "scripts": [],
            "scenes": [],
            "resources": []
        }
        
        for root, dirs, files in os.walk(self.project_path):
            rel_path = Path(root).relative_to(self.project_path)
            
            for file in files:
                if file.endswith('.gd'):
                    structure["scripts"].append(str(rel_path / file))
                elif file.endswith('.tscn'):
                    structure["scenes"].append(str(rel_path / file))
                elif file.endswith('.tres'):
                    structure["resources"].append(str(rel_path / file))
        
        return structure
    
    def create_script(self, script_name, code_content, subfolder=""):
        if not script_name.endswith('.gd'):
            script_name += '.gd'
        
        if subfolder:
            target_folder = self.scripts_path / subfolder
            target_folder.mkdir(parents=True, exist_ok=True)
        else:
            target_folder = self.scripts_path
        
        script_path = target_folder / script_name
        
        if script_path.exists():
            backup_path = script_path.with_suffix('.gd.bak')
            script_path.rename(backup_path)
            self.log_action('backup', str(script_path), f"Backed up")
        
        try:
            script_path.write_text(code_content, encoding='utf-8')
            self.log_action('create', str(script_path), "Script created")
            return {
                "success": True,
                "path": str(script_path.relative_to(self.project_path)),
                "message": f"Script created: {script_name}"
            }
        except Exception as e:
            self.log_action('error', str(script_path), str(e))
            return {"success": False, "error": str(e)}
    
    def read_script(self, script_name):
        for root, dirs, files in os.walk(self.project_path):
            if script_name in files:
                script_path = Path(root) / script_name
                return {
                    "success": True,
                    "content": script_path.read_text(encoding='utf-8'),
                    "path": str(script_path.relative_to(self.project_path))
                }
        
        return {"success": False, "error": f"Script not found: {script_name}"}
    
    def list_scripts(self):
        scripts = []
        for root, dirs, files in os.walk(self.project_path):
            for file in files:
                if file.endswith('.gd'):
                    full_path = Path(root) / file
                    rel_path = full_path.relative_to(self.project_path)
                    scripts.append({
                        "name": file,
                        "path": str(rel_path),
                        "size": full_path.stat().st_size,
                        "modified": datetime.fromtimestamp(
                            full_path.stat().st_mtime
                        ).strftime("%Y-%m-%d %H:%M")
                    })
        
        return scripts
    
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