"""
File System Watcher - Monitors a drop folder for new files.

This is the simplest watcher implementation, perfect for Bronze Tier.
Users can drop any file into the monitored folder, and the watcher
will create corresponding action files in the Needs_Action folder.

Usage:
    python filesystem_watcher.py /path/to/vault

Features:
- Monitors a "drop folder" for new files
- Creates metadata .md files for each dropped file
- Copies dropped files to the vault
- Supports common file types: .txt, .pdf, .doc, .docx, .csv, .jpg, .png
"""

import sys
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

from base_watcher import BaseWatcher


class DropFolderHandler(FileSystemEventHandler):
    """Handles file system events for the drop folder."""
    
    def __init__(self, watcher: 'FileSystemWatcher'):
        self.watcher = watcher
        self.logger = watcher.logger
    
    def on_created(self, event):
        """Called when a file or directory is created."""
        if event.is_directory:
            return
        
        source = Path(event.src_path)
        
        # Skip hidden files and temporary files
        if source.name.startswith('.') or source.name.endswith('.tmp'):
            return
        
        self.logger.info(f"New file detected: {source.name}")
        self.watcher.process_file(source)


class FileSystemWatcher(BaseWatcher):
    """
    Watches a drop folder for new files and creates action files.
    
    This is the simplest watcher to set up - just drop files into
    the monitored folder and they'll be processed automatically.
    """
    
    def __init__(self, vault_path: str, drop_folder: str = None, check_interval: int = 5):
        """
        Initialize the file system watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            drop_folder: Path to the folder to monitor (default: vault/Drop_Folder)
            check_interval: Seconds between checks (default: 5 for responsive file drops)
        """
        super().__init__(vault_path, check_interval)
        
        self.drop_folder = Path(drop_folder) if drop_folder else self.vault_path / 'Drop_Folder'
        self.drop_folder.mkdir(parents=True, exist_ok=True)
        
        # Track processed files by hash to avoid duplicates
        self.processed_files: dict = {}  # filename -> file hash
        
    def check_for_updates(self) -> list:
        """
        Check for new files in the drop folder.
        
        Returns:
            List of new file paths to process
        """
        new_files = []
        
        for file_path in self.drop_folder.iterdir():
            if file_path.is_file() and not file_path.name.startswith('.'):
                file_hash = self._get_file_hash(file_path)
                
                # Check if we've already processed this file
                if file_path.name in self.processed_files:
                    if self.processed_files[file_path.name] == file_hash:
                        continue  # Same file, already processed
                
                new_files.append(file_path)
                self.processed_files[file_path.name] = file_hash
        
        return new_files
    
    def _get_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of a file for duplicate detection."""
        hash_md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def process_file(self, file_path: Path):
        """Process a newly dropped file."""
        try:
            self.create_action_file(file_path)
        except Exception as e:
            self.logger.error(f"Error processing file {file_path.name}: {e}")
    
    def create_action_file(self, file_path: Path) -> Path:
        """
        Create a .md action file for the dropped file.
        
        Args:
            file_path: Path to the dropped file
            
        Returns:
            Path to the created action file
        """
        # Generate unique ID based on filename and timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_id = f"{file_path.stem}_{timestamp}"
        
        # Get file metadata
        file_size = file_path.stat().st_size
        file_extension = file_path.suffix.lower()
        
        # Copy file to vault
        dest_folder = self.vault_path / 'Inbox'
        dest_folder.mkdir(parents=True, exist_ok=True)
        dest_path = dest_folder / file_path.name
        
        # Handle duplicate filenames
        counter = 1
        while dest_path.exists():
            new_name = f"{file_path.stem}_{counter}{file_path.suffix}"
            dest_path = dest_folder / new_name
            counter += 1
        
        shutil.copy2(file_path, dest_path)
        
        # Create action file content
        content = f"""---
type: file_drop
source: {file_path.name}
received: {datetime.now().isoformat()}
file_path: {dest_path}
file_size: {file_size} bytes
status: pending
priority: normal
---

# File Dropped for Processing

**Original File:** `{file_path.name}`

**File Size:** {file_size} bytes

**Received:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**Location:** [[Inbox/{dest_path.name}]]

## Description

A new file has been dropped for processing. Please review and take appropriate action.

## Suggested Actions

- [ ] Review file contents
- [ ] Categorize the file
- [ ] Take necessary action
- [ ] Move to appropriate folder
- [ ] Mark as complete

## Notes

_Add any notes or context here_

---
*Created by FileSystemWatcher*
"""
        
        # Create action file
        action_file = self.needs_action / f"FILE_DROP_{file_id}.md"
        action_file.write_text(content, encoding='utf-8')
        
        self.logger.info(f"Created action file: {action_file.name}")
        return action_file
    
    def run(self):
        """
        Run the file system watcher with watchdog for real-time monitoring.
        """
        self.logger.info(f"Starting {self.__class__.__name__}")
        self.logger.info(f"Drop folder: {self.drop_folder}")
        self.logger.info(f"Vault path: {self.vault_path}")
        
        # Process any existing files first
        existing_files = self.check_for_updates()
        for file_path in existing_files:
            self.create_action_file(file_path)
        
        # Set up watchdog observer for real-time monitoring
        event_handler = DropFolderHandler(self)
        observer = Observer()
        observer.schedule(event_handler, str(self.drop_folder), recursive=False)
        observer.start()
        
        self.logger.info("Watching for new files... (Press Ctrl+C to stop)")
        
        try:
            while True:
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            observer.stop()
            self.logger.info("File system watcher stopped")
        
        observer.join()


# Import time here to avoid circular dependency
import time


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python filesystem_watcher.py <vault_path> [drop_folder]")
        print("\nExample:")
        print("  python filesystem_watcher.py ./AI_Employee_Vault")
        print("  python filesystem_watcher.py ./AI_Employee_Vault ./files_to_process")
        sys.exit(1)
    
    vault_path = sys.argv[1]
    drop_folder = sys.argv[2] if len(sys.argv) > 2 else None
    
    watcher = FileSystemWatcher(vault_path, drop_folder)
    watcher.run()
