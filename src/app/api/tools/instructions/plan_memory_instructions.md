# Plan Memory Tool - Usage Instructions

## OVERVIEW
This toolkit provides stateful, persistent memory for the Team Leader agent. It functions as your primary to-do list and state tracker, enabling you to create, execute step-by-step, and record the results of your execution plan.

## PURPOSE
- **Task Management**: Create and track execution plans with multiple steps
- **State Persistence**: Maintain execution state across multiple agent calls
- **Progress Tracking**: Monitor which tasks are pending, completed, or failed
- **Result Recording**: Store outcomes and results for each executed task

## AVAILABLE TOOLS (4 total)

### 1. **add_tasks(task_names: list[str])** → str
Adds one or more new tasks to the execution plan with 'pending' status.

**Behavior:**
- If a task with the same name already exists, it will NOT be added again (prevents duplicates)
- All new tasks start with status='pending' and result=None
- Tasks are added to the end of the task list

**Arguments:**
- `task_names` (list[str]): List of descriptive names for tasks to add

**Returns:**
- Confirmation message: "Added N new tasks."

**Example Usage:**
```python
add_tasks([
    "Fetch Bitcoin price data",
    "Analyze market sentiment from news",
    "Retrieve social media discussions",
    "Generate comprehensive report"
])
# Returns: "Added 4 new tasks."
```

**Best Practices:**
- Use clear, descriptive task names that explain what needs to be done
- Break complex operations into smaller, manageable tasks
- Order tasks logically (dependencies first)
- Include specific details in task names (e.g., "Fetch BTC price for last 7 days" not "Get price")

---

### 2. **get_next_pending_task()** → Task | None
Retrieves the FIRST task from the plan that has 'pending' status.

**Behavior:**
- Returns tasks in the order they were added (FIFO - First In, First Out)
- Only returns tasks with status='pending'
- Returns None if no pending tasks exist

**Returns:**
- Task object (dict) with keys:
  - `name` (str): Task name
  - `status` (str): Always "pending" when returned by this function
  - `result` (str | None): Always None for pending tasks
- None if no pending tasks

**Example Usage:**
```python
next_task = get_next_pending_task()
if next_task:
    print(f"Next task to execute: {next_task['name']}")
else:
    print("All tasks completed or no tasks in plan")
```

**Workflow Pattern:**
1. Call `get_next_pending_task()` to get next task
2. Execute the task using appropriate specialist agent/tool
3. Call `update_task_status()` with results
4. Repeat until `get_next_pending_task()` returns None

---

### 3. **update_task_status(task_name: str, status: Literal["completed", "failed"], result: str | None)** → str
Updates the status and result of a specific task after execution.

**Arguments:**
- `task_name` (str): Exact name of the task (must match name from add_tasks)
- `status` (str): New status - either "completed" or "failed"
- `result` (str | None): Optional description of outcome, error message, or summary

**Returns:**
- Success: "Task 'Task Name' updated to {status}."
- Error: "Error: Task 'Task Name' not found."

**Example Usage:**
```python
# After successfully executing a task:
update_task_status(
    task_name="Fetch Bitcoin price data",
    status="completed",
    result="Retrieved BTC price: $67,543 from Binance at 2025-10-30 14:23:00"
)

# After task failure:
update_task_status(
    task_name="Analyze market sentiment",
    status="failed",
    result="Error: News API rate limit exceeded. Unable to fetch articles."
)
```

**Best Practices:**
- Always update status immediately after task execution
- Provide meaningful results that can be referenced later
- Include key data in result (prices, counts, timestamps)
- For failures, include error details for debugging
- Keep results concise but informative

---

### 4. **list_all_tasks()** → list[str]
Lists all tasks in the execution plan with their status and results.

**Returns:**
- List of formatted strings, each describing one task
- Format: "- {task_name}: {status} (Result: {result})"
- Returns ["No tasks in the plan."] if task list is empty

**Example Output:**
```
[
    "- Fetch Bitcoin price data: completed (Result: BTC=$67,543 at 14:23:00)",
    "- Analyze market sentiment: completed (Result: Bullish sentiment, 15 articles)",
    "- Retrieve social media posts: pending (Result: N/A)",
    "- Generate report: pending (Result: N/A)"
]
```

**Use Cases:**
- Review overall plan progress
- Check which tasks remain pending
- Retrieve results from completed tasks
- Debug failed tasks
- Provide status updates to user

---

## WORKFLOW PATTERNS

### **Pattern 1: Simple Sequential Execution**
```python
# Step 1: Create plan
add_tasks(["Task A", "Task B", "Task C"])

# Step 2: Execute loop
while True:
    task = get_next_pending_task()
    if not task:
        break
    
    # Execute task...
    result = execute_task(task['name'])
    
    # Update status
    update_task_status(task['name'], "completed", result)

# Step 3: Review results
all_tasks = list_all_tasks()
```

### **Pattern 2: Conditional Execution**
```python
add_tasks(["Fetch data", "Analyze if data available", "Generate report"])

task = get_next_pending_task()
result = fetch_data()

if result is None:
    update_task_status("Fetch data", "failed", "No data available")
    # Skip remaining tasks or add alternative tasks
else:
    update_task_status("Fetch data", "completed", result)
    # Continue to next task
```

### **Pattern 3: Dynamic Task Addition**
```python
add_tasks(["Check user request type"])

task = get_next_pending_task()
request_type = analyze_request()

if request_type == "comprehensive":
    # Add detailed tasks for comprehensive analysis
    add_tasks([
        "Fetch from all providers",
        "Aggregate results",
        "Perform cross-validation"
    ])
else:
    # Add simple tasks for quick lookup
    add_tasks(["Fetch from single provider"])

update_task_status("Check user request type", "completed", f"Type: {request_type}")
```

---

## CRITICAL RULES

1. **Task Names Must Be Unique**: Don't add duplicate task names - they will be ignored
2. **Exact Name Matching**: When updating status, task_name must EXACTLY match the name used in add_tasks
3. **Update After Execution**: ALWAYS call update_task_status after executing a task
4. **Sequential Execution**: Execute tasks in order using get_next_pending_task()
5. **Meaningful Results**: Store actionable information in results, not just "Done" or "Success"
6. **Handle Failures**: Don't stop plan execution when a task fails - update status and continue or adapt plan
7. **Review Before Finishing**: Call list_all_tasks() before completing user request to verify all tasks executed

---

## TASK NAMING BEST PRACTICES

**Good Task Names:**
- ✅ "Fetch BTC price from Binance for last 7 days"
- ✅ "Analyze news sentiment for Ethereum"
- ✅ "Retrieve Reddit posts about DeFi (limit=10)"
- ✅ "Calculate VWAP from aggregated provider data"
- ✅ "Generate comparison report for BTC vs ETH"

**Poor Task Names:**
- ❌ "Get data" (too vague)
- ❌ "Step 1" (not descriptive)
- ❌ "Do analysis" (what kind of analysis?)
- ❌ "Fetch" (fetch what?)

---

## RESULT CONTENT GUIDELINES

**Good Results:**
- ✅ "BTC price: $67,543 (Binance, 2025-10-30 14:23:00)"
- ✅ "Analyzed 15 articles. Sentiment: Bullish. Key theme: ETF approval"
- ✅ "Retrieved 10 Reddit posts. Avg upvotes: 234. Trend: Positive on BTC"
- ✅ "Aggregated 3 providers: Binance, Coinbase, YFinance. VWAP: $67,521"

**Poor Results:**
- ❌ "Done"
- ❌ "Success"
- ❌ "OK"
- ❌ "Completed successfully"

---

## ERROR HANDLING

**Common Errors:**
1. **Task Not Found**: Task name doesn't match exactly
   - Solution: Check spelling, capitalization, and spacing
   
2. **No Pending Tasks**: get_next_pending_task() returns None
   - Solution: Verify tasks were added, check if all are completed/failed
   
3. **Duplicate Task Names**: Task not added because name exists
   - Solution: Use unique, descriptive names or update existing task

**Recovery Strategies:**
- If specialist agent fails, mark task as "failed" with error details
- Add alternative tasks to work around failures
- Continue execution with remaining tasks
- Provide partial results if some tasks completed

---

## INTEGRATION WITH SPECIALIST AGENTS

When delegating to specialist agents (Market, News, Social), follow this pattern:

```python
# 1. Create plan
add_tasks([
    "Fetch market data for BTC",
    "Analyze news sentiment",
    "Check social media trends"
])

# 2. Execute market task
task = get_next_pending_task()
# Delegate to Market Specialist...
market_result = market_agent.get_product("BTC")
update_task_status(task['name'], "completed", f"BTC Price: ${market_result.price}")

# 3. Execute news task
task = get_next_pending_task()
# Delegate to News Specialist...
news_result = news_agent.get_latest_news("Bitcoin", limit=20)
update_task_status(task['name'], "completed", f"Found {len(news_result)} articles")

# And so on...
```

---

## STATE PERSISTENCE

**Important Notes:**
- Task state persists within a single agent session/conversation
- State is NOT persisted across different sessions or restarts
- If agent is reset, all tasks are lost
- For long-running operations, periodically call list_all_tasks() to preserve progress in conversation context
