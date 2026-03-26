# AI Employee - Bronze Tier Implementation

A Personal AI Employee built with Qwen Code and Obsidian. This is the **Bronze Tier** foundation implementing the core architecture.

## Quick Start

### Prerequisites

- **Python 3.11+** with working pip
- **Qwen Code** installed and configured
- **Obsidian** (for viewing the vault)
- **Node.js v24+** (for MCP servers in future tiers)

### Installation

1. **Install Python dependencies:**

```bash
cd watchers
pip install -r requirements.txt
```

If pip has issues, try:
```bash
python -m ensurepip --upgrade
python -m pip install watchdog
```

2. **Open the Obsidian Vault:**

Open `AI_Employee_Vault/` folder in Obsidian.

3. **Verify Qwen Code:**

Ensure Qwen Code is properly configured in your IDE or environment.

## Project Structure

```
hackaton-AI-Employee/
├── AI_Employee_Vault/          # Obsidian vault
│   ├── Dashboard.md            # Real-time status dashboard
│   ├── Company_Handbook.md     # Rules of engagement
│   ├── Business_Goals.md       # Q1/Q2 objectives
│   ├── Inbox/                  # Raw incoming files
│   ├── Needs_Action/           # Items requiring processing
│   ├── Plans/                  # Generated plans
│   ├── Pending_Approval/       # Awaiting human approval
│   ├── Approved/               # Approved actions (ready to execute)
│   ├── Rejected/               # Rejected actions
│   ├── Done/                   # Completed tasks
│   ├── Accounting/             # Financial records
│   └── Briefings/              # CEO briefings
│
├── watchers/
│   ├── base_watcher.py         # Abstract base class for all watchers
│   ├── filesystem_watcher.py   # File drop watcher (Bronze tier)
│   └── requirements.txt        # Python dependencies
│
├── skills/
│   └── process-inbox/
│       └── SKILL.md            # Qwen Code Agent Skill
│
├── orchestrator.py             # Master process coordinator
└── README.md                   # This file
```

## Usage

### Option 1: Run File System Watcher Only

Start the watcher to monitor the Drop_Folder:

```bash
python watchers/filesystem_watcher.py ./AI_Employee_Vault
```

Then drop any file into `AI_Employee_Vault/Drop_Folder/` and the watcher will:
1. Create an action file in `Needs_Action/`
2. Copy the file to `Inbox/`

### Option 2: Run Full Orchestrator (RECOMMENDED)

The orchestrator manages watchers AND automatically processes items with Qwen Code:

```bash
python orchestrator.py ./AI_Employee_Vault
```

This will:
1. Start the file system watcher
2. **Auto-process items every 30 seconds** (Qwen Code decides actions)
3. Execute actions (move files, create plans, log actions)
4. Update the Dashboard every 60 seconds

**Integration Modes:**

```bash
# Simulation mode (default - for testing)
python orchestrator.py ./AI_Employee_Vault

# CLI mode (uses actual Qwen Code CLI)
python orchestrator.py ./AI_Employee_Vault cli

# API mode (uses Qwen API)
python orchestrator.py ./AI_Employee_Vault api
```

**This is the recommended way to run the AI Employee!**

### Option 3: Manual Qwen Code Processing

Process items manually with Qwen Code:

```bash
cd AI_Employee_Vault
# Use Qwen Code in your IDE or run:
qwen "Process all items in Needs_Action folder. Check Company_Handbook for rules. Update Dashboard when done."
```

## Testing the Workflow

### Quick Test (Recommended)

Run the automated test suite:

```bash
python test_orchestrator.py ./AI_Employee_Vault
```

This verifies all components work correctly.

### Manual File Drop Test

### Test File Drop Processing

1. **Start the watcher:**
   ```bash
   python watchers/filesystem_watcher.py ./AI_Employee_Vault
   ```

2. **Drop a test file:**
   Create a text file and save it to `AI_Employee_Vault/Drop_Folder/test_document.txt`

3. **Verify action file created:**
   Check `AI_Employee_Vault/Needs_Action/` for a new `FILE_DROP_*.md` file

4. **Process with Qwen Code:**
   ```bash
   cd AI_Employee_Vault
   qwen "Read the FILE_DROP action file and process it according to Company_Handbook rules"
   ```

5. **Verify completion:**
   - Check that file was moved to `Done/`
   - Check that Dashboard.md was updated

## Bronze Tier Deliverables Checklist

- [x] **Obsidian vault** with Dashboard.md and Company_Handbook.md
- [x] **Basic folder structure**: /Inbox, /Needs_Action, /Done
- [x] **One working Watcher script**: File System Watcher
- [x] **Qwen Code integration**: Reading from and writing to vault
- [x] **Agent Skill**: process-inbox SKILL.md

## Configuration

### Watcher Settings

Edit `watchers/filesystem_watcher.py` to customize:

```python
# Check interval (seconds)
check_interval = 5  # How often to check for new files

# Drop folder location
drop_folder = vault_path / 'Drop_Folder'  # Default location
```

### Orchestrator Settings

Edit `orchestrator.py` to customize:

```python
claude_check_interval = 60      # Seconds between Qwen Code processing
dashboard_update_interval = 300 # Seconds between dashboard updates
```

## Troubleshooting

### Python/pip Issues

If pip is broken:
```bash
python -m ensurepip --upgrade
python -m pip install --upgrade pip
python -m pip install watchdog
```

### Watcher Not Detecting Files

1. Check the Drop_Folder path is correct
2. Verify file doesn't start with `.` (hidden files are ignored)
3. Check watcher logs for errors

### Qwen Code Not Processing

1. Verify Qwen Code is properly configured
2. Check you're in the vault directory
3. Ensure files have `.md` extension

## Next Steps (Silver Tier)

To upgrade to Silver Tier, add:
- Gmail Watcher with Google API integration
- WhatsApp Watcher using Playwright
- MCP server for sending emails
- Human-in-the-loop approval workflow
- Scheduled tasks via cron/Task Scheduler

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  External Input │────▶│   Watchers       │────▶│  Needs_Action/  │
│  (Files, Email) │     │  (Python)        │     │  (Markdown)     │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
┌─────────────────┐     ┌──────────────────┐     ┌────────▼────────┐
│   Dashboard.md  │◀────│   Qwen Code      │◀────│   Plans/       │
│   (Status)      │     │   (Reasoning)    │     │   (Actions)     │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

## Security Notes

- Never commit `.env` files with credentials
- Keep API keys in environment variables
- Review all actions in `Done/` folder weekly
- Set appropriate approval thresholds in `Company_Handbook.md`

---

*AI Employee v0.1 - Bronze Tier*
*Built for Personal AI Employee Hackathon 2026*
