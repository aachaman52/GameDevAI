"""
Action Logger - Tracks all operations
Full audit trail
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

class ActionLogger:
    def __init__(self, log_dir='logs'):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.action_log_file = self.log_dir / 'actions.json'
    
    def log_action(self, action_type: str, details: Dict, status: str = 'success'):
        entry = {
            'timestamp': datetime.now().isoformat(),
            'type': action_type,
            'status': status,
            'details': details
        }
        
        logs = self._load_logs()
        logs.append(entry)
        self._save_logs(logs[-1000:])
    
    def log_script_created(self, script_name: str, path: str, size: int):
        self.log_action('script_created', {
            'script_name': script_name,
            'path': path,
            'size_bytes': size
        })
    
    def log_script_modified(self, script_name: str, path: str, backup_path: str):
        self.log_action('script_modified', {
            'script_name': script_name,
            'path': path,
            'backup': backup_path
        })
    
    def log_ai_request(self, prompt: str, response_time: float):
        self.log_action('ai_request', {
            'prompt_length': len(prompt),
            'response_time_seconds': round(response_time, 2)
        })
    
    def log_ai_error(self, error_message: str, prompt: str):
        self.log_action('ai_error', {
            'error': error_message,
            'prompt': prompt[:100]
        }, status='failure')
    
    def log_project_opened(self, project_path: str, project_type: str):
        self.log_action('project_opened', {
            'path': project_path,
            'type': project_type
        })
    
    def get_recent_logs(self, limit: int = 50) -> List[Dict]:
        logs = self._load_logs()
        return logs[-limit:]
    
    def get_stats(self) -> Dict:
        logs = self._load_logs()
        
        stats = {
            'total_actions': len(logs),
            'scripts_created': 0,
            'scripts_modified': 0,
            'ai_requests': 0,
            'errors': 0,
            'warnings': 0
        }
        
        for log in logs:
            if log['type'] == 'script_created':
                stats['scripts_created'] += 1
            elif log['type'] == 'script_modified':
                stats['scripts_modified'] += 1
            elif log['type'] == 'ai_request':
                stats['ai_requests'] += 1
            
            if log['status'] == 'failure':
                stats['errors'] += 1
            elif log['status'] == 'warning':
                stats['warnings'] += 1
        
        return stats
    
    def _load_logs(self) -> List[Dict]:
        if not self.action_log_file.exists():
            return []
        
        try:
            with open(self.action_log_file, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def _save_logs(self, logs: List[Dict]):
        try:
            with open(self.action_log_file, 'w') as f:
                json.dump(logs, f, indent=2)
        except Exception as e:
            print(f"Failed to save logs: {e}")

_logger_instance = None

def get_logger() -> ActionLogger:
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = ActionLogger()
    return _logger_instance