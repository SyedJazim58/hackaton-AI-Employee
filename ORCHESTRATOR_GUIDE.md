# Orchestrator Guide - AI Employee Bronze Tier

## What Does the Orchestrator Do?

The `orchestrator.py` script is the **brain** of your AI Employee. It:

1. **Runs the File Watcher** - Monitors Drop_Folder for new files
2. **Runs Qwen Code** - Processes items every 30 seconds
3. **Qwen Code Decides Actions** - Analyzes content and decides what to do
4. **Executes Actions** - Moves files, creates plans, logs activities
5. **Updates Dashboard** - Refreshes status every 60 seconds

## Quick Start

```bash
# Start the orchestrator (simulation mode - default)
python orchestrator.py ./AI_Employee_Vault

# Start with CLI mode (uses actual Qwen Code)
python orchestrator.py ./AI_Employee_Vault cli

# Start with API mode (uses Qwen API)
python orchestrator.py ./AI_Employee_Vault api

# Stop with Ctrl+C
```

## Integration Modes

| Mode | Description | When to Use |
|------|-------------|-------------|
| **simulation** | Simulated Qwen processing | Testing, development, demo |
| **cli** | Qwen Code CLI | You have Qwen Code installed |
| **api** | Qwen API | You have Qwen API key |

### Simulation Mode (Default)

Simulates Qwen Code decision-making based on content analysis:

```bash
python orchestrator.py ./AI_Employee_Vault
# or explicitly:
python orchestrator.py ./AI_Employee_Vault simulation
```

**What it does:**
- Analyzes file content for keywords (invoice, meeting, contract, urgent)
- Makes decisions based on Company Handbook rules
- Perfect for testing without needing Qwen Code installed

### CLI Mode

Uses actual Qwen Code CLI:

```bash
python orchestrator.py ./AI_Employee_Vault cli
```

**Requirements:**
- Qwen Code must be installed and accessible via `qwen` command

**Configuration:**
Edit `orchestrator.py` line 23:
```python
QWEN_COMMAND = 'qwen'  # Change if your command is different
```

### API Mode

Uses Qwen API directly:

```bash
python orchestrator.py ./AI_Employee_Vault api
```

**Requirements:**
- Set environment variable: `QWEN_API_KEY`
- Install requests: `pip install requests`

**Configuration:**
```bash
# Set API key
set QWEN_API_KEY=your_api_key_here

# Run orchestrator
python orchestrator.py ./AI_Employee_Vault api
```

## How Qwen Code Decides Actions

### Decision Flow

```
Qwen Code reads file content
         ↓
Analyzes for keywords and patterns
         ↓
Applies Company Handbook rules
         ↓
Decides action type:
┌─────────────────────────────────────┐
│ MOVE_TO_DONE     → File complete    │
│ MOVE_TO_PENDING  → Needs approval   │
│ CREATE_PLAN      → Complex task     │
│ LOG_ACTION       → Record activity  │
└─────────────────────────────────────┘
         ↓
Executes action automatically
```

### Decision Rules (Simulation Mode)

| Content Pattern | Decision | Action |
|-----------------|----------|--------|
| Invoice > $50 | Needs approval | MOVE_TO_PENDING |
| Invoice ≤ $50 | Auto-process | MOVE_TO_DONE |
| Meeting notes | File for reference | MOVE_TO_DONE |
| Contract/Agreement | Legal review needed | MOVE_TO_PENDING |
| Urgent/ASAP | Immediate attention | MOVE_TO_PENDING |
| Generic document | Standard processing | MOVE_TO_DONE |

### Example Qwen Code Output

```markdown
## Analysis
This is an invoice for $1,500.00. According to Company Handbook, 
payments over $50 require human approval.

## Decision
Moving to Pending_Approval for human review.

MOVE_TO_PENDING: FILE_DROP_invoice_123.md
LOG_ACTION: Invoice for $1,500.00 requires approval
```

## Action Commands

Qwen Code output is parsed for these commands:

| Command | Format | What It Does |
|---------|--------|--------------|
| **Move to Done** | `MOVE_TO_DONE: filename.md` | Moves file to Done/ folder |
| **Move to Pending** | `MOVE_TO_PENDING: filename.md` | Moves to Pending_Approval/ for human review |
| **Create Plan** | `CREATE_PLAN: plan_name` | Creates plan file in Plans/ |
| **Log Action** | `LOG_ACTION: message` | Logs action to Logs/YYYY-MM-DD.md |

## Configuration

Edit `orchestrator.py` to customize:

```python
# Line 20: Integration mode
INTEGRATION_MODE = 'simulation'  # Options: 'simulation', 'cli', 'api'

# Line 23: Qwen CLI command
QWEN_COMMAND = 'qwen'

# Line 32: Processing interval (default: 30 seconds)
QWEN_CHECK_INTERVAL = 30

# Line 33: Dashboard update interval (default: 60 seconds)
DASHBOARD_UPDATE_INTERVAL = 60
```

## Complete Example Session

```
$ python orchestrator.py ./AI_Employee_Vault

============================================================
AI Employee Orchestrator - Bronze Tier
============================================================
Vault: D:\...\AI_Employee_Vault
Integration Mode: simulation
Auto-processing: Enabled
Qwen Check Interval: 30s
Dashboard Update: 60s
============================================================
2026-03-26 19:00:00 - Orchestrator - INFO - File watcher started
2026-03-26 19:00:00 - Orchestrator - INFO - Entering main loop...

# You drop a file in another terminal:
$ echo "Invoice: Client ABC, Amount: $1500" > AI_Employee_Vault/Drop_Folder/invoice.txt

# Back in orchestrator terminal:
2026-03-26 19:00:05 - SimpleFileWatcher - INFO - Created action file: FILE_DROP_invoice_*.md

# 30 seconds later - Qwen Code processes:
2026-03-26 19:00:30 - Orchestrator - INFO - ============================================================
2026-03-26 19:00:30 - Orchestrator - INFO - Processing Cycle 1
2026-03-26 19:00:30 - Orchestrator - INFO - ============================================================
2026-03-26 19:00:30 - Orchestrator - INFO - Processing: FILE_DROP_invoice_*.md
2026-03-26 19:00:30 - Orchestrator - INFO - Qwen Code output:
2026-03-26 19:00:30 - Orchestrator - INFO - 
## Analysis
This is an invoice for $1500.00. According to Company Handbook, 
payments over $50 require human approval.

## Decision
Moving to Pending_Approval for human review.

MOVE_TO_PENDING: FILE_DROP_invoice_*.md
LOG_ACTION: Invoice for $1500.00 requires approval

2026-03-26 19:00:30 - Orchestrator - INFO - Qwen Code decided on 2 action(s)
2026-03-26 19:00:30 - ActionExecutor - INFO - ✓ Moved FILE_DROP_invoice_*.md to Pending_Approval (awaiting human review)
2026-03-26 19:00:30 - Orchestrator - INFO -   ✓ Executed: move_to_pending -> FILE_DROP_invoice_*.md
2026-03-26 19:00:30 - ActionExecutor - INFO - ✓ Logged: Invoice for $1500.00 requires approval
2026-03-26 19:00:30 - Orchestrator - INFO -   ✓ Executed: log_action -> Invoice for $1500.00 requires approval
2026-03-26 19:00:30 - Orchestrator - INFO - Processed 1 pending item(s)

# 60 seconds later - Dashboard updates:
2026-03-26 19:01:00 - Orchestrator - INFO - Dashboard updated: 0 pending, 1 completed

# You review and approve in Obsidian:
# Move FILE_DROP_invoice_*.md from Pending_Approval/ to Approved/

# Next cycle - approved file processed:
2026-03-26 19:01:30 - Orchestrator - INFO - Processing 1 approved item(s)
2026-03-26 19:01:30 - Orchestrator - INFO - Processed approved file: FILE_DROP_invoice_*.md

# Stop with Ctrl+C:
^C
2026-03-26 19:02:00 - Orchestrator - INFO - Orchestrator stopped by user
2026-03-26 19:02:00 - Orchestrator - INFO - Orchestrator shutdown complete
```

## Testing

Run the test suite:

```bash
python test_orchestrator.py ./AI_Employee_Vault
```

Expected output:
```
✓ Orchestrator initialized
✓ Integration mode: simulation
✓ Move to Done: Success
✓ Qwen simulation completed
✓ Parsed 2 action(s)
✓ Dashboard updated successfully
✓ All items processed successfully
```

## Logs

All activities are logged to `orchestrator.log`:

```bash
# View recent logs
type orchestrator.log

# View errors only
type orchestrator.log | findstr ERROR

# Live tail (PowerShell)
powershell -Command "Get-Content orchestrator.log -Wait -Tail 20"
```

## Troubleshooting

### Orchestrator Won't Start

```bash
# Check Python version
python --version  # Should be 3.11+

# Check vault path exists
dir AI_Employee_Vault
```

### Qwen CLI Mode Fails

```bash
# Verify Qwen Code is installed
qwen --version

# If not found, use simulation mode instead
python orchestrator.py ./AI_Employee_Vault simulation
```

### API Mode Fails

```bash
# Check API key is set
echo %QWEN_API_KEY%

# Install requests library
pip install requests

# Test API connection
python -c "import requests; print('OK')"
```

### Files Not Being Processed

```bash
# Check if files are in Needs_Action
dir AI_Employee_Vault\Needs_Action

# Check logs for Qwen errors
type orchestrator.log | findstr "Qwen"

# Reduce processing interval for faster processing
# Edit orchestrator.py line 32:
QWEN_CHECK_INTERVAL = 10  # Process every 10 seconds
```

### Qwen Making Wrong Decisions

Review and update `Company_Handbook.md`:

```bash
# Open in editor
notepad AI_Employee_Vault\Company_Handbook.md

# Add more specific rules, e.g.:
## Payment Rules
- Payments under $50: Auto-approve
- Payments $50-$200: Require approval
- Payments over $200: Require CEO approval
```

## Advanced: Custom Qwen Integration

To customize how Qwen Code is called, edit `QwenCodeRunner` class:

```python
def _run_cli(self, prompt: str) -> str:
    """Custom CLI integration."""
    # Your custom code here
    result = subprocess.run(
        ['your-custom-command', prompt],
        capture_output=True,
        text=True
    )
    return result.stdout
```

## Human-in-the-Loop Workflow

For items requiring approval:

```
1. Qwen Code analyzes file
   ↓
2. Decides: "Needs human approval"
   ↓
3. Moves to Pending_Approval/
   ↓
4. You review in Obsidian
   ↓
5. You move to Approved/ or Rejected/
   ↓
6. Orchestrator processes approved files
   ↓
7. Moves to Done/ when complete
```

## Quick Reference

```
┌─────────────────────────────────────────────────────────┐
│  ORCHESTRATOR QUICK REFERENCE                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  START:                                                 │
│    python orchestrator.py ./AI_Employee_Vault           │
│    python orchestrator.py ./AI_Employee_Vault cli       │
│    python orchestrator.py ./AI_Employee_Vault api       │
│                                                         │
│  STOP: Ctrl+C                                           │
│                                                         │
│  TEST: python test_orchestrator.py ./AI_Employee_Vault  │
│                                                         │
│  LOGS: type orchestrator.log                            │
│                                                         │
│  MODES:                                                 │
│    simulation - Test without Qwen Code                  │
│    cli        - Use Qwen Code CLI                        │
│    api        - Use Qwen API                             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

*For more details, see README.md*
