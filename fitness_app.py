# Complicated task to test models and crewAI processes
# Sort of like a TodoMVC for local models and agent flows

import os

# set global vars
from dotenv import load_dotenv
from langchain.globals import set_debug

load_dotenv()
set_debug(True)

from crewai import Agent, Crew, Process, Task

# create a default language model
from langchain_openai import ChatOpenAI

default_llm = ChatOpenAI(
    model=os.environ.get("OPENAI_MODEL_NAME"),
)

# setup file logging and callback
from loguru import logger
from datetime import datetime

log_timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
log_file = f"{log_timestamp}-fitness_app.log"

logger.add(log_file, colorize=True, enqueue=True)


def custom_step_callback(output: str):
    """
    Custom callback function to log each step of the CrewAI execution.
    """
    print("--------------------------------------------------")
    print(output)
    print("--------------------------------------------------")
    logger.info(output)


# create manager agent
# to test if sequential still works

manager_agent = Agent(
    role="Manager",
    goal="Create a fitness app.",
    backstory="An experienced manager with a knack for understanding user needs and translating them into actionable development tasks.",
    verbose=True,
    allow_delegation=True,
    # llm=default_llm,
)

# overall objective: Create a fitness app

fitness_objective = """
  Let's create a fitness app! Break this down into tasks and delegate them to the best agents for the job.
  It should be a PWA with a focus on guiding and tracking workouts.
  It should be simple to use and visually appealing. Minimalist, clean styles preferred.
  It should focus on bodyweight exercises, but allow for adding equipment.
  It should provide workout routines, and allow customizing/saving new routines.
  It should have customizable timers for types of exercises, rest periods, and stretching.
  It should track progress over time and provide insights into workout habits.
  It should be easy to add new workouts and exercises to the app, with options to look up or import data.
  It should be able to provide a workout plan based on user input, including goals, time available, and equipment available.
  It should contain workout modifiers, like 2x speed, 2x reps, randoomly repeating an exercise, bonus challenge, etc.
  """

calculator_objective = """
  Create a calculator app that can add, subtract, multiply, and divide two numbers.
  """

objective = calculator_objective

initial_task = Task(
    description=objective,
    expected_output="A working application that meets all of the provided criteria. Iterate until it is complete.",
    # agent=manager_agent, for sequential
)

# create agent with file access

from tempfile import TemporaryDirectory
from langchain_community.agent_toolkits import FileManagementToolkit
from textwrap import dedent

working_directory = TemporaryDirectory()

file_tools = FileManagementToolkit(root_dir=str(working_directory.name)).get_tools()

file_agent = Agent(
    role="File System Agent",
    goal="Create and manage files and directories.",
    tools=file_tools,
    backstory=dedent(
        """\
    You are a file system agent with the ability to create, manage, and delete files and directories.
    You take your job very seriously and pay close attention to detail.
    Date and time stamps are always formatted ISO-8601 YYYY-MM-DD-HH-SS.
    """
    ),
    allow_delegation=False,
    verbose=True,
    # llm=default_llm,
)

# create agent with shell access

# disabling for now - moved to langchain-experimental

# from langchain.tools import ShellTool

# shell_tool = ShellTool()

# shell_agent = Agent(
# role="Shell Agent",
# goal="Execute shell commands and scripts.",
# memory=True,
# tools=shell_tool,
# backstory=dedent(
# """\
# You are a shell agent with the ability to execute shell commands and scripts on Ubuntu Bash.
# You take your job very seriously and pay close attention to detail.
# Never take an action that can harm the system.
# """
# ),n
# alnlow_delegation=False,
# verbose=True,
# )

# create agent with internet search tools

from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

wikipedia_tool = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())

from langchain_community.tools import DuckDuckGoSearchRun

duckduckgo_search_tool = DuckDuckGoSearchRun()

internet_research_agent = Agent(
    role="Internet Research Agent",
    goal="Search the internet for information.",
    tools=[wikipedia_tool, duckduckgo_search_tool],
    backstory=dedent(
        """\
        You are an internet research agent with the ability to search the internet for information.
        You take your job very seriously and pay close attention to detail.
        """
    ),
    allow_delegation=False,
    verbose=True,
    # llm=default_llm,
)

# h/t to @pythonbyte for the SDLC agent template here

product_manager_agent = Agent(
    role="Product Manager",
    goal="Identify user requirements and coordinate the software development process.",
    backstory="An experienced product manager with a knack for understanding user needs and translating them into actionable development tasks.",
    tools=[duckduckgo_search_tool],
    verbose=True,
    allow_delegation=True,
    # llm=default_llm,
)

qa_software_engineer_agent = Agent(
    role="QA Software Engineer",
    goal="Create a comprehensive test suite and implement the code for all the test cases. Use the file agent to read and save file data.",
    backstory="A meticulous QA engineer with a keen eye for detail and a passion for delivering high-quality software.",
    tools=[duckduckgo_search_tool],
    verbose=True,
    allow_delegation=True,
    # llm=default_llm,
)

sr_software_engineer_agent = Agent(
    role="Sr Software Engineer",
    goal="Write the code to implement the features based on requirements. Use the file agent to read and save file data.",
    backstory="A seasoned software engineer with a wealth of experience in developing software solutions across various domains.",
    tools=[duckduckgo_search_tool],
    verbose=True,
    allow_delegation=True,
    # llm=default_llm,
)

software_auditor_agent = Agent(
    role="Software Auditor",
    goal="Evaluate the software and ensure it meets the specified requirements.",
    backstory="A diligent auditor with a strong background in software development and quality assurance, committed to delivering high-quality software.",
    tools=[duckduckgo_search_tool],
    verbose=True,
    allow_delegation=True,
    # llm=default_llm,
)

# create a crew to achieve the objective

crew = Crew(
    agents=[
        file_agent,
        internet_research_agent,
        product_manager_agent,
        qa_software_engineer_agent,
        sr_software_engineer_agent,
        software_auditor_agent,
    ],  # shell_agent
    process=Process.hierarchical,
    tasks=[initial_task],
    manager_llm=default_llm,
    function_calling_llm=default_llm,
    step_callback=custom_step_callback,
)

# run the crew and log result

result = crew.kickoff()

print("--------------------------------------------------")
print("Final Result:\n")
print(result)

result_logfile = f"{log_timestamp}-fitness_app_final_result.log"

with open(result_logfile, "w") as f:
    f.write(result)
