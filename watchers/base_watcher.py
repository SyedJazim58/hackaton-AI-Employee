"""
Base Watcher - Abstract base class for all AI Employee watchers.

All watchers follow this pattern:
1. Continuously monitor an input source (Gmail, WhatsApp, filesystem, etc.)
2. Detect new items that require action
3. Create .md action files in the Needs_Action folder
4. Claude Code processes these files and takes action

Usage:
    class MyWatcher(BaseWatcher):
        def check_for_updates(self) -> list:
            # Return list of new items
            pass
        
        def create_action_file(self, item) -> Path:
            # Create .md file in Needs_Action
            pass
        
        def run(self):
            # Start monitoring
            watcher = MyWatcher("/path/to/vault")
            watcher.run()
"""

import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class BaseWatcher(ABC):
    """
    Abstract base class for all watcher scripts.
    
    Watchers are lightweight Python scripts that run continuously
    and monitor various input sources for new items requiring action.
    """
    
    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize the watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            check_interval: Seconds between checks (default: 60)
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.inbox = self.vault_path / 'Inbox'
        self.check_interval = check_interval
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Ensure directories exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.inbox.mkdir(parents=True, exist_ok=True)
        
        # Track processed items to avoid duplicates
        self.processed_ids: set = set()
        
    @abstractmethod
    def check_for_updates(self) -> list:
        """
        Check for new items that require action.
        
        Returns:
            List of new items to process
        """
        pass
    
    @abstractmethod
    def create_action_file(self, item: Any) -> Path:
        """
        Create a .md action file in the Needs_Action folder.
        
        Args:
            item: The item to create an action file for
            
        Returns:
            Path to the created file
        """
        pass
    
    def create_inbox_file(self, item: Any, filename: str, content: str) -> Path:
        """
        Create a .md file in the Inbox folder.
        
        Args:
            item: The item to create a file for
            filename: Base filename (without extension)
            content: Markdown content for the file
            
        Returns:
            Path to the created file
        """
        filepath = self.inbox / f"{filename}.md"
        filepath.write_text(content, encoding='utf-8')
        self.logger.info(f"Created inbox file: {filepath}")
        return filepath
    
    def run(self):
        """
        Main watcher loop.
        
        Continuously checks for updates and creates action files.
        Runs until interrupted (Ctrl+C).
        """
        self.logger.info(f"Starting {self.__class__.__name__}")
        self.logger.info(f"Vault path: {self.vault_path}")
        self.logger.info(f"Check interval: {self.check_interval}s")
        
        try:
            while True:
                try:
                    items = self.check_for_updates()
                    for item in items:
                        try:
                            self.create_action_file(item)
                        except Exception as e:
                            self.logger.error(f"Error creating action file: {e}")
                except Exception as e:
                    self.logger.error(f"Error checking for updates: {e}")
                
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            self.logger.info(f"{self.__class__.__name__} stopped by user")
    
    def run_once(self) -> int:
        """
        Run a single check cycle (useful for testing).
        
        Returns:
            Number of items processed
        """
        items = self.check_for_updates()
        for item in items:
            self.create_action_file(item)
        return len(items)
