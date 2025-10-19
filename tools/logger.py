"""
Centralized Logger - Tracks all AI actions and file operations
Used across the entire application for audit trails
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class ActionLogger:
    """Logs all important actions for debugging and audit"""
    
    def __init__(self, log_dir='logs'):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Main action log file
        self.action_log_file = self.log_dir / 'actions.json'
        self.error_log_file = self.log_dir / 'errors.log'
        
        # Setup Python logging for errors
        logging.basicConfig(
            filename=str(self.error_log_file),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def log_action(self, action_type: str, details: Dict, status: str = 'success'):
        """
        Log any action taken by the application
        
        Args:
            action_type: Type of action (e.g., 'script_created', 'ai_response', 'project_opened')
            details: Dictionary with action details
            status: 'success', 'failure', 'warning'
        """
        entry = {
            'timestamp': datetime.now().isoformat(),
            'type': action_type,
            'status': status,
            'details': details
        }
        
        # Load existing logs
        logs = self._load_logs()
        logs.append(entry)
        
        # Save (keep last 1000 entries)
        self._save_logs(logs[-1000:])
        
        # Also log to Python logger if error
        if status == 'failure':
            self.logger.error(f"{action_type}: {details}")
        elif status == 'warning':
            self.logger.warning(f"{action_type}: {details}")
    
    def log_script_created(self, script_name: str, path: str, size: int):
        """Log script creation"""
        self.log_action('script_created', {
            'script_name': script_name,
            'path': path,
            'size_bytes': size
        })
    
    def log_script_modified(self, script_name: str, path: str, backup_path: str):
        """Log script modification"""
        self.log_action('script_modified', {
            'script_name': script_name,
            'path': path,
            'backup': backup_path
        })
    
    def log_script_deleted(self, script_name: str, path: str):
        """Log script deletion"""
        self.log_action('script_deleted', {
            'script_name': script_name,
            'path': path
        }, status='warning')
    
    def log_ai_request(self, prompt: str, response_time: float):
        """Log AI interaction"""
        self.log_action('ai_request', {
            'prompt_length': len(prompt),
            'response_time_seconds': round(response_time, 2)
        })
    
    def log_ai_error(self, error_message: str, prompt: str):
        """Log AI error"""
        self.log_action('ai_error', {
            'error': error_message,
            'prompt': prompt[:100] + '...' if len(prompt) > 100 else prompt
        }, status='failure')
    
    def log_project_opened(self, project_path: str, project_type: str):
        """Log project opening"""
        self.log_action('project_opened', {
            'path': project_path,
            'type': project_type
        })
    
    def log_error(self, error_type: str, error_message: str, context: Optional[Dict] = None):
        """Log general error"""
        details = {
            'error_type': error_type,
            'message': error_message
        }
        if context:
            details['context'] = context
        
        self.log_action('error', details, status='failure')
    
    def get_recent_logs(self, limit: int = 50, action_type: Optional[str] = None) -> List[Dict]:
        """
        Retrieve recent logs
        
        Args:
            limit: Number of logs to return
            action_type: Filter by specific action type
        """
        logs = self._load_logs()
        
        # Filter by type if specified
        if action_type:
            logs = [log for log in logs if log['type'] == action_type]
        
        return logs[-limit:]
    
    def get_logs_by_date(self, date_str: str) -> List[Dict]:
        """Get all logs from a specific date (YYYY-MM-DD)"""
        logs = self._load_logs()
        return [log for log in logs if log['timestamp'].startswith(date_str)]
    
    def get_error_count(self, hours: int = 24) -> int:
        """Count errors in last N hours"""
        from datetime import timedelta
        
        cutoff = datetime.now() - timedelta(hours=hours)
        logs = self._load_logs()
        
        error_count = 0
        for log in logs:
            log_time = datetime.fromisoformat(log['timestamp'])
            if log_time >= cutoff and log['status'] == 'failure':
                error_count += 1
        
        return error_count
    
    def get_stats(self) -> Dict:
        """Get usage statistics"""
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
    
    def clear_old_logs(self, days: int = 30):
        """Remove logs older than N days"""
        from datetime import timedelta
        
        cutoff = datetime.now() - timedelta(days=days)
        logs = self._load_logs()
        
        filtered_logs = []
        for log in logs:
            log_time = datetime.fromisoformat(log['timestamp'])
            if log_time >= cutoff:
                filtered_logs.append(log)
        
        self._save_logs(filtered_logs)
        return len(logs) - len(filtered_logs)  # Number deleted
    
    def export_logs(self, output_file: str):
        """Export logs to a file"""
        logs = self._load_logs()
        output_path = Path(output_file)
        
        with open(output_path, 'w') as f:
            json.dump(logs, f, indent=2)
        
        return len(logs)
    
    def _load_logs(self) -> List[Dict]:
        """Load logs from file"""
        if not self.action_log_file.exists():
            return []
        
        try:
            with open(self.action_log_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            self.logger.error("Failed to load action logs")
            return []
    
    def _save_logs(self, logs: List[Dict]):
        """Save logs to file"""
        try:
            with open(self.action_log_file, 'w') as f:
                json.dump(logs, f, indent=2)
        except IOError as e:
            self.logger.error(f"Failed to save logs: {e}")

# Global logger instance
_logger_instance = None

def get_logger() -> ActionLogger:
    """Get global logger instance"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = ActionLogger()
    return _logger_instance