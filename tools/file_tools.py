import os
from langchain.tools import tool
from pydantic import BaseModel, validator, constr, ValidationError


class PathModel(BaseModel):
    path: constr(strip_whitespace=True)


# expect two parameters
# 1. filename as string
# 2. data as string
# both are required
class AppendFileModel(BaseModel):
    filename: str
    data: str


class WriteFileModel(BaseModel):
    data: str

    @validator("data")
    def validate_data(cls, v):
        parts = v.split("|", 1)
        if len(parts) != 2:
            raise ValueError("Data must contain a path and content separated by '|'")
        path, content = parts
        if not path.strip():
            raise ValueError("Path cannot be empty")
        return v


class FileTools:

    @tool
    @staticmethod
    def get_current_directory(dummy_arg=None):
        """Returns the current working directory."""
        try:
            current_dir = os.getcwd()
            return f"Current directory: {current_dir}"
        except Exception as e:
            return f"Error getting current directory: {e}"

    @tool
    @staticmethod
    def change_directory(path):
        """Changes the current working directory to the given path."""
        try:
            validated_input = PathModel(path=path)
            os.chdir(validated_input.path)
            return f"Changed directory to {validated_input.path}."
        except ValidationError as e:
            return f"Validation Error: {e}"
        except Exception as e:
            return f"Error changing directory: {e}"

    @tool
    @staticmethod
    def create_file(path):
        """Equivalent to the Unix 'touch' command. Creates an empty file if it does not exist, or updates its last modified time if it does."""
        try:
            validated_input = PathModel(path=path)
            # Open the file in append mode and immediately close it to update last access and modification times without changing content
            with open(validated_input.path, "a"):
                pass
            return f"File '{validated_input.path}' touched successfully."
        except ValidationError as e:
            return f"Validation Error: {e}"
        except Exception as e:
            return f"Error touching file: {e}"

    @tool
    @staticmethod
    def create_directory(path):
        """Creates a new directory at the specified path."""
        try:
            validated_input = PathModel(path=path)
            os.makedirs(validated_input.path, exist_ok=True)
            return f"Directory '{validated_input.path}' created successfully."
        except ValidationError as e:
            return f"Validation Error: {e}"
        except Exception as e:
            return f"Error creating directory: {e}"

    @tool
    @staticmethod
    def check_if_file_exists(path):
        """Checks if a file or directory exists at the specified path."""
        try:
            validated_input = PathModel(path=path)
            exists = os.path.exists(validated_input.path)
            return f"{'Exists' if exists else 'Does not exist'}: {validated_input.path}"
        except ValidationError as e:
            return f"Validation Error: {e}"

    @tool
    @staticmethod
    def list_files(dummy_arg=None):
        """Lists files in the current working directory."""
        try:
            files = os.listdir()
            return f"Files in the current directory: {', '.join(files)}"
        except Exception as e:
            return f"Error listing files: {e}"

    @tool
    @staticmethod
    def read_file(path):
        """Reads the content of a file at the given path."""
        try:
            validated_input = PathModel(path=path)
            with open(validated_input.path, "r") as f:
                content = f.read()
            return content
        except ValidationError as e:
            return f"Validation Error: {e}"
        except Exception as e:
            return f"Error reading file: {e}"

    @tool
    @staticmethod
    def append_to_file(input_data: dict):
        """Appends text to a file with the given name."""
        try:
            # Extract filename and data from the input dictionary
            filename = input_data.get("filename")
            data = input_data.get("data")

            # Validate the input using AppendFileModel
            validated_data = AppendFileModel(filename=filename, data=data)

            with open(validated_data.filename, "a") as f:
                f.write(
                    validated_data.data + "\n"
                )  # Adding a newline for clarity in the appended content
            return f"Appended content to {validated_data.filename}."
        except ValidationError as e:
            return f"Validation Error: {e.errors()}"
        except Exception as e:
            return f"Error appending to file: {e}"

    @tool
    @staticmethod
    def write_file(data):
        """Writes content to a file at the given path."""
        try:
            validated_data = WriteFileModel(data=data)
            path, content = validated_data.data.split("|")
            path = path.strip().replace("`", "")
            if not path.startswith("./context"):
                path = f"./context/{path}"
            with open(path, "w") as f:
                f.write(content)
            return f"File written to {path}."
        except ValidationError as e:
            return f"Validation Error: {e.errors()}"
        except Exception as e:
            return f"Error writing file: {e}"

    # @tool
    # @staticmethod
    # def move_or_rename_file(source, destination):
    #    """Moves or renames a file or directory from source to destination."""
    #    try:
    #        os.rename(source, destination)
    #        return f"Moved/Renamed '{source}' to '{destination}'."
    #    except Exception as e:
    #        return f"Error moving/renaming: {e}"
