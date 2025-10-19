"""
File Manager - Safe file operations with backup and validation
Handles reading, writing, and managing game project files
"""

import os
import shutil
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime
import json

class FileManager:
    """Manages file operations with safety features"""
    
    def __init__(self, project_root: Optional[str] = None):
        self.project_root = Path(project_root) if project_root else None
        self.backup_dir = Path('backups')
        self.backup_dir.mkdir(exist_ok=True)
    
    def read_file(self, file_path: str, encoding: str = 'utf-8') -> Dict:
        """
        Safely read a file
        
        Returns:
            Dict with 'success', 'content', and 'error' keys
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return {
                    'success': False,
                    'error': f'File not found: {file_path}'
                }
            
            content = path.read_text(encoding=encoding)
            return {
                'success': True,
                'content': content,
                'size': path.stat().st_size,
                'modified': datetime.fromtimestamp(path.stat().st_mtime).isoformat()
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def write_file(self, file_path: str, content: str, 
                   create_backup: bool = True, encoding: str = 'utf-8') -> Dict:
        """
        Safely write to a file with optional backup
        
        Returns:
            Dict with operation results
        """
        try:
            path = Path(file_path)
            
            # Create backup if file exists
            if create_backup and path.exists():
                backup_result = self.create_backup(file_path)
                if not backup_result['success']:
                    return backup_result
            
            # Create parent directories if needed
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            path.write_text(content, encoding=encoding)
            
            return {
                'success': True,
                'path': str(path),
                'size': len(content),
                'backup': backup_result.get('backup_path') if create_backup and path.exists() else None
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_backup(self, file_path: str) -> Dict:
        """
        Create a backup of a file
        
        Returns:
            Dict with backup path and status
        """
        try:
            source = Path(file_path)
            if not source.exists():
                return {
                    'success': False,
                    'error': f'File not found: {file_path}'
                }
            
            # Generate backup filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"{source.stem}_{timestamp}{source.suffix}.bak"
            backup_path = self.backup_dir / backup_name
            
            # Copy file
            shutil.copy2(source, backup_path)
            
            return {
                'success': True,
                'backup_path': str(backup_path),
                'original_size': source.stat().st_size
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def restore_backup(self, backup_path: str, target_path: str) -> Dict:
        """Restore a file from backup"""
        try:
            backup = Path(backup_path)
            target = Path(target_path)
            
            if not backup.exists():
                return {
                    'success': False,
                    'error': f'Backup not found: {backup_path}'
                }
            
            # Create backup of current file if it exists
            if target.exists():
                current_backup = self.create_backup(target_path)
            
            # Restore
            shutil.copy2(backup, target)
            
            return {
                'success': True,
                'restored_to': str(target)
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def list_backups(self, file_name: Optional[str] = None) -> List[Dict]:
        """List all backups, optionally filtered by filename"""
        backups = []
        
        for backup_file in self.backup_dir.glob('*.bak'):
            # Parse backup filename
            # Format: filename_YYYYMMDD_HHMMSS.ext.bak
            
            if file_name and not backup_file.stem.startswith(file_name.split('.')[0]):
                continue
            
            backups.append({
                'path': str(backup_file),
                'name': backup_file.name,
                'size': backup_file.stat().st_size,
                'created': datetime.fromtimestamp(backup_file.stat().st_mtime).isoformat()
            })
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x['created'], reverse=True)
        return backups
    
    def delete_file(self, file_path: str, create_backup: bool = True) -> Dict:
        """Safely delete a file with optional backup"""
        try:
            path = Path(file_path)
            
            if not path.exists():
                return {
                    'success': False,
                    'error': f'File not found: {file_path}'
                }
            
            # Create backup before deletion
            backup_result = None
            if create_backup:
                backup_result = self.create_backup(file_path)
            
            # Delete
            path.unlink()
            
            return {
                'success': True,
                'deleted': str(path),
                'backup': backup_result.get('backup_path') if backup_result else None
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def validate_csharp(self, code: str) -> Dict:
        """
        Basic validation of C# code syntax
        
        Returns:
            Dict with validation results
        """
        issues = []
        
        # Check basic syntax
        if code.count('{') != code.count('}'):
            issues.append('Mismatched curly braces')
        
        if code.count('(') != code.count(')'):
            issues.append('Mismatched parentheses')
        
        if code.count('[') != code.count(']'):
            issues.append('Mismatched square brackets')
        
        # Check for required elements in Unity script
        if 'MonoBehaviour' in code or 'ScriptableObject' in code:
            if 'using UnityEngine;' not in code:
                issues.append('Missing "using UnityEngine;" statement')
        
        # Check class declaration
        if 'class ' in code:
            # Extract class name
            import re
            class_match = re.search(r'class\s+(\w+)', code)
            if not class_match:
                issues.append('Invalid class declaration')
        else:
            issues.append('No class declaration found')
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': self._get_code_warnings(code)
        }
    
    def _get_code_warnings(self, code: str) -> List[str]:
        """Get non-critical warnings about code"""
        warnings = []
        
        # Check for common issues
        if 'Debug.Log' in code:
            if code.count('Debug.Log') > 5:
                warnings.append('Many Debug.Log statements (consider removing for production)')
        
        if 'FindObjectOfType' in code or 'GameObject.Find' in code:
            warnings.append('Using Find methods can be slow (consider caching references)')
        
        if code.count('\t') > 0:
            warnings.append('Code contains tabs (Unity prefers spaces)')
        
        return warnings
    
    def scan_directory(self, directory: str, extensions: List[str] = None) -> List[Dict]:
        """
        Scan directory for files
        
        Args:
            directory: Path to scan
            extensions: List of extensions to filter (e.g., ['.cs', '.txt'])
        
        Returns:
            List of file info dicts
        """
        dir_path = Path(directory)
        if not dir_path.exists():
            return []
        
        files = []
        for file_path in dir_path.rglob('*'):
            if not file_path.is_file():
                continue
            
            # Filter by extension if specified
            if extensions and file_path.suffix not in extensions:
                continue
            
            files.append({
                'name': file_path.name,
                'path': str(file_path),
                'relative_path': str(file_path.relative_to(dir_path)),
                'size': file_path.stat().st_size,
                'extension': file_path.suffix,
                'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            })
        
        return files
    
    def get_file_info(self, file_path: str) -> Dict:
        """Get detailed information about a file"""
        try:
            path = Path(file_path)
            
            if not path.exists():
                return {
                    'exists': False,
                    'error': 'File not found'
                }
            
            stat = path.stat()
            
            return {
                'exists': True,
                'name': path.name,
                'path': str(path.absolute()),
                'size': stat.st_size,
                'size_readable': self._format_size(stat.st_size),
                'extension': path.suffix,
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'is_readonly': not os.access(path, os.W_OK)
            }
        
        except Exception as e:
            return {
                'exists': False,
                'error': str(e)
            }
    
    def _format_size(self, size_bytes: int) -> str:
        """Format byte size to human-readable string"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
    
    def clean_old_backups(self, days: int = 30) -> Dict:
        """Remove backups older than N days"""
        from datetime import timedelta
        
        cutoff = datetime.now() - timedelta(days=days)
        deleted_count = 0
        deleted_size = 0
        
        for backup_file in self.backup_dir.glob('*.bak'):
            modified_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
            
            if modified_time < cutoff:
                deleted_size += backup_file.stat().st_size
                backup_file.unlink()
                deleted_count += 1
        
        return {
            'deleted_count': deleted_count,
            'freed_space': self._format_size(deleted_size)
        }
    
    def copy_file(self, source: str, destination: str) -> Dict:
        """Copy a file to new location"""
        try:
            src = Path(source)
            dst = Path(destination)
            
            if not src.exists():
                return {
                    'success': False,
                    'error': f'Source file not found: {source}'
                }
            
            # Create destination directory if needed
            dst.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy
            shutil.copy2(src, dst)
            
            return {
                'success': True,
                'source': str(src),
                'destination': str(dst),
                'size': dst.stat().st_size
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def move_file(self, source: str, destination: str) -> Dict:
        """Move a file to new location"""
        try:
            src = Path(source)
            dst = Path(destination)
            
            if not src.exists():
                return {
                    'success': False,
                    'error': f'Source file not found: {source}'
                }
            
            # Create destination directory if needed
            dst.parent.mkdir(parents=True, exist_ok=True)
            
            # Move
            shutil.move(str(src), str(dst))
            
            return {
                'success': True,
                'from': str(src),
                'to': str(dst)
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }