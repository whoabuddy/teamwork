from crewai import Agent
from textwrap import dedent
from tools.file_tools import FileTools
from tools.task_tools import TaskManagerTools, TaskRepositoryTools


# Shared resource class for tasks
class TaskRepository:
    planner_tasks = []
    executor_tasks = []
    reviewer_tasks = []

    @classmethod
    def iterate_task_roles(cls):
        """Iterate over all task roles and their tasks."""
        for attr in dir(cls):
            if attr.endswith("_tasks"):
                yield attr.replace("_tasks", ""), getattr(cls, attr)

    @classmethod
    def get_all_tasks(cls):
        """Retrieve all tasks across all roles."""
        all_tasks = []
        for _, tasks in cls.iterate_task_roles():
            all_tasks.extend(tasks)
        return all_tasks

    @classmethod
    def get_tasks_for_role(cls, role):
        """Retrieve tasks for the given role."""
        return getattr(cls, f"{role}_tasks")


class PlanningCrew:

    @staticmethod
    def planner_agent():
        return Agent(
            role="Planner",
            goal="Read context and create a list of tasks to complete the objective(s).",
            tools=[
                TaskManagerTools.read_context,
                TaskRepositoryTools.get_current_tasks,
                TaskRepositoryTools.clear_all_tasks,
                TaskRepositoryTools.add_task_for_executor,
                TaskRepositoryTools.add_task_for_reviewer,
            ],
            backstory=dedent(
                """\
                    You are a top-notch planner with the ability to break down complex
                    objectives into smaller, actionable tasks. Your job is to read the
                    context and create a list of tasks for execution.
                """
            ),
            allow_delegation=True,
            verbose=True,
        )


class ExecutionCrew:

    @staticmethod
    def executor_agent():
        return Agent(
            role="Executor",
            goal="Complete assigned tasks",
            tools=[
                FileTools.append_to_file,
                FileTools.check_if_file_exists,
                FileTools.create_file,
                FileTools.list_files,
                TaskManagerTools.read_context,
                TaskRepositoryTools.add_task_for_executor,
            ],
            backstory=dedent(
                """\
                    You are an executor with a knack for getting things done. Your job
                    is to complete the tasks assigned to you by the Planner.
                """
            ),
            allow_delegation=False,
            verbose=True,
        )

    @staticmethod
    def reviewer_agent():
        return Agent(
            role="Reviewer",
            goal="Ensure tasks are completed satisfactorily.",
            tools=[
                FileTools.check_if_file_exists,
                FileTools.list_files,
                FileTools.read_file,
                TaskManagerTools.read_context,
                TaskRepositoryTools.add_task_for_planner,
            ],
            backstory=dedent(
                """\
                    You are a reviewer with an eye for detail. Your job is to verify the
                    completion and quality of all tasks completed, and to check that the
                    objective(s) listed in the context are met. If not, create a task
                    for the Planner to address the issue.
                """
            ),
            allow_delegation=False,
        )

    # think this could be done better with tools/flags
    @staticmethod
    def decider_agent():
        return Agent(
            role="Decider",
            goal="Respond only with yes or no given the provided context.",
            tools=[],
            backstory=dedent(
                """\
                    You are a specialized machine that can only output the words 'yes' or
                    'no'. Your job is to review the given context and decide whether the
                    objective has been met or not.
                """
            ),
            allow_delegation=False,
        )
