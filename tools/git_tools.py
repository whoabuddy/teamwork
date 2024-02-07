import subprocess
from langchain.tools import tool


class GitTools:

    @tool
    @staticmethod
    def git_status():
        """Displays the working tree status."""
        return GitTools.run_git_command("git status")

    @tool
    @staticmethod
    def git_branch():
        """Lists all branches."""
        return GitTools.run_git_command("git branch")

    @tool
    @staticmethod
    def git_commit(message):
        """Stages all changes and creates a commit with the given message."""
        GitTools.run_git_command("git add -A")
        return GitTools.run_git_command(f'git commit -m "{message}"')

    @tool
    @staticmethod
    def git_diff():
        """Shows changes between commits, commit and working tree, etc."""
        return GitTools.run_git_command("git diff")

    @tool
    @staticmethod
    def git_log(n=0, oneline=False):
        """Shows the commit logs. 'n' limits the number of entries. 'oneline' shows a brief summary."""
        command = "git log"
        if n > 0:
            command += f" -n {n}"
        if oneline:
            command += " --oneline"
        return GitTools.run_git_command(command)

    @tool
    @staticmethod
    def git_push():
        """Updates remote refs along with associated objects."""
        return GitTools.run_git_command("git push")

    @tool
    @staticmethod
    def git_pull():
        """Fetches from and integrates with another repository or a local branch."""
        return GitTools.run_git_command("git pull")

    @staticmethod
    def run_git_command(command):
        """Utility method to run a git command and return its output or error."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            return result.stdout or "Command executed successfully."
        except subprocess.CalledProcessError as e:
            return f"Error executing command: {e.stderr}"
