# Plan Memory Tool - Instructions

## Purpose
Stateful task management for Team Leader: create, track, and record execution plans with persistent state.

## Tools (4)

### 1. `add_tasks(task_names: list[str])` → str
Adds tasks with 'pending' status. Prevents duplicates. Returns: "Added N new tasks."

**Best Practices:**
- Clear, descriptive names (e.g., "Fetch BTC price for last 7 days" not "Get data")
- Order logically (dependencies first)
- Include specific details in names

### 2. `get_next_pending_task()` → Task | None
Returns FIRST pending task (FIFO order) or None if no pending tasks.

**Task Object:** `{name: str, status: "pending", result: None}`

### 3. `update_task_status(task_name, status, result)` → str
Updates task after execution. Status: "completed" or "failed". Result: optional outcome/error.

**Example:**
```python
update_task_status("Fetch BTC price", "completed", "BTC=$67,543 at 14:23:00")
update_task_status("Analyze sentiment", "failed", "API rate limit exceeded")
```

**Best Practices:**
- Update immediately after execution
- Include key data in result (prices, counts, timestamps)
- For failures, include error details

### 4. `list_all_tasks()` → list[str]
Lists all tasks with status and results. Format: "- {name}: {status} (Result: {result})"

## Workflow Pattern
```python
add_tasks(["Task A", "Task B", "Task C"])
while task := get_next_pending_task():
    result = execute(task['name'])
    update_task_status(task['name'], "completed", result)
all_tasks = list_all_tasks()
```

## Critical Rules
1. Task names must be unique (exact match for updates)
2. Always update status after execution
3. Execute sequentially using get_next_pending_task()
4. Store meaningful results, not just "Done"
5. Handle failures: update status="failed" and continue
6. Review with list_all_tasks() before finishing

## Good vs Poor Examples
**Good Task Names:** "Fetch BTC price from Binance for 7 days" | "Analyze Ethereum news sentiment"
**Poor Task Names:** "Get data" | "Step 1" | "Do analysis"

**Good Results:** "BTC: $67,543 (Binance, 2025-10-30 14:23)" | "15 articles, Bullish sentiment"
**Poor Results:** "Done" | "Success" | "OK"

## State Persistence
- Persists within single session only (not across restarts)
- Call list_all_tasks() periodically to preserve context
