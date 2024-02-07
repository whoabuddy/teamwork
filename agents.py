from textwrap import dedent
from crewai import Agent, Task, Crew, Process
from tools.file_tools import FileTools
from tools.task_tools import TaskManagerTools, TaskStatuses, CrewTaskTools


def append_result_to_context_md(result):
    # Open context.md in append mode
    with open("context.md", "a") as file:
        # Append the separator and the result to the file
        file.write(f"---\n{result}\n")


class TaskExecutorCrew:

    @staticmethod
    def planner_agent():
        return Agent(
            role="Planner",
            goal="Read context and create a list of tasks to complete the objective(s).",
            tools=[
                TaskManagerTools.read_context,
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

    @staticmethod
    def executor_agent():
        return Agent(
            role="Executor",
            goal="Complete assigned tasks",
            tools=[
                FileTools.create_file,
                FileTools.check_existence,
                FileTools.list_files,
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

    def run_crew(self):
        # Initialize Agents
        planner = self.planner_agent()
        executor = self.executor_agent()

        # Define the initial Task for the planner
        initial_task = Task(
            description="Achieve the objective by breaking it down into small, actionable tasks.",
            agent=planner,
        )

        # Initialize tasks list with the initial task
        tasks = [initial_task]

        crew = Crew(
            agents=[planner, executor],
            tasks=tasks,
            process=Process.sequential,
            verbose=True,
        )

        result = crew.kickoff()

        return result


class TaskReviewerCrew:
    @staticmethod
    def reviewer_agent():
        return Agent(
            role="Reviewer",
            goal="Ensure tasks are completed satisfactorily and update the task list.",
            tools=[
                FileTools.read_file,
                FileTools.check_existence,
                FileTools.list_files,
                TaskManagerTools.read_context,
            ],
            backstory=dedent(
                """\
                  You are a reviewer with an eye for detail. Your job is to verify the
                  completion and quality of all tasks completed, and to check that the
                  objective(s) listed in the context are met.
                """
            ),
            allow_delegation=False,
            verbose=True,
        )

    def run_crew(self):
        # Initialize Agents
        reviewer = self.reviewer_agent()

        # Define the initial Task for the planner
        initial_task = Task(
            description="Achieve the objective by breaking it down into small, actionable tasks.",
            agent=reviewer,
        )

        # Initialize tasks list with the initial task
        tasks = [initial_task]

        crew = Crew(
            agents=[reviewer],
            tasks=tasks,
            process=Process.sequential,
            verbose=True,
        )

        result = crew.kickoff()

        return result


class CoordinationCrew:
    dynamic_tasks = []

    @classmethod
    def add_dynamic_task(cls, task):
        cls.dynamic_tasks.append(task)

    @staticmethod
    def planner_agent():
        return Agent(
            role="Planner",
            goal="Read context and create a list of tasks for execution",
            tools=[
                TaskManagerTools.read_context,
                CrewTaskTools.add_task_for_planner,
                CrewTaskTools.add_task_for_executor,
                CrewTaskTools.add_task_for_reviewer,
            ],
            backstory=dedent(
                """\
                    As the Planner, your job is to use the available context create
                    the necessary tasks to complete the objective(s) and assigning
                    them to the appropriate agents for completion.
                """
            ),
            allow_delegation=True,
            verbose=True,
        )

    @staticmethod
    def executor_agent():
        return Agent(
            role="Executor",
            goal="Complete assigned tasks",
            tools=[
                FileTools.get_current_directory,
                FileTools.change_directory,
                FileTools.create_directory,
                FileTools.create_file,
                FileTools.check_existence,
                FileTools.list_files,
            ],
            backstory=dedent(
                """\
                    As the Executor, you are responsible for carrying out the tasks 
                    delegated by the Planner. Your work is critical in making tangible 
                    progress towards the crew's objectives.
                """
            ),
            allow_delegation=False,
            verbose=True,
        )

    @staticmethod
    def reviewer_agent():
        return Agent(
            role="Reviewer",
            goal="Ensure tasks are completed satisfactorily and update the task list",
            tools=[
                FileTools.get_current_directory,
                FileTools.change_directory,
                FileTools.read_file,
                FileTools.check_existence,
                FileTools.list_files,
                CrewTaskTools.add_task_for_planner,
                TaskStatuses.get_valid_statuses,
            ],
            backstory=dedent(
                """\
                  As the Reviewer, your role is to verify the completion and quality
                  of all tasks completed, and to check that the objective(s) listed
                  in the context are met.
                """
            ),
            allow_delegation=False,
            verbose=True,
        )

    def run_crew(self):
        # Initialize Agents
        planner = self.planner_agent()
        executor = self.executor_agent()
        reviewer = self.reviewer_agent()

        # Define the initial Task for the planner
        initial_task = Task(
            description="Achieve the objective by breaking it down into small, actionable tasks.",
            agent=planner,
        )

        # Initialize tasks list with the initial task
        tasks = [initial_task]

        # Loop until the project is complete
        while True:
            print("--Initializing Crew--")
            # Include dynamically generated tasks into the tasks list
            tasks.extend(self.dynamic_tasks)
            self.dynamic_tasks.clear()  # Clear dynamic_tasks for the next iteration
            # Initialize or update Crew with the current tasks
            crew = Crew(
                agents=[planner, executor, reviewer],
                tasks=tasks,
                process=Process.sequential,
                verbose=True,
            )

            print("--Crew Initialized, Kicking off operation--")
            # Execute the crew process
            result = crew.kickoff()

            print("--Crew Execution Completed, Updating Context--")
            # Append the result to context.md
            append_result_to_context_md(result)

            # Define a review task to assess project completion
            review_task = Task(
                description="You are a computer program that can only return true or false. Review the updated context and determine if the project objectives have been met.",
                agent=reviewer,
            )
            # Execute the review task
            print("--Reviewing Outcome--")
            review_result = review_task.execute()

            if review_result.lower() == "true":
                print("--Project is complete!--")
                break  # Exit the loop if the project is complete

            print("--Clearing tasks, starting over--")
            tasks.clear()  # Clear the tasks list

            # The Planner agent will generate new tasks based on the updated context at the start of the next loop iteration
