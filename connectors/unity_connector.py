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
        
        for root, dirs, files in os.walk(self.assets_path):
            rel_root = Path(root).relative_to(self.assets_path)
            for d in dirs:
                structure["assets_folders"].append(str(rel_root / d))
            for f in files:
                if f.endswith('.cs'):
                    structure["scripts"].append(str(rel_root / f))
                elif f.endswith('.unity'):
                    structure["scenes"].append(str(rel_root / f))
                elif f.endswith('.prefab'):
                    structure["prefabs"].append(str(rel_root / f))