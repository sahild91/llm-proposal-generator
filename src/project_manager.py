"""
Project Manager for handling file operations and project structure
"""

import os
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import shutil

class ProjectManager:
    """Manages project files, folders, and database operations"""
    
    def __init__(self, projects_dir: Path, db_path: Path):
        self.projects_dir = Path(projects_dir)
        self.db_path = Path(db_path)
        self.projects_dir.mkdir(exist_ok=True)
    
    def create_project(self, project_data: Dict[str, Any]) -> bool:
        """Create a new project with folder structure"""
        try:
            project_name = project_data['project_name']
            safe_name = self._sanitize_filename(project_name)
            
            # Create project directory structure
            project_dir = self.projects_dir / safe_name
            if project_dir.exists():
                raise ValueError(f"Project '{project_name}' already exists")
            
            # Create folder structure
            project_dir.mkdir(parents=True)
            (project_dir / "Proposal").mkdir()
            (project_dir / "Feasibility").mkdir()
            (project_dir / "Assets").mkdir()
            
            # Create project metadata file
            metadata = {
                'project_name': project_name,
                'client_name': project_data.get('client_name', ''),
                'project_type': project_data.get('project_type', ''),
                'description': project_data.get('requirements', ''),
                'created_date': datetime.now().isoformat(),
                'modified_date': datetime.now().isoformat(),
                'hardware_components': project_data.get('hardware_components', []),
                'software_modules': project_data.get('software_modules', []),
                'expected_duration': project_data.get('expected_duration', ''),
                'status': 'draft'
            }
            
            with open(project_dir / "project_metadata.json", 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            # Save to database
            self._save_project_to_db(metadata, safe_name)
            
            return True
            
        except Exception as e:
            print(f"Error creating project: {e}")
            return False
    
    def save_document(self, project_name: str, doc_type: str, content: str, changelog: str = "") -> bool:
        """Save document content to file and create version"""
        try:
            safe_name = self._sanitize_filename(project_name)
            project_dir = self.projects_dir / safe_name
            
            if not project_dir.exists():
                raise ValueError(f"Project '{project_name}' does not exist")
            
            # Determine file path based on document type
            if doc_type == "proposal":
                file_path = project_dir / "Proposal" / "proposal.md"
            elif doc_type == "feasibility":
                file_path = project_dir / "Feasibility" / "feasibility.md"
            else:
                file_path = project_dir / f"{doc_type}.md"
            
            # Save current content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Update project modified date
            self._update_project_modified_date(safe_name)
            
            # Save version to database
            self._save_document_version(safe_name, doc_type, content, changelog)
            
            return True
            
        except Exception as e:
            print(f"Error saving document: {e}")
            return False
    
    def load_document(self, project_name: str, doc_type: str) -> Optional[str]:
        """Load document content from file"""
        try:
            safe_name = self._sanitize_filename(project_name)
            project_dir = self.projects_dir / safe_name
            
            if doc_type == "proposal":
                file_path = project_dir / "Proposal" / "proposal.md"
            elif doc_type == "feasibility":
                file_path = project_dir / "Feasibility" / "feasibility.md"
            else:
                file_path = project_dir / f"{doc_type}.md"
            
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            return None
            
        except Exception as e:
            print(f"Error loading document: {e}")
            return None
    
    def get_project_list(self) -> List[Dict[str, Any]]:
        """Get list of all projects"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT name, client_name, project_type, description, 
                       created_date, modified_date, status
                FROM projects 
                ORDER BY modified_date DESC
            """)
            
            projects = []
            for row in cursor.fetchall():
                projects.append({
                    'name': row[0],
                    'client_name': row[1],
                    'project_type': row[2],
                    'description': row[3],
                    'created_date': row[4],
                    'modified_date': row[5],
                    'status': row[6]
                })
            
            conn.close()
            return projects
            
        except Exception as e:
            print(f"Error getting project list: {e}")
            return []
    
    def get_project_metadata(self, project_name: str) -> Optional[Dict[str, Any]]:
        """Get project metadata"""
        try:
            safe_name = self._sanitize_filename(project_name)
            project_dir = self.projects_dir / safe_name
            metadata_file = project_dir / "project_metadata.json"
            
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            return None
            
        except Exception as e:
            print(f"Error getting project metadata: {e}")
            return None
    
    def delete_project(self, project_name: str) -> bool:
        """Delete a project and all its files"""
        try:
            safe_name = self._sanitize_filename(project_name)
            project_dir = self.projects_dir / safe_name
            
            if project_dir.exists():
                shutil.rmtree(project_dir)
            
            # Remove from database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get project ID first
            cursor.execute("SELECT id FROM projects WHERE name = ?", (project_name,))
            result = cursor.fetchone()
            
            if result:
                project_id = result[0]
                # Delete document versions
                cursor.execute("DELETE FROM document_versions WHERE project_id = ?", (project_id,))
                # Delete project
                cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Error deleting project: {e}")
            return False
    
    def get_document_versions(self, project_name: str, doc_type: str) -> List[Dict[str, Any]]:
        """Get version history for a document"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT dv.version, dv.changelog, dv.created_date
                FROM document_versions dv
                JOIN projects p ON dv.project_id = p.id
                WHERE p.name = ? AND dv.document_type = ?
                ORDER BY dv.version DESC
            """, (project_name, doc_type))
            
            versions = []
            for row in cursor.fetchall():
                versions.append({
                    'version': row[0],
                    'changelog': row[1],
                    'created_date': row[2]
                })
            
            conn.close()
            return versions
            
        except Exception as e:
            print(f"Error getting document versions: {e}")
            return []
    
    def add_asset(self, project_name: str, asset_path: str) -> bool:
        """Add an asset file to the project"""
        try:
            safe_name = self._sanitize_filename(project_name)
            project_dir = self.projects_dir / safe_name
            assets_dir = project_dir / "Assets"
            
            if not project_dir.exists():
                raise ValueError(f"Project '{project_name}' does not exist")
            
            # Copy file to assets directory
            asset_file = Path(asset_path)
            destination = assets_dir / asset_file.name
            
            shutil.copy2(asset_path, destination)
            
            # Update project modified date
            self._update_project_modified_date(safe_name)
            
            return True
            
        except Exception as e:
            print(f"Error adding asset: {e}")
            return False
    
    def get_assets(self, project_name: str) -> List[str]:
        """Get list of asset files in the project"""
        try:
            safe_name = self._sanitize_filename(project_name)
            project_dir = self.projects_dir / safe_name
            assets_dir = project_dir / "Assets"
            
            if not assets_dir.exists():
                return []
            
            assets = []
            for file_path in assets_dir.iterdir():
                if file_path.is_file():
                    assets.append(file_path.name)
            
            return sorted(assets)
            
        except Exception as e:
            print(f"Error getting assets: {e}")
            return []
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe file system operations"""
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Trim whitespace and dots
        filename = filename.strip(' .')
        
        # Ensure not empty
        if not filename:
            filename = "untitled_project"
        
        return filename
    
    def _save_project_to_db(self, metadata: Dict[str, Any], safe_name: str):
        """Save project metadata to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO projects (name, client_name, project_type, description, 
                                created_date, modified_date, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            metadata['project_name'],
            metadata['client_name'],
            metadata['project_type'],
            metadata['description'],
            metadata['created_date'],
            metadata['modified_date'],
            metadata['status']
        ))
        
        conn.commit()
        conn.close()
    
    def _update_project_modified_date(self, safe_name: str):
        """Update project modified date"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Update metadata file
        project_dir = self.projects_dir / safe_name
        metadata_file = project_dir / "project_metadata.json"
        
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            metadata['modified_date'] = datetime.now().isoformat()
            
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            # Update database
            cursor.execute("""
                UPDATE projects 
                SET modified_date = ? 
                WHERE name = ?
            """, (metadata['modified_date'], metadata['project_name']))
        
        conn.commit()
        conn.close()
    
    def _save_document_version(self, safe_name: str, doc_type: str, content: str, changelog: str):
        """Save document version to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get project ID
        cursor.execute("SELECT id FROM projects WHERE name LIKE ?", (f"%{safe_name}%",))
        result = cursor.fetchone()
        
        if result:
            project_id = result[0]
            
            # Get next version number
            cursor.execute("""
                SELECT MAX(version) FROM document_versions 
                WHERE project_id = ? AND document_type = ?
            """, (project_id, doc_type))
            
            max_version = cursor.fetchone()[0]
            next_version = (max_version or 0) + 1
            
            # Insert new version
            cursor.execute("""
                INSERT INTO document_versions 
                (project_id, document_type, version, content, changelog)
                VALUES (?, ?, ?, ?, ?)
            """, (project_id, doc_type, next_version, content, changelog))
        
        conn.commit()
        conn.close()
    
    def close(self):
        """Clean up resources"""
        # Any cleanup operations can go here
        pass