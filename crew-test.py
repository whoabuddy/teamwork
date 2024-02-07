# engagement.py
from agents import CoordinationCrew


# Function to initialize and kick off the crew
def engage_crew_with_tasks():
    # Initialize an instance of CoordinationCrew
    coordination_crew = CoordinationCrew()

    # Kick off the crew's execution process
    result = coordination_crew.run_crew()

    # Handle the result
    print("Crew execution completed. Results:")
    print(result)


if __name__ == "__main__":
    engage_crew_with_tasks()
