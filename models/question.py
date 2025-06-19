import json

class Question:
    """
    Represents a single question in a quiz.

    Attributes:
        question_text (str): The text of the question.
        options (list): A list of strings, where each string is a possible answer option.
        correct_answer_index (int): The 0-based index of the correct answer in the 'options' list.
    """

    def __init__(self, question_text: str, options: list, correct_answer_index: int):
        """
        Initializes a new Question object.

        Args:
            question_text (str): The text of the question.
            options (list): A list of possible answer options (strings).
            correct_answer_index (int): The 0-based index of the correct answer.

        Raises:
            ValueError: If inputs are invalid (e.g., empty text, no options, invalid index).
        """
        if not isinstance(question_text, str) or not question_text.strip():
            raise ValueError("Question text cannot be empty.")
        if not isinstance(options, list) or not options:
            raise ValueError("Options must be a non-empty list.")
        if not all(isinstance(opt, str) and opt.strip() for opt in options):
            raise ValueError("All options must be non-empty strings.")
        if not isinstance(correct_answer_index, int) or not (0 <= correct_answer_index < len(options)):
            raise ValueError("Correct answer index is out of bounds or not an integer.")

        self.question_text = question_text.strip()
        self.options = [opt.strip() for opt in options]
        self.correct_answer_index = correct_answer_index

    def display(self) -> str:
        """
        Returns a formatted string for displaying the question and its options.

        Returns:
            str: A string representation of the question.
        """
        display_str = f"Pytanie: {self.question_text}\n"
        for i, option in enumerate(self.options):
            display_str += f"  {i + 1}. {option}\n"
        return display_str

    def is_correct(self, user_answer_index: int) -> bool:
        """
        Checks if the user's provided answer index matches the correct answer.

        Args:
            user_answer_index (int): The 0-based index of the user's chosen answer.

        Returns:
            bool: True if the answer is correct, False otherwise.
        """
        return user_answer_index == self.correct_answer_index

    def to_dict(self) -> dict:
        """
        Converts the Question object to a dictionary for JSON serialization.

        Returns:
            dict: A dictionary representation of the question.
        """
        return {
            "question_text": self.question_text,
            "options": self.options,
            "correct_answer_index": self.correct_answer_index
        }

    @classmethod
    def from_dict(cls, data: dict):
        """
        Creates a Question object from a dictionary (for JSON deserialization).

        Args:
            data (dict): A dictionary containing question data.

        Returns:
            Question: A new Question object.
        """
        return cls(
            question_text=data["question_text"],
            options=data["options"],
            correct_answer_index=data["correct_answer_index"]
        )

    def __str__(self):
        """
        Returns a human-readable string representation of the Question object.
        """
        return f"Pytanie: '{self.question_text}', Opcje: {self.options}, Poprawna: {self.options[self.correct_answer_index]}"

    def __repr__(self):
        """
        Returns an official string representation of the Question object for debugging.
        """
        return f"Question('{self.question_text}', {self.options}, {self.correct_answer_index})"
