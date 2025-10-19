"""
Unity Connector - Unity project integration
Handles C# script creation and project management
"""

import os
from pathlib import Path
import json
from datetime import datetime

class UnityConnector:
    def __init__(self, project_path):
        self.project_path = Path(project_path)
        self.assets_path = self.project_path / "Assets"
        self.scripts_path = self.assets_path / "Scripts"
        
        if not self.assets_path.exists():
            raise ValueError(f"Not a valid Unity project: {project_path}")
        
        self.scripts_path.mkdir(exist_ok=True)
        self.log_file = Path('logs/unity_actions.json')
        self.log_file.parent.mkdir(exist_ok=True)
    
    def get_project_structure(self):
        structure = {
            "project_name": self.project_path.name,
            "assets_folders": [],
            "scripts": [],
            "scenes": [],
            "prefabs": []
        }
        
        # CONTINUATION OF unity_connector.py
        
        for root, dirs, files in os.walk(self.assets_path):
            rel_path = Path(root).relative_to(self.assets_path)
            
            if rel_path != Path('.'):
                structure["assets_folders"].append(str(rel_path))
            
            for file in files:
                if file.endswith('.cs'):
                    structure["scripts"].append(str(rel_path / file))
                elif file.endswith('.unity'):
                    structure["scenes"].append(str(rel_path / file))
                elif file.endswith('.prefab'):
                    structure["prefabs"].append(str(rel_path / file))
        
        return structure
    
    def create_script(self, script_name, code_content, subfolder=""):
        if not script_name.endswith('.cs'):
            script_name += '.cs'
        
        if subfolder:
            target_folder = self.scripts_path / subfolder
            target_folder.mkdir(parents=True, exist_ok=True)
        else:
            target_folder = self.scripts_path
        
        script_path = target_folder / script_name
        
        if script_path.exists():
            backup_path = script_path.with_suffix('.cs.bak')
            script_path.rename(backup_path)
            self.log_action('backup', str(script_path), f"Backed up to {backup_path}")
        
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
        for root, dirs, files in os.walk(self.assets_path):
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
        for root, dirs, files in os.walk(self.assets_path):
            for file in files:
                if file.endswith('.cs'):
                    full_path = Path(root) / file
                    rel_path = full_path.relative_to(self.assets_path)
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