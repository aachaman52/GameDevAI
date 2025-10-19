"""
File Manager - Safe file operations
Handles reading, writing with backup
"""

import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict

class FileManager:
    def __init__(self, project_root=None):
        self.project_root = Path(project_root) if project_root else None
        self.backup_dir = Path('backups')
        self.backup_dir.mkdir(exist_ok=True)
    
    def read_file(self, file_path: str) -> Dict:
        try:
            path = Path(file_path)
            if not path.exists():
                return {'success': False, 'error': f'File not found: {file_path}'}
            
            content = path.read_text(encoding='utf-8')
            return {
                'success': True,
                'content': content,
                'size': path.stat().st_size
            }
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def write_file(self, file_path: str, content: str, create_backup: bool = True) -> Dict:
        try:
            path = Path(file_path)
            
            if create_backup and path.exists():
                backup_result = self.create_backup(file_path)
                if not backup_result['success']:
                    return backup_result
            
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')
            
            return {
                'success': True,
                'path': str(path),
                'size': len(content)
            }
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_backup(self, file_path: str) -> Dict:
        try:
            source = Path(file_path)
            if not source.exists():
                return {'success': False, 'error': 'File not found'}
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"{source.stem}_{timestamp}{source.suffix}.bak"
            backup_path = self.backup_dir / backup_name
            
            shutil.copy2(source, backup_path)
            
            return {
                'success': True,
                'backup_path': str(backup_path)
            }
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def list_backups(self, file_name=None):
        backups = []
        
        for backup_file in self.backup_dir.glob('*.bak'):
            if file_name and not backup_file.stem.startswith(file_name.split('.')[0]):
                continue
            
            backups.append({
                'path': str(backup_file),
                'name': backup_file.name,
                'size': backup_file.stat().st_size,
                'created': datetime.fromtimestamp(backup_file.stat().st_mtime).isoformat()
            })
        
        backups.sort(key=lambda x: x['created'], reverse=True)
        return backups