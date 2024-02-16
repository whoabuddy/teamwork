# A self-generating framework for CrewAI

overall_goal = """
  Let's create a fitness app!
  It should be a PWA with a focus on guiding and tracking workouts.
  It should be simple to use and visually appealing. Minimalist, clean styles preferred.
  It should focus on bodyweight exercises, but allow for adding equipment.
  It should provide workout routines, and allow customizing/saving new routines.
  It should track progress over time and provide insights into workout habits.
  It should be easy to add new workouts and exercises to the app.
  It should be able to provide a workout plan based on user input, including goals, time available, and equipment available.
  It should contain workout modifiers, like 2x speed, 2x reps, randoomly repeating an exercise, bonus challenge, etc.
"""

##### DO NOT EDIT BELOW THIS LINE #####


from crewai import Agent, Crew, Task
from typing import List

# Define shared data structure

class ProjectPlan:
  goal: str
  objectives: List[str]
  style_guide: List[str]
  tech_stack: List[str]


def kick_off_generative_crew():

  initial_task = Task(description=overall_goal)

  planner_agent = Agent(

  )

# We have a general task/request, input from the user. Ideally it would be a well-formed, clear description of the required outcome.

# We have a planner agent who orchestrates what happens next:

# CREATE AGENTS
# (using available tools for now, maybe generate later)

# Task: Create and set a list of team roles you need to complete the assigned task. You have access to any and all necessary resources to complete this project.
# Tool: set_team_roles(team_role_list: List[str]) -> None
# - sets global variable for team roles
# - validate against Pydantic model for List[str]
# Final result: List of team roles stored in a global variable.

# For each team role: (name = role for now)

# Task: These are your requested team roles to complete the assigned task: {team_role_list}. For {team_role}, create and set the missing information:
#   Tool: set_friendly_name(name: str) -> None
#   Tool: set_goal(goal: str) -> None
#   Tool: set_backstory(backstory: str) -> None
#   Tool: set_memory(has_memory: bool) -> None
#   Tool: get_all_tools(dummy_arg: None) -> List[str]
#   Tool: add_tools(tools: List[str]) -> None
#   Tool: set_agent_delegation(allow_delegation: bool) -> None
# Final result: Agent objects for each team role with the requested information set, stored in a global variable.
# - how to track variables for each team role? easy tool to see what is/isn't set?
# - how to approach this in an iterate-until-done way?

# CREATE PROJECT PLAN

# project: goal, objective(s), style guide, tech stack

# Task: Create a project plan based on input from the user.
# (this is an object to help provide context later)
# Tool: set_project_goal(goal: str) -> None # sets global variable for project goal
# Tool: add_project_objective(objective: str) -> None # adds to global list of project objectives
# Tool: add_to_style_guide(style_rule: str) -> None # sets global list of strings for style guide
# Tool: add_to_tech_stack(tech: str) -> None # sets global list of strings for tech stack
# General Tool: move_on_to_next_step(dummy_arg: None) -> None
# - recursive method to build up an external variable to be used later
# - example: while false, show user input, project goal, project objectives + option to add objective
# - example: while false, show user input, project goal, project objectives, style guide + option to add style rule

# CREATE TASKS

# Review until it thinks it's done:
# - list project plan as context
# - list agents+roles as context
# - list current tasks as context
# Tool: add_task(task: str) -> None

# CREATE CREW

# Use new Heierarchical type to create a manager
# assign all agents defined earlier
# assign all tasks defined earlier
# kick off the crew
# how to make sure they always have best context?

# ITERATIVE APPROACH
# - this is the object we are creating
# - these are the current values
# - tools to set each value
# - tool to move on to next step or mark object as complete