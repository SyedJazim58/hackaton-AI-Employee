"""
Simple File Watcher - Polling-based watcher (no watchdog dependency).

This is a simpler alternative to filesystem_watcher.py that uses
polling instead of watchdog events. Useful when watchdog installation
fails.

Usage:
    python simple_file_watcher.py ./AI_Employee_Vault
"""

import sys
import shutil
import hashlib
import time
from pathlib import Path
from datetime import datetime

# Import base watcher
sys.path.insert(0, str(Path(__file__).parent))
from base_watcher import BaseWatcher


class SimpleFileWatcher(BaseWatcher):
    """
    Simple polling-based file watcher.
    
    Checks the drop folder at regular intervals and processes new files.
    Does not require watchdog package.
    """
    
    def __init__(self, vault_path: str, drop_folder: str = None, check_interval: int = 5):
        super().__init__(vault_path, check_interval)
        
        self.drop_folder = Path(drop_folder) if drop_folder else self.vault_path / 'Drop_Folder'
        self.drop_folder.mkdir(parents=True, exist_ok=True)
        
        # Track processed files
        self.processed_files: dict = {}
        
    def check_for_updates(self) -> list:
        """Check for new files in drop folder."""
        new_files = []
        
        if not self.drop_folder.exists():
            return new_files
        
        for file_path in self.drop_folder.iterdir():
            if file_path.is_file() and not file_path.name.startswith('.'):
                file_hash = self._get_file_hash(file_path)
                
                if file_path.name in self.processed_files:
                    if self.processed_files[file_path.name] == file_hash:
                        continue
                
                new_files.append(file_path)
                self.processed_files[file_path.name] = file_hash
        
        return new_files
    
    def _get_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of file."""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            self.logger.error(f"Error hashing {file_path.name}: {e}")
            return str(file_path.stat().st_mtime)
    
    def create_action_file(self, file_path: Path) -> Path:
        """Create action file for dropped file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_id = f"{file_path.stem}_{timestamp}"
        
        file_size = file_path.stat().st_size
        file_extension = file_path.suffix.lower()
        
        # Copy to vault
        dest_folder = self.vault_path / 'Inbox'
        dest_folder.mkdir(parents=True, exist_ok=True)
        dest_path = dest_folder / file_path.name
        
        counter = 1
        while dest_path.exists():
            new_name = f"{file_path.stem}_{counter}{file_path.suffix}"
            dest_path = dest_folder / new_name
            counter += 1
        
        shutil.copy2(file_path, dest_path)
        
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
**Location:** Inbox/{dest_path.name}

## Suggested Actions

- [ ] Review file contents
- [ ] Categorize the file
- [ ] Take necessary action
- [ ] Move to appropriate folder
- [ ] Mark as complete

---
*Created by SimpleFileWatcher*
"""
        
        action_file = self.needs_action / f"FILE_DROP_{file_id}.md"
        action_file.write_text(content, encoding='utf-8')
        
        self.logger.info(f"Created action file: {action_file.name}")
        return action_file


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python simple_file_watcher.py <vault_path>")
        print("\nExample: python simple_file_watcher.py ./AI_Employee_Vault")
        sys.exit(1)
    
    vault_path = sys.argv[1]
    
    if not Path(vault_path).exists():
        print(f"Error: Vault path does not exist: {vault_path}")
        sys.exit(1)
    
    print("=" * 50)
    print("Simple File Watcher (Bronze Tier)")
    print("=" * 50)
    print(f"Vault: {vault_path}")
    print(f"Drop Folder: {vault_path}/Drop_Folder")
    print("\nDrop files into the Drop_Folder to create action items.")
    print("Press Ctrl+C to stop.\n")
    
    watcher = SimpleFileWatcher(vault_path)
    watcher.run()
