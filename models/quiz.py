class Quiz:
    """
    Represents a collection of questions that form a quiz.

    Attributes:
        title (str): The title of the quiz.
        description (str): An optional description of the quiz.
        questions (list): A list of Question objects belonging to this quiz.
    """

    def __init__(self, title: str, description: str = "", questions: list = None):
        """
        Initializes a new Quiz object.

        Args:
            title (str): The title of the quiz.
            description (str, optional): An optional description. Defaults to "".
            questions (list, optional): A list of Question objects. Defaults to an empty list.
        """
        if not isinstance(title, str) or not title.strip():
            raise ValueError("Quiz title cannot be empty.")

        self.title = title.strip()
        self.description = description.strip() if description else ""
        self.questions = []
        if questions:
            for q in questions:
                if not isinstance(q, Question):
                    raise TypeError("All items in 'questions' must be Question objects.")
                self.questions.append(q)

    def add_question(self, question: Question):
        """
        Adds a Question object to the quiz.

        Args:
            question (Question): The Question object to add.

        Raises:
            TypeError: If the provided item is not a Question object.
        """
        if not isinstance(question, Question):
            raise TypeError("Only Question objects can be added to the quiz.")
        self.questions.append(question)

    def remove_question(self, index: int):
        """
        Removes a question from the quiz by its index.

        Args:
            index (int): The 0-based index of the question to remove.

        Raises:
            IndexError: If the index is out of bounds.
        """
        if not isinstance(index, int):
            raise TypeError("Index must be an integer.")
        if not (0 <= index < len(self.questions)):
            raise IndexError("Question index is out of bounds.")
        self.questions.pop(index)

    def to_dict(self) -> dict:
        """
        Converts the Quiz object to a dictionary for JSON serialization.
        Each question is also converted to its dictionary representation.

        Returns:
            dict: A dictionary representation of the quiz.
        """
        return {
            "title": self.title,
            "description": self.description,
            "questions": [q.to_dict() for q in self.questions]
        }

    @classmethod
    def from_dict(cls, data: dict):
        """
        Creates a Quiz object from a dictionary (for JSON deserialization).
        Converts dictionary representations of questions back into Question objects.

        Args:
            data (dict): A dictionary containing quiz data.

        Returns:
            Quiz: A new Quiz object.
        """
        questions = [Question.from_dict(q_data) for q_data in data.get("questions", [])]
        return cls(
            title=data["title"],
            description=data.get("description", ""),
            questions=questions
        )

    def __str__(self):
        """
        Returns a human-readable string representation of the Quiz object.
        """
        return f"Quiz: '{self.title}' ({len(self.questions)} pytań)"

    def __repr__(self):
        """
        Returns an official string representation of the Quiz object for debugging.
        """
        return f"Quiz('{self.title}', '{self.description}', {self.questions})"
