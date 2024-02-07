from crewai import Crew, Process, Task
from agents_v2 import TaskRepository, PlanningCrew, ExecutionCrew


# Function to initialize and kick off the crew
def engage_crew_with_tasks():

    # define agents
    planner = PlanningCrew.planner_agent()
    executor = ExecutionCrew.executor_agent()
    reviewer = ExecutionCrew.reviewer_agent()
    # decider = ExecutionCrew.decider_agent()

    # define the initial task for the planner
    initial_task = Task(
        description="Achieve the objective by breaking it down into small, actionable tasks that can be carried out by other agents.",
        agent=planner,
    )
    # add the task to the shared task list for the planner
    TaskRepository.planner_tasks.append(initial_task)

    # loop as long as the planner has tasks
    while TaskRepository.planner_tasks:
        # planner has a tool to read the context
        # planner has a tool to read the current shared tasks
        # planner has a tool to create tasks for the executor, reviewer, and decider agents
        # tasks are Task() objects that should be added to tasks list
        planning_crew = Crew(
            agents=[planner],
            process=Process.sequential,
            tasks=TaskRepository.planner_tasks,
            verbose=True,
        )

        # run the crew
        planning_result = planning_crew.kickoff()

        # clear the planner task list
        TaskRepository.planner_tasks.clear()

        # print the result
        print("--------------------------------------------------")
        print("Planning Crew Result:")
        print(planning_result)
        print("--------------------------------------------------")
        print("Planner Tasks:")
        for task in TaskRepository.planner_tasks:
            print(f"- {task.description}")
        print("Executor Tasks:")
        for task in TaskRepository.executor_tasks:
            print(f"- {task.description}")
        print("Reviewer Tasks:")
        for task in TaskRepository.reviewer_tasks:
            print(f"- {task.description}")
        print("--------------------------------------------------")

        # check if executor crew has tasks
        if TaskRepository.executor_tasks:

            # executor has file tools, can read context, add task for itself
            # reviewer has file tools, can read context, add task for planner
            execution_crew = Crew(
                agents=[executor, reviewer],
                process=Process.sequential,
                tasks=TaskRepository.executor_tasks,
                verbose=True,
            )

            # run the crew
            execution_result = execution_crew.kickoff()

            # clear the executor task list
            TaskRepository.executor_tasks.clear()

            # print the result
            print("--------------------------------------------------")
            print("Execution Crew Result:")
            print(execution_result)
            print("--------------------------------------------------")
            print("Planner Tasks:")
            for task in TaskRepository.planner_tasks:
                print(f"- {task.description}")
            print("Executor Tasks:")
            for task in TaskRepository.executor_tasks:
                print(f"- {task.description}")
            print("Reviewer Tasks:")
            for task in TaskRepository.reviewer_tasks:
                print(f"- {task.description}")
            print("--------------------------------------------------")


if __name__ == "__main__":
    engage_crew_with_tasks()
