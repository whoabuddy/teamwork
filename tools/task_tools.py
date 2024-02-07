import hashlib
import os
from crewai import Task
from langchain.tools import tool
from pydantic import BaseModel, validator, ValidationError


# Model for adding a task
class AddTaskModel(BaseModel):
    description: str


# Model for updating a task's status
class UpdateTaskStatusModel(BaseModel):
    task_id: str
    new_status: str

    # Validator to ensure `new_status` is one of the valid statuses
    @validator("new_status")
    def validate_status(cls, v):
        valid_statuses = [
            TaskStatuses.TODO,
            TaskStatuses.ACTIVE,
            TaskStatuses.REVIEW,
            TaskStatuses.DONE,
        ]
        if v.upper() not in valid_statuses:
            raise ValueError(f"Invalid status: {v}, must be one of {valid_statuses}")
        return v.upper()


class TaskStatuses:
    # Define the statuses as class attributes for easy reference
    TODO = "TODO"
    ACTIVE = "ACTIVE"
    REVIEW = "REVIEW"
    DONE = "DONE"

    # A dictionary mapping each status to its description
    STATUS_DESCRIPTIONS = {
        TODO: "A task that needs to be completed",
        ACTIVE: "A task being actively worked on",
        REVIEW: "A task that needs human review (causing errors, need more info)",
        DONE: "A task that is completed",
    }

    @tool
    @staticmethod
    def get_valid_statuses(dummy_arg=None):
        """Returns a list of dictionaries with the names and descriptions of valid task statuses."""
        return [
            {"name": name, "description": description}
            for name, description in TaskStatuses.STATUS_DESCRIPTIONS.items()
        ]


class TaskRepositoryTools:
    @tool
    @staticmethod
    def get_current_tasks(role=None):
        """Retrieves the current tasks for a specified role or all roles if no role is specified."""
        from agents_v2 import TaskRepository

        tasks_summary = []

        try:
            if role:
                # Retrieve tasks for a specific role using the existing class method
                tasks = TaskRepository.get_tasks_for_role(role)
                if tasks:  # Check if any tasks were found for the role
                    tasks_summary.append(f"Tasks for {role.capitalize()}:")
                    tasks_summary.extend([task.description for task in tasks])
                else:
                    return f"No current tasks found for {role}."
            else:
                # Retrieve tasks for all roles
                tasks_summary.append("Tasks for all roles:")
                for role_name, tasks in TaskRepository.iterate_task_roles():
                    if tasks:  # Check if the role has any tasks
                        tasks_summary.append(f"Tasks for {role_name.capitalize()}:")
                        tasks_summary.extend([task.description for task in tasks])

            if (
                len(tasks_summary) <= 1
            ):  # Adjusted check to account for the header string
                return "No current tasks found."

            return "\n".join(tasks_summary)
        except Exception as e:
            return f"Error retrieving tasks: {e}"

    @tool
    @staticmethod
    def clear_all_tasks(dummy_arg=None):
        """Clears all tasks from the shared task lists using the task roles iterator."""
        from agents_v2 import TaskRepository

        # Iterate over all task roles and clear their respective task lists
        for _, tasks in TaskRepository.iterate_task_roles():
            tasks.clear()  # Clear the tasks list for each role

        return "All tasks cleared."

    @tool
    @staticmethod
    def add_task_for_planner(description):
        """Adds a task with the provided description for the planner."""
        from agents_v2 import PlanningCrew, TaskRepository

        try:
            validated_input = AddTaskModel(description=description)
            new_task = Task(
                description=validated_input.description,
                agent=PlanningCrew.planner_agent(),
            )
            TaskRepository.planner_tasks.append(new_task)
            return f"Task '{validated_input.description}' added for the planner."
        except ValidationError as e:
            return f"Validation Error: {e}"

    @tool
    @staticmethod
    def add_task_for_executor(description):
        """Adds a task with the provided description for the executor."""
        from agents_v2 import ExecutionCrew, TaskRepository

        try:
            validated_input = AddTaskModel(description=description)
            new_task = Task(
                description=validated_input.description,
                agent=ExecutionCrew.executor_agent(),
            )
            TaskRepository.executor_tasks.append(new_task)
            return f"Task '{validated_input.description}' added for the executor."
        except ValidationError as e:
            return f"Validation Error: {e}"

    @tool
    @staticmethod
    def add_task_for_reviewer(description):
        """Adds a task with the provided description for the reviewer."""
        from agents_v2 import ExecutionCrew, TaskRepository

        try:
            validated_input = AddTaskModel(description=description)
            new_task = Task(
                description=validated_input.description,
                agent=ExecutionCrew.reviewer_agent(),
            )
            TaskRepository.reviewer_tasks.append(new_task)
            return f"Task '{validated_input.description}' added for the reviewer."
        except ValidationError as e:
            return f"Validation Error: {e}"

    @tool
    @staticmethod
    def add_task_for_decider(description):
        """Adds a task with the provided description for the decider."""
        from agents_v2 import ExecutionCrew, TaskRepository

        try:
            validated_input = AddTaskModel(description=description)
            new_task = Task(
                description=validated_input.description,
                agent=ExecutionCrew.decider_agent(),
            )
            TaskRepository.shared_executor_tasks.append(new_task)
            return f"Task '{validated_input.description}' added for the decider."
        except ValidationError as e:
            return f"Validation Error: {e}"


class CrewTaskTools:
    @tool
    @staticmethod
    def add_task_for_planner(description):
        """Adds a task with the provided description for the planner."""
        from agents import CoordinationCrew

        try:
            validated_input = AddTaskModel(description=description)
            new_task = Task(
                description=validated_input.description,
                agent=CoordinationCrew.planner_agent(),
            )
            CoordinationCrew.add_dynamic_task(new_task)
            return f"Task '{validated_input.description}' added for the planner."
        except ValidationError as e:
            return f"Validation Error: {e}"

    @tool
    @staticmethod
    def add_task_for_executor(description):
        """Adds a task with the provided description for the executor."""
        from agents import CoordinationCrew

        try:
            validated_input = AddTaskModel(description=description)
            new_task = Task(
                description=validated_input.description,
                agent=CoordinationCrew.executor_agent(),
            )
            CoordinationCrew.add_dynamic_task(new_task)
            return f"Task '{validated_input.description}' added for the executor."
        except ValidationError as e:
            return f"Validation Error: {e}"

    @tool
    @staticmethod
    def add_task_for_reviewer(description):
        """Adds a task with the provided description for the reviewer."""
        from agents import CoordinationCrew

        try:
            validated_input = AddTaskModel(description=description)
            new_task = Task(
                description=validated_input.description,
                agent=CoordinationCrew.reviewer_agent(),
            )
            CoordinationCrew.add_dynamic_task(new_task)
            return f"Task '{validated_input.description}' added for the reviewer."
        except ValidationError as e:
            return f"Validation Error: {e}"


class TaskManagerTools:
    CONTEXT_FILE_PATH = "./context.md"
    TASK_FILE_PATH = "./tasks.md"

    @tool
    @staticmethod
    def read_context(dummy_arg=None):
        """Reads the context from the markdown file and returns it as a string."""
        if not os.path.exists(TaskManagerTools.CONTEXT_FILE_PATH):
            return "Context file does not exist."

        with open(TaskManagerTools.CONTEXT_FILE_PATH, "r") as file:
            return file.read()

    @tool
    @staticmethod
    def read_tasks(dummy_arg=None):
        """Reads tasks from the markdown file and returns them as a list of dictionaries."""
        tasks = []
        if not os.path.exists(TaskManagerTools.TASK_FILE_PATH):
            return "Task file does not exist."

        with open(TaskManagerTools.TASK_FILE_PATH, "r") as file:
            for line in file:
                if line.startswith("- ["):
                    status, _, task_content = line.strip().partition("] ")
                    task_id, _, description = task_content.partition(": ")
                    tasks.append(
                        {
                            "id": task_id,
                            "status": status[2:-1],
                            "description": description,
                        }
                    )

        return tasks

    @tool
    @staticmethod
    def add_task(description):
        """Adds a new task with the given description to the markdown file."""
        try:
            validated_input = AddTaskModel(description=description)
            task_id = TaskManagerTools._generate_task_id(validated_input.description)
            with open(TaskManagerTools.TASK_FILE_PATH, "a") as file:
                file.write(f"- [TODO] {task_id}: {validated_input.description}\n")
            return f"Task {task_id} added."
        except ValidationError as e:
            return f"Validation Error: {e}"

    @tool
    @staticmethod
    def update_task_status(task_id, new_status):
        """Updates the status of a task identified by `task_id`."""
        try:
            validated_input = UpdateTaskStatusModel(
                task_id=task_id, new_status=new_status
            )
            tasks_updated = []
            with open(TaskManagerTools.TASK_FILE_PATH, "r") as file:
                tasks = file.readlines()

            with open(TaskManagerTools.TASK_FILE_PATH, "w") as file:
                for line in tasks:
                    if f"{validated_input.task_id}:" in line:
                        parts = line.split(": ", 1)
                        line = f"{parts[0].split(' ', 1)[0]} [{validated_input.new_status.upper()}]: {parts[1]}"
                    tasks_updated.append(line)

                file.writelines(tasks_updated)
            return f"Task {validated_input.task_id} status updated to {validated_input.new_status.upper()}."
        except ValidationError as e:
            return f"Validation Error: {e}"

    @staticmethod
    def _generate_task_id(description):
        """Generates a task ID based on a hash of the task description."""
        hash_object = hashlib.sha256(description.encode())
        return hash_object.hexdigest()  # Use the full hash for the ID
