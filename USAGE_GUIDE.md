# AI Employee - Complete Usage Guide

## Quick Start

### 1. Start the Orchestrator

```bash
cd D:\WMD\AI-employee\hackaton-AI-Employee
python orchestrator.py ./AI_Employee_Vault
```

**Keep this terminal running!**

### 2. Drop a File to Process

In another terminal or File Explorer:

```bash
echo "Invoice for Client ABC - Amount: $750" > AI_Employee_Vault/Drop_Folder/invoice.txt
```

### 3. Watch Qwen Code Process It

The orchestrator will:
1. Detect the new file (within 10 seconds)
2. **TRIGGER QWEN CODE** to analyze it
3. Qwen Code decides what action to take
4. Execute the action automatically

### 4. Check Results

```bash
# Check what Qwen Code decided
dir AI_Employee_Vault\Pending_Approval    # If approval needed
dir AI_Employee_Vault\Done                # If auto-processed
```

---

## How It Works

### The Complete Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI EMPLOYEE PROCESS                          │
└─────────────────────────────────────────────────────────────────┘

1. YOU drop a file
   ↓
   AI_Employee_Vault/Drop_Folder/your_file.txt

2. FILE WATCHER detects it (10 second interval)
   ↓
   Creates: Needs_Action/FILE_DROP_*.md
   Copies:  Inbox/your_file.txt

3. ORCHESTRATOR triggers QWEN CODE
   ↓
   Sends file content to Qwen Code with prompt:
   "Analyze this and decide what action to take"

4. QWEN CODE ANALYZES and DECIDES
   ↓
   Qwen Code reads content
   Applies Company Handbook rules
   Decides action based on content type:
   
   ┌──────────────────────────────────────────┐
   │ Content Type      →  Qwen's Decision     │
   ├──────────────────────────────────────────┤
   │ Invoice > $500    →  MOVE_TO_PENDING     │
   │ Invoice ≤ $500    →  MOVE_TO_DONE        │
   │ Meeting notes     →  MOVE_TO_DONE        │
   │ Contract          →  MOVE_TO_PENDING     │
   │ Urgent/ASAP       →  MOVE_TO_PENDING     │
   │ Generic document  →  MOVE_TO_DONE        │
   └──────────────────────────────────────────┘

5. ACTION EXECUTOR carries out Qwen's decision
   ↓
   Moves file to appropriate folder
   Logs the action
   Updates Dashboard

6. DASHBOARD updated (every cycle)
   ↓
   Shows current status
```

### Example: Invoice Processing

```
STEP 1: You drop invoice.txt with "$750" content
        ↓
STEP 2: Watcher creates FILE_DROP_invoice_*.md
        ↓
STEP 3: TRIGGER QWEN CODE
        ↓
STEP 4: Qwen Code analyzes:
        "This is an invoice for $750.
         Amount is over $500 threshold.
         Requires human approval."
        ↓
STEP 5: Qwen Code outputs decision:
        MOVE_TO_PENDING: FILE_DROP_invoice_*.md
        LOG_ACTION: Invoice for $750 requires approval
        ↓
STEP 6: Executor moves file to Pending_Approval/
        ↓
STEP 7: You review in Obsidian
        ↓
STEP 8: You move file to Approved/ if OK
        ↓
STEP 9: Next cycle - orchestrator processes approved file
        ↓
STEP 10: File moved to Done/ - Complete!
```

---

## Commands Reference

### Starting Commands

| Command | Description |
|---------|-------------|
| `python orchestrator.py ./AI_Employee_Vault` | Start orchestrator (simulation mode) |
| `python orchestrator.py ./AI_Employee_Vault cli` | Start with Qwen Code CLI |
| `python orchestrator.py ./AI_Employee_Vault api` | Start with Qwen API |

### File Operations

```bash
# Drop a file for processing
echo "content" > AI_Employee_Vault/Drop_Folder/file.txt

# Check pending items
dir AI_Employee_Vault\Needs_Action

# Check completed items
dir AI_Employee_Vault\Done

# Check items awaiting approval
dir AI_Employee_Vault\Pending_Approval

# View dashboard
type AI_Employee_Vault\Dashboard.md
```

### Log Commands

```bash
# View all logs
type orchestrator.log

# View errors only
type orchestrator.log | findstr ERROR

# Live tail (PowerShell)
powershell -Command "Get-Content orchestrator.log -Wait -Tail 30"

# View Qwen Code decisions only
type orchestrator.log | findstr "QWEN\|Decision"
```

---

## Qwen Code Decision Examples

### Example 1: Large Invoice (>$500)

**You drop:**
```
Invoice for XYZ Corp
Amount: $1,500
Services: Consulting
```

**Qwen Code decides:**
```markdown
## Analysis
This is an invoice for $1,500. According to Company Handbook,
amounts over $500 require human approval.

## Decision
MOVE_TO_PENDING: FILE_DROP_invoice_*.md
LOG_ACTION: Invoice for $1,500 requires human approval
```

**Result:** File moved to `Pending_Approval/` for your review

---

### Example 2: Small Invoice (≤$500)

**You drop:**
```
Invoice for Office Supplies
Amount: $150
```

**Qwen Code decides:**
```markdown
## Analysis
This is an invoice for $150. Below the $500 approval threshold.
Auto-processing.

## Decision
MOVE_TO_DONE: FILE_DROP_invoice_*.md
LOG_ACTION: Auto-processed invoice for $150
```

**Result:** File auto-processed to `Done/`

---

### Example 3: Meeting Notes

**You drop:**
```
Meeting Notes - Project Alpha
Attendees: John, Jane, Bob
Action: Create timeline
```

**Qwen Code decides:**
```markdown
## Analysis
These are meeting notes. Informational document for reference.
No action required beyond filing.

## Decision
MOVE_TO_DONE: FILE_DROP_meeting_*.md
LOG_ACTION: Filed meeting notes for reference
```

**Result:** Filed in `Done/`

---

### Example 4: Contract

**You drop:**
```
Service Agreement
Between Company ABC and Client XYZ
Terms: 12 months
```

**Qwen Code decides:**
```markdown
## Analysis
This is a legal document (contract/agreement).
Legal documents require human review.

## Decision
MOVE_TO_PENDING: FILE_DROP_contract_*.md
LOG_ACTION: Contract requires legal review
```

**Result:** Moved to `Pending_Approval/` for legal review

---

### Example 5: Urgent Item

**You drop:**
```
URGENT: Server down
ASAP assistance needed
```

**Qwen Code decides:**
```markdown
## Analysis
This item is marked as URGENT.
Requires immediate human attention.

## Decision
MOVE_TO_PENDING: FILE_DROP_urgent_*.md
LOG_ACTION: ⚠️ URGENT - Requires immediate human attention
```

**Result:** Moved to `Pending_Approval/` with high priority

---

## Configuration

### Change Processing Speed

Edit `orchestrator.py` line ~280:

```python
# Check every 10 seconds (default)
# Lower = faster processing, more CPU usage
time.sleep(10)  # Change to 5 for faster, 30 for slower
```

### Change Qwen Code Behavior

Edit `orchestrator.py` in `QwenCodeTrigger._simulate_qwen_decision()`:

```python
# Change approval threshold from $500 to $1000
if amount > 1000:  # Was 500
    # Needs approval
```

### Use Real Qwen Code

Edit `orchestrator.py` in `QwenCodeTrigger._call_qwen_code()`:

```python
# Uncomment this line to use real Qwen Code CLI:
return self._call_qwen_cli(prompt)

# Or this for Qwen API:
return self._call_qwen_api(prompt)
```

---

## Troubleshooting

### Problem: Orchestrator Won't Start

```bash
# Check Python version
python --version  # Should be 3.11+

# Check vault exists
dir AI_Employee_Vault
```

### Problem: Files Not Being Processed

```bash
# Check if file is in Drop_Folder
dir AI_Employee_Vault\Drop_Folder

# Check if action file was created
dir AI_Employee_Vault\Needs_Action

# Check logs for errors
powershell -Command "Get-Content orchestrator.log -Tail 50"
```

### Problem: Qwen Making Wrong Decisions

Update `Company_Handbook.md` with clearer rules:

```markdown
## Payment Approval Rules
- Payments under $50: Auto-approve
- Payments $50-$500: Manager approval
- Payments over $500: CEO approval
```

### Problem: Too Slow

Reduce check interval in `orchestrator.py`:

```python
# Line ~280: Change from 10 to 5 seconds
time.sleep(5)
```

---

## Daily Workflow

### Morning (9:00 AM)

```bash
# 1. Start orchestrator
python orchestrator.py ./AI_Employee_Vault

# 2. Drop any overnight files
echo "Overnight invoice" > AI_Employee_Vault/Drop_Folder/overnight.txt

# 3. Open Dashboard in Obsidian
# File: AI_Employee_Vault/Dashboard.md
```

### During Day

Just drop files into `Drop_Folder/`:

```bash
# Examples:
echo "Invoice for Client A - $300" > AI_Employee_Vault/Drop_Folder\invoice_a.txt
echo "Meeting notes from standup" > AI_Employee_Vault/Drop_Folder\standup.txt
echo "Contract review needed" > AI_Employee_Vault/Drop_Folder\contract.txt
```

Qwen Code will process each one automatically every 10 seconds!

### Evening (5:00 PM)

```bash
# 1. Check Dashboard in Obsidian
# Review what was processed

# 2. Review Pending_Approval items
dir AI_Employee_Vault\Pending_Approval

# 3. Move approved items to Approved/ folder

# 4. Stop orchestrator (optional - can run 24/7)
# Press Ctrl+C
```

---

## Understanding the Output

### Terminal Output Explained

```
2026-03-26 19:00:00 - Orchestrator - INFO - CYCLE 1 - Checking for files...
                                                              ↑
                                                      Processing cycle number

2026-03-26 19:00:05 - FileWatcher - INFO - ✓ Created action file: FILE_DROP_*.md
                                                ↑
                                        Watcher detected file

2026-03-26 19:00:10 - QwenCodeTrigger - INFO - 🤖 TRIGGERING QWEN CODE for: FILE_DROP_*.md
                                                    ↑
                                            Sending to Qwen Code

2026-03-26 19:00:11 - QwenCodeTrigger - INFO - ✅ QWEN CODE DECISION RECEIVED
                                                    ↑
                                            Got Qwen's decision

2026-03-26 19:00:11 - Orchestrator - INFO - 📋 Qwen decided on 2 action(s)
                                                ↑
                                        Number of actions to execute

2026-03-26 19:00:11 - ActionExecutor - INFO - ✓ Moved FILE_DROP_*.md to Pending_Approval
                                                    ↑
                                            Action executed

2026-03-26 19:00:11 - Orchestrator - INFO - 📊 Dashboard: 0 pending, 1 awaiting, 5 done
                                                ↑       ↑       ↑
                                            Pending Awaiting Done
```

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│  AI EMPLOYEE - QUICK REFERENCE                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  START:                                                 │
│    python orchestrator.py ./AI_Employee_Vault           │
│                                                         │
│  DROP FILES:                                            │
│    AI_Employee_Vault/Drop_Folder/your_file.txt          │
│                                                         │
│  CHECK STATUS:                                          │
│    Needs_Action/     → Waiting to process               │
│    Pending_Approval/ → Awaiting your review             │
│    Done/             → Completed                        │
│    Dashboard.md      → Open in Obsidian                 │
│                                                         │
│  QWEN CODE DECISIONS:                                   │
│    MOVE_TO_DONE     → Task complete                     │
│    MOVE_TO_PENDING  → Needs your approval               │
│    CREATE_PLAN      → Complex task                      │
│    LOG_ACTION       → Recording activity                │
│                                                         │
│  STOP: Ctrl+C                                           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

**That's it!** Your AI Employee with Qwen Code decision-making is ready to use! 🎉

For more details, see:
- `README.md` - Project overview
- `ORCHESTRATOR_GUIDE.md` - Detailed orchestrator documentation
- `AI_Employee_Vault/Company_Handbook.md` - Rules Qwen Code follows
