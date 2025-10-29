from agno.tools.toolkit import Toolkit
from typing import TypedDict, Literal



class Task(TypedDict):
    """
    Represents a single task in the execution plan.

    Attributes:
        name (str): The unique name of the task.
        status (Literal["pending", "completed", "failed"]): The current status of the task.
            - "pending": The task is yet to be executed.
            - "completed": The task has been successfully executed.
            - "failed": The task execution was unsuccessful.
        result (str | None): An optional field to store the result or outcome of the task.
            This could be a summary, an error message, or any relevant information.
    """
    name: str
    status: Literal["pending", "completed", "failed"]
    result: str | None


class PlanMemoryTool(Toolkit):
    def __init__(self):
        self.tasks: list[Task] = []
        Toolkit.__init__(self, # type: ignore[call-arg]
            name="Plan Memory Tool",
            instructions="Provides stateful, persistent memory for the Team Leader. " \
                 "This is your primary to-do list and state tracker. " \
                 "Use it to create, execute step-by-step, and record the results of your execution plan.",
            tools=[
                self.add_tasks,
                self.get_next_pending_task,
                self.update_task_status,
                self.list_all_tasks,
            ]
        )

    def add_tasks(self, task_names: list[str]) -> str:
        """
        Adds one or more new tasks to the execution plan with a 'pending' status.
        If a task with the same name already exists, it will not be added again.

        Args:
            task_names (list[str]): A list of descriptive names for the tasks to be added.

        Returns:
            str: A confirmation message, e.g., "Added 3 new tasks."
        """
        count = 0
        for name in task_names:
            if not any(t['name'] == name for t in self.tasks):
                self.tasks.append({"name": name, "status": "pending", "result": None})
                count += 1
        return f"Added {count} new tasks."

    def get_next_pending_task(self) -> Task | None:
        """
        Retrieves the *first* task from the plan that is currently in 'pending' status.
        This is used to fetch the next step in the execution plan.

        Returns:
            Task | None: A Task object (dict) with 'name', 'status', and 'result' keys,
                          or None if no tasks are pending.
        """
        for task in self.tasks:
            if task["status"] == "pending":
                return task
        return None

    def update_task_status(self, task_name: str, status: Literal["completed", "failed"], result: str | None = None) -> str:
        """
        Updates the status and result of a specific task, identified by its unique name.
        This is crucial for tracking the plan's progress after a step is executed.

        Args:
            task_name (str): The exact name of the task to update (must match one from add_tasks).
            status (Literal["completed", "failed"]): The new status for the task.
            result (str | None, optional): An optional string describing the outcome or result
                                             of the task (e.g., a summary, an error message).

        Returns:
            str: A confirmation message (e.g., "Task 'Task Name' updated to completed.")
                 or an error message if the task is not found.
        """
        for task in self.tasks:
            if task["name"] == task_name:
                task["status"] = status
                if result is not None:
                    task["result"] = result
                return f"Task '{task_name}' updated to {status}."
        return f"Error: Task '{task_name}' not found."

    def list_all_tasks(self) -> list[str]:
        """
        Lists all tasks currently in the execution plan, along with their status and result.
        Useful for reviewing the overall plan and progress.

        Returns:
            list[str]: A list of formatted strings, where each string describes a task
                       (e.g., "- TaskName: completed (Result: Done.)").
        """
        if not self.tasks:
            return ["No tasks in the plan."]
        return [f"- {t['name']}: {t['status']} (Result: {t.get('result', 'N/A')})" for t in self.tasks]