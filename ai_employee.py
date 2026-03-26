#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI Employee - Complete System with Watcher + Orchestrator

WORKFLOW:
1. WATCHER: Monitors Drop_Folder → Moves file to Inbox → Creates action file in Needs_Action
2. ORCHESTRATOR: Detects file in Needs_Action → Triggers Qwen Code
3. QWEN CODE: Analyzes → Creates Plan → Makes Decision
4. DECISION:
   - If needs approval → Move to Pending_Approval (wait for human)
   - If auto-approve → Execute action → Move to Done
5. HUMAN: Reviews Pending_Approval → Moves to Approved
6. ORCHESTRATOR: Processes Approved → Executes → Moves to Done

Usage:
    python ai_employee.py ./AI_Employee_Vault
"""

import sys
import re
import subprocess
import logging
import time
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('orchestrator.log', encoding='utf-8', mode='a')
    ]
)


# ============================================================================
# WATCHER - Monitors Drop_Folder
# ============================================================================

class FileWatcher:
    """
    Watches Drop_Folder for new files.
    When file detected:
    1. Copy to Inbox/
    2. Create action file in Needs_Action/
    """
    
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.drop_folder = vault_path / 'Drop_Folder'
        self.inbox = vault_path / 'Inbox'
        self.needs_action = vault_path / 'Needs_Action'
        self.processed = set()
        self.logger = logging.getLogger('FileWatcher')
        
        # Ensure folders exist
        self.drop_folder.mkdir(parents=True, exist_ok=True)
        self.inbox.mkdir(parents=True, exist_ok=True)
        self.needs_action.mkdir(parents=True, exist_ok=True)
    
    def check_for_new_files(self) -> List[Path]:
        """Check Drop_Folder for new files."""
        new_files = []
        
        if not self.drop_folder.exists():
            return new_files
        
        for file_path in self.drop_folder.iterdir():
            if file_path.is_file() and not file_path.name.startswith('.'):
                file_hash = hash(file_path.name + str(file_path.stat().st_mtime))
                
                if file_hash not in self.processed:
                    new_files.append(file_path)
                    self.processed.add(file_hash)
        
        return new_files
    
    def process_file(self, file_path: Path) -> Optional[Path]:
        """
        Process a new file from Drop_Folder:
        1. Copy to Inbox/
        2. Create action file in Needs_Action/
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Determine file type from content
            content = file_path.read_text(encoding='utf-8', errors='ignore').lower()
            file_type = self._detect_file_type(content)
            
            # Copy to Inbox
            dest = self.inbox / file_path.name
            shutil.copy2(file_path, dest)
            self.logger.info(f"✓ Copied to Inbox: {file_path.name}")
            
            # Create action file in Needs_Action
            action_filename = f"{file_type}_{file_path.stem}_{timestamp}.md"
            action_file = self.needs_action / action_filename
            
            action_content = f"""---
type: {file_type}
source: {file_path.name}
received: {datetime.now().isoformat()}
status: pending
priority: normal
---

# Action Required: {file_type.replace('_', ' ').title()}

**Source File:** `{file_path.name}`
**Received:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Location:** [[Inbox/{file_path.name}]]

## Original Content

```
{file_path.read_text(encoding='utf-8', errors='ignore')}
```

## Processing Workflow

- [ ] Qwen Code to analyze content
- [ ] Create plan in /Plans/
- [ ] Generate response/action
- [ ] Execute or request approval
- [ ] Move to /Done/ when complete
"""
            
            action_file.write_text(action_content, encoding='utf-8')
            self.logger.info(f"✓ Created action file: {action_filename}")
            
            return action_file
            
        except Exception as e:
            self.logger.error(f"Error processing file: {e}")
            return None
    
    def _detect_file_type(self, content: str) -> str:
        """Detect file type from content."""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['invoice', 'payment', 'bill', 'receipt', '$']):
            return 'invoice'
        elif any(word in content_lower for word in ['email', 'message', 'reply']):
            return 'message'
        elif any(word in content_lower for word in ['meeting', 'notes', 'agenda']):
            return 'meeting_notes'
        elif any(word in content_lower for word in ['contract', 'agreement', 'legal']):
            return 'contract'
        elif any(word in content_lower for word in ['deposit', 'bank', 'transaction']):
            return 'deposit'
        elif any(word in content_lower for word in ['urgent', 'asap', 'emergency']):
            return 'urgent'
        else:
            return 'document'


# ============================================================================
# ORCHESTRATOR - Manages Qwen Code Processing
# ============================================================================

class Orchestrator:
    """
    Main orchestrator for the AI Employee system.
    
    Workflow:
    1. Process files from Watcher (in Needs_Action)
    2. Trigger Qwen Code to analyze and create plans
    3. Execute Qwen's decisions
    4. Handle approval workflow
    """

    def __init__(self, vault_path: str, check_interval: int = 30):
        self.vault_path = Path(vault_path)
        self.check_interval = check_interval
        self.logger = logging.getLogger('Orchestrator')

        # Folder paths
        self.inbox = self.vault_path / 'Inbox'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.done = self.vault_path / 'Done'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        self.plans = self.vault_path / 'Plans'
        self.logs = self.vault_path / 'Logs'
        self.dashboard = self.vault_path / 'Dashboard.md'
        self.handbook = self.vault_path / 'Company_Handbook.md'

        # Ensure folders exist
        for folder in [self.inbox, self.needs_action, self.done,
                       self.pending_approval, self.approved, self.rejected,
                       self.plans, self.logs]:
            folder.mkdir(parents=True, exist_ok=True)

        # Track processed files
        self.processed_files = set()
        
        # Initialize watcher
        self.watcher = FileWatcher(self.vault_path)

        self.logger.info(f'Orchestrator initialized for vault: {self.vault_path}')

    def get_pending_items(self) -> List[Path]:
        """Get unprocessed .md files from Needs_Action."""
        if not self.needs_action.exists():
            return []

        pending = []
        for f in self.needs_action.glob('*.md'):
            if f.name not in self.processed_files:
                pending.append(f)

        pending.sort(key=lambda x: x.stat().st_mtime)
        return pending

    def get_approved_items(self) -> List[Path]:
        """Get items from Approved folder ready for action."""
        if not self.approved.exists():
            return []
        return list(self.approved.glob('*.md'))

    def count_items(self) -> Dict[str, int]:
        """Count items in each folder."""
        return {
            'needs_action': len(list(self.needs_action.glob('*.md'))),
            'pending_approval': len(list(self.pending_approval.glob('*.md'))),
            'approved': len(list(self.approved.glob('*.md'))),
            'done': len(list(self.done.glob('*.md'))),
            'plans': len(list(self.plans.glob('*.md'))),
        }

    def update_dashboard(self):
        """Update Dashboard.md with current status."""
        counts = self.count_items()
        timestamp = datetime.now().isoformat()

        # Get recent activity
        recent = []
        done_files = sorted(self.done.glob('*.md'), key=lambda x: x.stat().st_mtime, reverse=True)[:5]
        for f in done_files:
            mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
            recent.append(f'- [{mtime}] Processed: {f.name}')

        # Get pending approvals
        pending = []
        for f in self.pending_approval.glob('*.md'):
            pending.append(f'- {f.name}')

        content = f"""---
last_updated: {timestamp}
status: active
---

# AI Employee Dashboard

## Quick Status

| Metric | Value | Trend |
|--------|-------|-------|
| Pending Tasks | {counts['needs_action']} | {'⚠️' if counts['needs_action'] > 5 else '✓'} |
| Awaiting Approval | {counts['pending_approval']} | - |
| Completed Total | {counts['done']} | - |

## Recent Activity

{chr(10).join(recent) if recent else '*No recent activity*'}

## Pending Approvals

{chr(10).join(pending) if pending else '*No pending approvals*'}

## Quick Links

- [[Company_Handbook]] - Rules
- [[Business_Goals]] - Objectives
- [Inbox](./Inbox/) - Raw files
- [Needs_Action](./Needs_Action/) - To process
- [Pending_Approval](./Pending_Approval/) - Awaiting review
- [Approved](./Approved/) - Ready to execute
- [Done](./Done/) - Completed

---
*Last processed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*AI Employee v1.0 - Powered by Qwen Code*
"""

        try:
            self.dashboard.write_text(content, encoding='utf-8')
            self.logger.info(f'📊 Dashboard: {counts["needs_action"]} pending, {counts["pending_approval"]} awaiting, {counts["done"]} done')
        except Exception as e:
            self.logger.error(f'Error updating dashboard: {e}')

    def trigger_qwen(self, prompt: str, timeout: int = 120) -> str:
        """
        Trigger Qwen Code and capture output.
        
        Returns Qwen Code's response.
        """
        try:
            import platform
            import os

            use_shell = platform.system() == 'Windows'
            cmd_name = 'qwen.cmd' if use_shell else 'qwen'

            original_cwd = os.getcwd()
            os.chdir(str(self.vault_path))

            cmd_string = f'{cmd_name} "{prompt}"'

            self.logger.info(f'🤖 TRIGGERING QWEN CODE...')

            result = subprocess.run(
                cmd_string,
                shell=use_shell,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            os.chdir(original_cwd)

            output = result.stdout if result.returncode == 0 else f"ERROR: {result.stderr}"
            
            if result.returncode == 0:
                self.logger.info('✅ Qwen Code completed')
            else:
                self.logger.error(f'Qwen Code error: {result.stderr}')

            return output

        except subprocess.TimeoutExpired:
            return "ERROR: Qwen Code timed out"
        except Exception as e:
            return f"ERROR: {str(e)}"

    def process_needs_action(self):
        """
        Process items in Needs_Action:
        1. Trigger Qwen Code
        2. Qwen analyzes and creates plan
        3. Qwen decides action (auto or approval)
        4. Execute decision
        """
        pending = self.get_pending_items()

        if not pending:
            self.logger.debug('No pending items')
            return

        self.logger.info(f'📁 Found {len(pending)} pending item(s)')

        for item in pending:
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f'Processing: {item.name}')
            
            # Read item content
            content = item.read_text(encoding='utf-8')
            
            # Build prompt for Qwen Code
            prompt = self._build_qwen_prompt(item.name, content)
            
            # TRIGGER QWEN CODE
            qwen_output = self.trigger_qwen(prompt)
            
            self.logger.info(f'📝 QWEN OUTPUT:\n{qwen_output[:500]}...')
            
            # Parse Qwen's decision
            decision = self._parse_qwen_decision(qwen_output, item.name)
            
            # Execute decision
            self._execute_decision(decision, item)
            
            self.processed_files.add(item.name)
            self.logger.info(f"{'='*60}\n")

    def _build_qwen_prompt(self, filename: str, content: str) -> str:
        """Build prompt for Qwen Code."""
        return f"""You are an AI Employee assistant. Process this action file.

## Company Handbook Rules
- Payments over $500 require approval
- Contracts require legal review
- Urgent items need immediate attention
- Meeting notes are for reference only

## Action File: {filename}

{content}

## YOUR TASK

1. ANALYZE the content type (invoice, message, contract, etc.)
2. CREATE a plan in /Plans/ with:
   - Objective
   - Step-by-step checklist
   - Mark steps needing approval
3. GENERATE appropriate response/action
4. DECIDE:
   - If needs approval → Output: MOVE_TO_PENDING: filename.md
   - If auto-approve → Output: MOVE_TO_DONE: filename.md
5. LOG your action → Output: LOG_ACTION: description

## OUTPUT FORMAT

```
## Analysis
[Your analysis]

## Plan Created
[Plan details or N/A]

## Response/Action
[Generated response or action taken]

## Decision
MOVE_TO_PENDING: filename.md
or
MOVE_TO_DONE: filename.md

## Log
LOG_ACTION: [description]
```
"""

    def _parse_qwen_decision(self, output: str, filename: str) -> Dict:
        """Parse Qwen Code output to extract decision."""
        decision = {
            'action': 'unknown',
            'target': filename,
            'plan': None,
            'log': None
        }
        
        # Check for move commands
        if 'MOVE_TO_PENDING' in output.upper():
            decision['action'] = 'move_to_pending'
        elif 'MOVE_TO_DONE' in output.upper():
            decision['action'] = 'move_to_done'
        else:
            # Default: if mentions approval needed, move to pending
            if any(word in output.lower() for word in ['approval', 'review', 'human']):
                decision['action'] = 'move_to_pending'
            else:
                decision['action'] = 'move_to_done'
        
        # Extract log action
        log_match = re.search(r'LOG_ACTION:\s*(.+?)(?:\n|$)', output, re.IGNORECASE)
        if log_match:
            decision['log'] = log_match.group(1).strip()
        
        return decision

    def _execute_decision(self, decision: Dict, item: Path):
        """Execute Qwen's decision."""
        action = decision['action']
        filename = decision['target']
        
        try:
            if action == 'move_to_pending':
                dest = self.pending_approval / filename
                item.rename(dest)
                self.logger.info(f'✓ Moved to Pending_Approval: {filename}')
                
            elif action == 'move_to_done':
                dest = self.done / filename
                item.rename(dest)
                self.logger.info(f'✓ Moved to Done: {filename}')
            
            # Log action
            if decision.get('log'):
                self._log_action('qwen_decision', decision['log'], filename)
                
        except Exception as e:
            self.logger.error(f'Error executing decision: {e}')

    def process_approved(self):
        """Process items that human has approved."""
        approved = self.get_approved_items()

        if not approved:
            return

        self.logger.info(f'✓ Found {len(approved)} approved item(s)')

        for item in approved:
            self.logger.info(f'Processing approved: {item.name}')
            
            # Read and extract action type
            content = item.read_text()
            action_type = self._extract_field(content, 'action')
            
            self.logger.info(f'Action type: {action_type}')
            
            # Execute based on action type
            if action_type == 'email_send':
                to_email = self._extract_field(content, 'to')
                subject = self._extract_field(content, 'subject')
                self.logger.info(f'Sending email to {to_email}: {subject}')
                # Would call email sending here
            
            # Move to Done after processing
            dest = self.done / item.name
            try:
                item.rename(dest)
                self.logger.info(f'✓ Moved to Done: {item.name}')
                self.processed_files.add(item.name)
            except Exception as e:
                self.logger.error(f'Error moving file: {e}')

    def _extract_field(self, content: str, field: str, default: str = '') -> str:
        """Extract field from markdown frontmatter."""
        match = re.search(rf'^{field}:\s*(.+)$', content, re.MULTILINE)
        return match.group(1).strip() if match else default

    def _log_action(self, action_type: str, details: str, file: str = None):
        """Log action to Logs folder."""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs / f'{today}.jsonl'

        entry = {
            'timestamp': datetime.now().isoformat(),
            'action_type': action_type,
            'actor': 'orchestrator',
            'details': details,
            'file': file,
            'status': 'success'
        }

        with open(log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')

    def run(self):
        """Main orchestration loop."""
        self.logger.info('=' * 60)
        self.logger.info('AI Employee System Starting')
        self.logger.info(f'Vault: {self.vault_path}')
        self.logger.info(f'Check interval: {self.check_interval}s')
        self.logger.info('Workflow: Watcher → Needs_Action → Qwen Code → Decision')
        self.logger.info('=' * 60)

        try:
            while True:
                try:
                    # STEP 1: Watcher checks Drop_Folder
                    new_files = self.watcher.check_for_new_files()
                    for file_path in new_files:
                        self.logger.info(f'📁 New file detected: {file_path.name}')
                        self.watcher.process_file(file_path)
                    
                    # STEP 2: Process Needs_Action with Qwen Code
                    self.process_needs_action()
                    
                    # STEP 3: Process Approved items
                    self.process_approved()
                    
                    # STEP 4: Update Dashboard
                    self.update_dashboard()

                except Exception as e:
                    self.logger.error(f'Error in loop: {e}')
                    self._log_action('error', str(e))

                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            self.logger.info('\n⛔ Stopped by user')
        finally:
            self.update_dashboard()
            self.logger.info('✅ Shutdown complete')


def main():
    if len(sys.argv) < 2:
        print("=" * 60)
        print("AI Employee System v1.0")
        print("=" * 60)
        print("\nUsage: python ai_employee.py /path/to/vault [options]")
        print("\nWorkflow:")
        print("  1. Drop file in Drop_Folder/")
        print("  2. Watcher moves to Inbox/ + Creates action in Needs_Action/")
        print("  3. Qwen Code analyzes and decides")
        print("  4. If approval needed → Pending_Approval/")
        print("  5. Human reviews → moves to Approved/")
        print("  6. Orchestrator executes → Done/")
        print("\nExample:")
        print("  python ai_employee.py ./AI_Employee_Vault")
        print("  python ai_employee.py ./AI_Employee_Vault --interval 20")
        print("\nPress Ctrl+C to stop")
        print("=" * 60)
        sys.exit(1)

    vault_path = sys.argv[1]
    interval = 30
    
    if '--interval' in sys.argv:
        try:
            idx = sys.argv.index('--interval')
            interval = int(sys.argv[idx + 1])
        except (IndexError, ValueError):
            pass

    if not Path(vault_path).exists():
        print(f"Error: Vault not found: {vault_path}")
        sys.exit(1)

    orchestrator = Orchestrator(vault_path, interval)
    orchestrator.run()


if __name__ == '__main__':
    main()
