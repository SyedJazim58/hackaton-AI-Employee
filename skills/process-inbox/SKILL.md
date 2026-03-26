---
name: process-inbox
description: |
  Process items from the AI Employee vault's Inbox and Needs_Action folders.
  Reads pending items, creates plans, and moves completed items to Done.
  Use this skill to manage the AI Employee's task queue.
---

# Process Inbox Skill

This skill enables Qwen Code to process items from the AI Employee vault.

## Workflow

1. **Read** items from `/Needs_Action/` folder
2. **Analyze** each item and determine required actions
3. **Create** a plan in `/Plans/` if complex actions needed
4. **Execute** simple actions directly (file moves, updates)
5. **Request approval** for sensitive actions (payments, external comms)
6. **Move** completed items to `/Done/`

## Usage

### Process All Pending Items

```bash
claude "Process all items in Needs_Action folder using the process-inbox skill"
```

### Process Specific Item

```bash
claude "Process the file drop item in Needs_Action about invoice.pdf"
```

### Update Dashboard

```bash
claude "Update Dashboard.md with current pending items count and recent activity"
```

## Action File Schema

Action files in `/Needs_Action/` follow this structure:

```markdown
---
type: file_drop | email | whatsapp | task
source: original_filename or sender
received: ISO timestamp
status: pending | in_progress | completed
priority: low | normal | high | urgent
---

# Content

Description of what needs to be done.

## Suggested Actions

- [ ] Action item 1
- [ ] Action item 2
```

## Plan File Template

When creating plans in `/Plans/`:

```markdown
---
created: ISO timestamp
status: pending | in_progress | completed | blocked
requires_approval: true | false
---

## Objective

Clear statement of what needs to be accomplished.

## Steps

- [x] Step already completed
- [ ] Next step to take
- [ ] Future step

## Notes

Any relevant context or decisions made.
```

## Approval Request Template

For actions requiring human approval:

```markdown
---
type: approval_request
action: send_email | make_payment | post_social | delete_file
created: ISO timestamp
expires: ISO timestamp (optional)
status: pending
---

## Action Details

Describe what will happen.

## To Approve

Move this file to `/Approved/` folder.

## To Reject

Move this file to `/Rejected/` folder or add comment explaining why.
```

## Rules

1. **Always** check `[[Company_Handbook]]` before taking actions
2. **Always** create approval requests for sensitive actions
3. **Never** delete files without explicit approval
4. **Always** log actions taken in the Dashboard
5. **Always** move completed items to `/Done/`

## Priority Keywords

| Keyword | Priority | Response Time |
|---------|----------|---------------|
| urgent, asap, emergency | High | Immediate |
| invoice, payment, billing | High | Within 2 hours |
| meeting, schedule | Medium | Within 4 hours |
| general inquiry | Normal | Within 24 hours |

## Examples

### Example: Processing a File Drop

1. Read the action file in `/Needs_Action/FILE_DROP_xxx.md`
2. Review the linked file in `/Inbox/`
3. Determine what action is needed
4. If simple (categorization): Do it and move to Done
5. If complex (requires external action): Create plan, request approval
6. Update Dashboard with activity

### Example: Updating Dashboard

```markdown
## Recent Activity

- [2026-03-26 10:30] Processed file drop: invoice.pdf
- [2026-03-26 09:15] Updated business goals for Q2

## Pending Approvals

- Payment to Vendor ABC ($150) - Awaiting approval since 2026-03-25
```

---

*Skill version: 1.0 (Bronze Tier)*
