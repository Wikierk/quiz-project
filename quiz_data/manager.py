import json
import os
from models.question import Question
from models.quiz import Quiz

class QuizDataManager:
    """
    Manages loading and saving Quiz objects to/from JSON files.

    This class provides static methods for handling file operations related to quizzes,
    including error handling for common file-system and JSON parsing issues.
    """

    @staticmethod
    def save_quiz(quiz: Quiz, filename: str, directory: str = "data/quiz_examples"):
        """
        Saves a Quiz object to a JSON file.

        The quiz object is first converted to a dictionary using its to_dict() method.
        The file will be saved in the specified directory. If the directory does not exist,
        it will be created.

        Args:
            quiz (Quiz): The Quiz object to be saved.
            filename (str): The name of the file (e.g., "my_quiz.json").
            directory (str): The directory where the quiz file will be saved.
                             Defaults to "data/quiz_examples".

        Raises:
            IOError: If there's an issue writing to the file (e.g., permissions).
            TypeError: If the provided object is not a Quiz instance.
        """
        if not isinstance(quiz, Quiz):
            raise TypeError("Only Quiz objects can be saved.")
        if not filename.endswith(".json"):
            filename += ".json" # Ensure filename has .json extension

        # Ensure the directory exists
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
                print(f"Created directory: {directory}")
            except OSError as e:
                print(f"Error creating directory {directory}: {e}")
                raise IOError(f"Could not create directory {directory}.") from e

        file_path = os.path.join(directory, filename)

        try:
            # Convert Quiz object to a dictionary
            quiz_data = quiz.to_dict()
            with open(file_path, 'w', encoding='utf-8') as f:
                # Use indent for pretty-printing JSON
                json.dump(quiz_data, f, indent=4, ensure_ascii=False)
            print(f"Quiz '{quiz.title}' saved successfully to {file_path}")
        except IOError as e:
            print(f"Error saving quiz to {file_path}: {e}")
            raise IOError(f"Failed to write quiz to file: {file_path}") from e
        except Exception as e: # Catch any other unexpected errors during serialization
            print(f"An unexpected error occurred while saving quiz: {e}")
            raise

    @staticmethod
    def load_quiz(filename: str, directory: str = "data/quiz_examples") -> Quiz:
        """
        Loads a Quiz object from a JSON file.

        The JSON data is read from the file and then converted back into a Quiz object
        using the Quiz.from_dict() method.

        Args:
            filename (str): The name of the file (e.g., "my_quiz.json").
            directory (str): The directory where the quiz file is located.
                             Defaults to "data/quiz_examples".

        Returns:
            Quiz: The loaded Quiz object.

        Raises:
            FileNotFoundError: If the specified file does not exist.
            json.JSONDecodeError: If the file content is not valid JSON.
            KeyError: If the JSON structure is missing required keys for Quiz/Question.
            Exception: For other unexpected errors during loading.
        """
        if not filename.endswith(".json"):
            filename += ".json" # Ensure filename has .json extension

        file_path = os.path.join(directory, filename)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Quiz file not found: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                quiz_data = json.load(f)
            # Convert dictionary data back to Quiz object
            quiz = Quiz.from_dict(quiz_data)
            print(f"Quiz '{quiz.title}' loaded successfully from {file_path}")
            return quiz
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {file_path}: {e}")
            raise json.JSONDecodeError(f"Invalid JSON format in file: {file_path}", e.doc, e.pos) from e
        except KeyError as e:
            print(f"Missing required data in quiz file {file_path}: {e}")
            raise KeyError(f"Corrupt quiz file. Missing key: {e}") from e
        except Exception as e: # Catch any other unexpected errors during deserialization
            print(f"An unexpected error occurred while loading quiz from {file_path}: {e}")
            raise

    @staticmethod
    def list_available_quizzes(directory: str = "data/quiz_examples") -> list[str]:
        """
        Lists all available quiz files (JSON files) in the specified directory.

        Args:
            directory (str): The directory to search for quiz files.
                             Defaults to "data/quiz_examples".

        Returns:
            list[str]: A list of filenames (without the .json extension)
                       representing available quizzes. Returns an empty list
                       if the directory does not exist or contains no quizzes.
        """
        if not os.path.exists(directory):
            return [] # Return empty list if directory doesn't exist

        quiz_files = []
        try:
            for item in os.listdir(directory):
                if item.endswith(".json"):
                    quiz_files.append(os.path.splitext(item)[0]) # Add filename without extension
            quiz_files.sort() # Sort alphabetically for consistent display
        except OSError as e:
            print(f"Error listing files in directory {directory}: {e}")
            # Optionally re-raise if this error is critical for the application flow
        return quiz_files