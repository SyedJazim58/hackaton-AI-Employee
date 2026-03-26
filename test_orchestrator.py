"""
Test script for AI Employee Orchestrator.

Run this to verify all components work correctly.

Usage:
    python test_orchestrator.py ./AI_Employee_Vault
"""

import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from orchestrator import Orchestrator, ActionExecutor, QwenCodeRunner


def test_orchestrator(vault_path: str):
    """Run comprehensive tests on the orchestrator."""
    
    print("=" * 60)
    print("AI Employee Orchestrator - Test Suite")
    print("=" * 60)
    
    # Test 1: Initialization
    print("\n[TEST 1] Initializing Orchestrator...")
    try:
        orchestrator = Orchestrator(vault_path)
        print(f"✓ Orchestrator initialized for: {orchestrator.vault_path}")
    except Exception as e:
        print(f"✗ Failed to initialize: {e}")
        return False
    
    # Test 2: Action Executor
    print("\n[TEST 2] Testing ActionExecutor...")
    executor = orchestrator.action_executor
    
    # Create test file
    test_file = orchestrator.needs_action / 'TEST_MOVE_TO_DONE.md'
    test_file.write_text("""---
type: test
status: pending
---

# Test File

This is a test file for move operations.
""")
    print(f"  Created test file: {test_file.name}")
    
    # Test move to done
    success = executor.move_to_done('TEST_MOVE_TO_DONE.md')
    if success:
        print(f"  ✓ Move to Done: Success")
    else:
        print(f"  ✗ Move to Done: Failed")
        return False
    
    # Test 3: Qwen Code Runner
    print("\n[TEST 3] Testing QwenCodeRunner...")
    runner = orchestrator.qwen_runner
    
    # Create test file for Qwen processing
    test_file2 = orchestrator.needs_action / 'FILE_DROP_invoice_test.md'
    test_file2.write_text("""---
type: file_drop
source: invoice.txt
received: 2026-03-26T12:00:00
status: pending
---

# Invoice for Processing

**Client:** ABC Corporation
**Amount:** $1,500
**Service:** Consulting

Please process this invoice.
""")
    print(f"  Created test file: {test_file2.name}")
    
    # Process with simulated Qwen
    output = runner.process_item(test_file2, orchestrator.handbook)
    print(f"  ✓ Qwen simulation completed")
    print(f"  Output length: {len(output)} characters")
    
    # Parse actions
    actions = executor.parse_qwen_actions(output)
    print(f"  ✓ Parsed {len(actions)} action(s)")
    for action in actions:
        print(f"    - {action['type']}: {action['target']}")
    
    # Execute actions
    for action in actions:
        success = executor.execute_action(action)
        if success:
            print(f"    ✓ Executed: {action['type']}")
        else:
            print(f"    ✗ Failed: {action['type']}")
    
    # Test 4: Dashboard Update
    print("\n[TEST 4] Testing Dashboard Update...")
    try:
        orchestrator.update_dashboard()
        if orchestrator.dashboard.exists():
            content = orchestrator.dashboard.read_text()
            if 'AI Employee Dashboard' in content:
                print(f"  ✓ Dashboard updated successfully")
            else:
                print(f"  ✗ Dashboard content invalid")
                return False
        else:
            print(f"  ✗ Dashboard file not found")
            return False
    except Exception as e:
        print(f"  ✗ Dashboard update failed: {e}")
        return False
    
    # Test 5: Batch Processing
    print("\n[TEST 5] Testing Batch Processing...")
    
    # Create multiple test files
    for i in range(3):
        test_file = orchestrator.needs_action / f'BATCH_TEST_{i}.md'
        test_file.write_text(f"""---
type: batch_test
item: {i}
---

# Batch Test {i}

Process this item.
""")
    
    print(f"  Created 3 batch test files")
    
    # Process all pending
    processed = orchestrator.process_pending_items()
    print(f"  ✓ Processed {processed} item(s)")
    
    # Verify all moved to Done
    pending = len(orchestrator.get_pending_files())
    print(f"  Remaining pending: {pending}")
    
    if pending == 0:
        print(f"  ✓ All items processed successfully")
    else:
        print(f"  ⚠ {pending} items still pending")
    
    # Final Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Vault: {vault_path}")
    print(f"Pending files: {len(orchestrator.get_pending_files())}")
    print(f"Done files: {len(list(orchestrator.done.glob('*.md')))}")
    print(f"Approved files: {len(orchestrator.get_approved_files())}")
    print("=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)
    
    return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python test_orchestrator.py <vault_path>")
        print("\nExample: python test_orchestrator.py ./AI_Employee_Vault")
        sys.exit(1)
    
    vault_path = sys.argv[1]
    
    if not Path(vault_path).exists():
        print(f"Error: Vault path does not exist: {vault_path}")
        sys.exit(1)
    
    success = test_orchestrator(vault_path)
    sys.exit(0 if success else 1)
