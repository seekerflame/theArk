# Jules Mission: Code Mint Testing

> **Agent**: Jules
> **Priority**: HIGH
> **Branch**: `feature/jules-code-mint-tests`

---

## Objective

Write comprehensive tests for the new `/api/mint/code` endpoint and `CODE_MINT` block type.

---

## Tasks

### 1. Add CODE_MINT Test to test_ledger.py

Add this test case:

```python
def test_get_balance_code_mint(ledger):
    ledger.add_block("CODE_MINT", {"minter": "jules", "reward": 15, "lines_changed": 150})
    assert ledger.get_balance("jules") == 15
```

### 2. Create test_economy.py

Create a new test file for economy API endpoints:

```python
# tests/test_economy.py
import pytest
from unittest.mock import Mock, MagicMock

def test_mint_code_endpoint():
    """Test /api/mint/code calculates rewards correctly"""
    # Test cases:
    # - 100 lines, standard complexity = 10 AT
    # - 100 lines, expert complexity = 30 AT
    # - 10 lines (should get minimum 1 AT)
    pass
```

### 3. Test n8n Workflow

Import `code_contribution_mint.json` into n8n and verify:

- Webhook receives test payload
- Complexity classification works
- API call succeeds

---

## Acceptance Criteria

- [ ] All existing tests still pass (`pytest tests/ -v`)
- [ ] New CODE_MINT test added and passing
- [ ] Economy API tests created
- [ ] PR opened with `[Jules]` prefix

---

## Context

Today's changes:

- `core/ledger.py`: Added CODE_MINT to get_balance()
- `api/economy.py`: Added `/api/mint/code` endpoint

Complexity multipliers:

- trivial: 0.5x (docs, comments)
- standard: 1.0x (normal code)
- complex: 2.0x (core systems)
- expert: 3.0x (crypto, architecture)

Base rate: 0.1 AT per line changed

---

*Created: 2026-01-04*
*Mission issued by: Antigravity*
