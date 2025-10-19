"""
Project Memory System - Tracks project context
Phase 5 implementation
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class ProjectMemory:
    def __init__(self, memory_file='data/project_memory.json'):
        self.memory_file = Path(memory_file)
        self.memory_file.parent.mkdir(exist_ok=True)
        self.memory = self._load_memory()
    
    def _load_memory(self) -> Dict:
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
            except:
                return self._create_empty_memory()
        return self._create_empty_memory()
    
    def _create_empty_memory(self) -> Dict:
        return {
            'project_info': {
                'name': '',
                'genre': '',
                'description': '',
                'engine': '',
                'created': datetime.now().isoformat()
            },
            'scripts': [],
            'assets': [],
            'todos': [],
            'completed_tasks': [],
            'user_preferences': {
                'coding_style': 'standard',
                'naming_convention': 'PascalCase'
            },
            'last_updated': datetime.now().isoformat()
        }
    
    def _save_memory(self):
        self.memory['last_updated'] = datetime.now().isoformat()
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=2)
    
    def set_project_info(self, name=None, genre=None, engine=None):
        if name:
            self.memory['project_info']['name'] = name
        if genre:
            self.memory['project_info']['genre'] = genre
        if engine:
            self.memory['project_info']['engine'] = engine
        self._save_memory()
    
    def get_project_info(self) -> Dict:
        return self.memory['project_info']
    
    def add_script(self, script_name: str, purpose: str, features: List[str] = None):
        existing = self.get_script(script_name)
        if existing:
            existing['purpose'] = purpose
            existing['features'] = features or existing['features']
            existing['last_modified'] = datetime.now().isoformat()
        else:
            script = {
                'name': script_name,
                'purpose': purpose,
                'features': features or [],
                'created': datetime.now().isoformat(),
                'last_modified': datetime.now().isoformat()
            }
            self.memory['scripts'].append(script)
        
        self._save_memory()
    
    def get_script(self, script_name: str) -> Optional[Dict]:
        for script in self.memory['scripts']:
            if script['name'] == script_name:
                return script
        return None
    
    def list_scripts(self) -> List[Dict]:
        return self.memory['scripts']
    
    def add_todo(self, task: str, priority: str = 'medium'):
        todo = {
            'task': task,
            'priority': priority,
            'added': datetime.now().isoformat(),
            'completed': False
        }
        self.memory['todos'].append(todo)
        self._save_memory()
    
    def list_todos(self) -> List[Dict]:
        return self.memory['todos']
    
    def build_context_summary(self) -> str:
        project = self.memory['project_info']
        scripts = self.memory['scripts']
        todos = self.memory['todos']
        
        context = f"""PROJECT CONTEXT:
- Name: {project.get('name', 'Unnamed')}
- Engine: {project.get('engine', 'N/A')}

SCRIPTS ({len(scripts)}):
"""
        for script in scripts[-5:]:
            context += f"  - {script['name']}: {script['purpose']}\n"
        
        if todos:
            context += f"\nTODOs ({len(todos)}):\n"
            for todo in todos[:3]:
                context += f"  - [{todo['priority']}] {todo['task']}\n"
        
        return context
    
    def get_stats(self) -> Dict:
        return {
            'total_scripts': len(self.memory['scripts']),
            'total_assets': len(self.memory['assets']),
            'pending_todos': len(self.memory['todos']),
            'completed_tasks': len(self.memory['completed_tasks']),
            'days_active': self._calculate_days_active(),
            'last_updated': self.memory['last_updated']
        }
    
    def _calculate_days_active(self) -> int:
        created = datetime.fromisoformat(self.memory['project_info']['created'])
        now = datetime.now()
        return (now - created).days
    
    def clear_memory(self):
        self.memory = self._create_empty_memory()
        self._save_memory()
    
    def search_scripts(self, query: str) -> List[Dict]:
        query = query.lower()
        results = []
        
        for script in self.memory['scripts']:
            if (query in script['name'].lower() or 
                query in script['purpose'].lower()):
                results.append(script)
        
        return results