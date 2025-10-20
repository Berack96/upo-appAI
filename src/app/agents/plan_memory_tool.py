from agno.tools.toolkit import Toolkit
from typing import TypedDict, Literal



class Task(TypedDict):
    name: str
    status: Literal["pending", "completed", "failed"]
    result: str | None


class PlanMemoryTool(Toolkit):
    def __init__(self):
        self.tasks: list[Task] = []
        Toolkit.__init__(self, # type: ignore
            instructions="This tool manages an execution plan. Add tasks, get the next pending task, update a task's status (completed, failed) and result, or list all tasks.",
            tools=[
                self.add_tasks,
                self.get_next_pending_task,
                self.update_task_status,
                self.list_all_tasks,
            ]
        )

    def add_tasks(self, task_names: list[str]) -> str:
        """Adds multiple new tasks to the plan with 'pending' status."""
        count = 0
        for name in task_names:
            if not any(t['name'] == name for t in self.tasks):
                self.tasks.append({"name": name, "status": "pending", "result": None})
                count += 1
        return f"Added {count} new tasks."

    def get_next_pending_task(self) -> Task | None:
        """Retrieves the first task that is still 'pending'."""
        for task in self.tasks:
            if task["status"] == "pending":
                return task
        return None

    def update_task_status(self, task_name: str, status: Literal["completed", "failed"], result: str | None = None) -> str:
        """Updates the status and result of a specific task by its name."""
        for task in self.tasks:
            if task["name"] == task_name:
                task["status"] = status
                if result is not None:
                    task["result"] = result
                return f"Task '{task_name}' updated to {status}."
        return f"Error: Task '{task_name}' not found."

    def list_all_tasks(self) -> list[str]:
        """Lists all tasks in the plan with their status and result."""
        if not self.tasks:
            return ["No tasks in the plan."]
        return [f"- {t['name']}: {t['status']} (Result: {t.get('result', 'N/A')})" for t in self.tasks]