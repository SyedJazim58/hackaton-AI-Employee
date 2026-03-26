# QWEN.md - Project Context

## Project Overview

This is a **hackathon project** for building a **Personal AI Employee** (Digital FTE - Full-Time Equivalent). The project creates an autonomous AI agent that manages personal and business affairs 24/7 using:

- **Qwen Code** as the reasoning engine
- **Obsidian** (Markdown) as the knowledge base/dashboard
- **Python "Watcher" scripts** for monitoring inputs (Gmail, WhatsApp, filesystem)
- **MCP (Model Context Protocol) servers** for external actions

The architecture follows a **Perception → Reasoning → Action** pattern with human-in-the-loop approval for sensitive operations.

## Directory Structure

```
hackaton-AI-Employee/
├── .claude/skills/           # Claude Code skills (installed via skills-lock.json)
│   └── browsing-with-playwright/
├── .qwen/skills/             # Qwen skills (mirrored from .claude)
│   └── browsing-with-playwright/
├── Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md  # Main documentation
├── skills-lock.json          # Skill dependencies
└── QWEN.md                   # This file
```

## Key Concepts

### Architecture Layers

| Layer | Component | Purpose |
|-------|-----------|---------|
| **Brain** | Qwen Code | Reasoning engine, task execution |
| **Memory/GUI** | Obsidian Vault | Dashboard, long-term memory (Markdown files) |
| **Senses** | Python Watchers | Monitor Gmail, WhatsApp, filesystem for triggers |
| **Hands** | MCP Servers | External actions (browser automation, email, payments) |

### Watcher Pattern

Lightweight Python scripts that continuously monitor inputs and create `.md` files in `/Needs_Action` folder:

```python
# All watchers follow this base pattern
class BaseWatcher:
    def check_for_updates() -> list  # Return new items to process
    def create_action_file(item) -> Path  # Create .md in Needs_Action
    def run()  # Main loop with configurable interval
```

### Ralph Wiggum Loop (Persistence)

A Stop hook pattern that keeps Qwen Code working autonomously until tasks are complete:
1. Orchestrator creates state file with prompt
2. Qwen Code works on task
3. Qwen Code tries to exit
4. Stop hook checks: Is task file in `/Done`?
5. If NO → Block exit, re-inject prompt (loop continues)
6. Repeat until complete or max iterations

### Human-in-the-Loop (HITL)

For sensitive actions (payments, sending emails), Qwen Code writes an approval request file to `/Pending_Approval/` instead of acting directly. User moves file to `/Approved/` to trigger action.

## Installed Skills

### browsing-with-playwright

Browser automation via Playwright MCP server (22 tools available).

**Server Management:**
```bash
# Start (port 8808)
bash .claude/skills/browsing-with-playwright/scripts/start-server.sh

# Stop
bash .claude/skills/browsing-with-playwright/scripts/stop-server.sh
```

**Key Tools:**
- `browser_navigate` - Navigate to URL
- `browser_snapshot` - Get accessibility snapshot (element refs)
- `browser_click` - Click element (requires `ref` from snapshot)
- `browser_type` - Type text into element
- `browser_fill_form` - Fill multiple form fields
- `browser_take_screenshot` - Capture screenshot
- `browser_evaluate` - Execute JavaScript
- `browser_run_code` - Run Playwright code snippet
- `browser_close` - Close browser

**Usage Pattern:**
1. Navigate to page
2. Get snapshot to find element refs
3. Interact using refs (click, type, fill)
4. Wait for confirmation
5. Close browser when done

**MCP Client:** The skill includes `mcp-client.py` for direct tool calls:
```bash
python scripts/mcp-client.py call -u http://localhost:8808 -t browser_navigate -p '{"url": "https://example.com"}'
```

## Obsidian Vault Structure (Expected)

```
Vault/
├── Dashboard.md              # Real-time summary
├── Company_Handbook.md       # Rules of engagement
├── Business_Goals.md         # Q1/Q2 objectives, metrics
├── Inbox/                    # Raw incoming items
├── Needs_Action/             # Items requiring processing
├── In_Progress/<agent>/      # Claimed by specific agent
├── Pending_Approval/         # Awaiting human approval
├── Approved/                 # Approved actions (triggers execution)
├── Rejected/                 # Rejected actions
├── Done/                     # Completed tasks
├── Plans/                    # Generated plans (Plan.md)
├── Accounting/               # Bank transactions, Current_Month.md
└── Briefings/                # CEO Briefings (Monday Morning reports)
```

## Hackathon Tiers

| Tier | Requirements | Time |
|------|--------------|------|
| **Bronze** | Obsidian dashboard, 1 watcher, Claude reading/writing | 8-12 hrs |
| **Silver** | 2+ watchers, MCP server, HITL workflow, scheduling | 20-30 hrs |
| **Gold** | Full integration, Odoo accounting, Ralph Wiggum loop, audit logging | 40+ hrs |
| **Platinum** | Cloud deployment, domain specialization, vault sync | 60+ hrs |

## Development Practices

### Skill-Based AI Functionality
All AI functionality should be implemented as **Agent Skills** (SKILL.md format) for modularity and reusability.

### File-Based Communication
Agents communicate by writing files to specific folders:
- `/Needs_Action/<domain>/` - New work items
- `/Plans/<domain>/` - Generated plans
- `/Pending_Approval/<domain>/` - Awaiting approval
- Claim-by-move rule: First agent to move item to `/In_Progress/<agent>/` owns it

### Security Rules
- Secrets never sync (`.env`, tokens, WhatsApp sessions, banking credentials)
- Vault sync includes only markdown/state files
- Cloud agents work in draft-only mode; Local executes final actions

## Building & Running

### Prerequisites
- Python 3.13+
- Node.js v24+ LTS
- Qwen Code configured
- Obsidian v1.10.6+

### Starting a Watcher
```bash
python gmail_watcher.py /path/to/vault
python whatsapp_watcher.py /path/to/vault
python filesystem_watcher.py /path/to/vault
```

### Running Qwen Code Loop
```bash
# Process items in Needs_Action
cd AI_Employee_Vault
qwen "Process all files in /Needs_Action, move to /Done when complete"
```

### MCP Server Configuration
Configure in your MCP settings:
```json
{
  "servers": [
    {
      "name": "browser",
      "command": "npx",
      "args": ["@playwright/mcp"],
      "env": {"HEADLESS": "true"}
    }
  ]
}
```

## Key Files

| File | Purpose |
|------|---------|
| `Personal AI Employee Hackathon 0_...md` | Comprehensive architecture blueprint |
| `skills-lock.json` | Tracks installed skill versions |
| `.claude/skills/browsing-with-playwright/SKILL.md` | Browser automation skill documentation |
| `.claude/skills/browsing-with-playwright/scripts/mcp-client.py` | Universal MCP client (HTTP/stdio) |

## Meeting Schedule

**Research & Showcase:** Wednesdays 10:00 PM PKT on Zoom
- First meeting: Wednesday, Jan 7th, 2026
- [Zoom Link](https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1)
- [YouTube Archive](https://www.youtube.com/@panaversity)
