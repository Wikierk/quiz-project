
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.question import Question
from models.quiz import Quiz

class TestQuestion(unittest.TestCase):
    """
    Unit tests for the Question class.
    Covers initialization, validation, display, correctness check,
    and serialization/deserialization.
    """

    def test_question_initialization_valid(self):
        """Test Question initialization with valid data."""
        question = Question("What is 2+2?", ["3", "4", "5"], 1)
        self.assertEqual(question.question_text, "What is 2+2?")
        self.assertEqual(question.options, ["3", "4", "5"])
        self.assertEqual(question.correct_answer_index, 1)

    def test_question_initialization_empty_text_raises_error(self):
        """Test Question initialization with empty question text."""
        with self.assertRaisesRegex(ValueError, "Question text cannot be empty."):
            Question("", ["a", "b"], 0)
        with self.assertRaisesRegex(ValueError, "Question text cannot be empty."):
            Question("  ", ["a", "b"], 0)

    def test_question_initialization_empty_options_raises_error(self):
        """Test Question initialization with empty options list."""
        with self.assertRaisesRegex(ValueError, "Options must be a non-empty list."):
            Question("Test?", [], 0)

    def test_question_initialization_invalid_option_type_raises_error(self):
        """Test Question initialization with non-string options."""
        with self.assertRaisesRegex(ValueError, "All options must be non-empty strings."):
            Question("Test?", ["a", 123], 0)
        with self.assertRaisesRegex(ValueError, "All options must be non-empty strings."):
            Question("Test?", ["a", " "], 0) # Empty string option

    def test_question_initialization_invalid_index_raises_error(self):
        """Test Question initialization with an out-of-bounds or invalid index."""
        with self.assertRaisesRegex(ValueError, "Correct answer index is out of bounds or not an integer."):
            Question("Test?", ["a", "b"], 2) # Index out of bounds
        with self.assertRaisesRegex(ValueError, "Correct answer index is out of bounds or not an integer."):
            Question("Test?", ["a", "b"], -1) # Negative index
        with self.assertRaisesRegex(ValueError, "Correct answer index is out of bounds or not an integer."):
            Question("Test?", ["a", "b"], "0") # Non-integer index

    def test_question_display_format(self):
        """Test the format of the display method."""
        question = Question("What is the capital of France?", ["Berlin", "Paris", "Rome"], 1)
        expected_display = "Pytanie: What is the capital of France?\n  1. Berlin\n  2. Paris\n  3. Rome\n"
        self.assertEqual(question.display(), expected_display)

    def test_question_is_correct(self):
        """Test the is_correct method for correct and incorrect answers."""
        question = Question("What is 2+2?", ["3", "4", "5"], 1)
        self.assertTrue(question.is_correct(1))
        self.assertFalse(question.is_correct(0))
        self.assertFalse(question.is_correct(2))
        # Test with out of bounds user index (should return False)
        self.assertFalse(question.is_correct(99))
        self.assertFalse(question.is_correct(-1))

    def test_question_to_dict_from_dict(self):
        """Test conversion to dictionary and back to object."""
        original_question = Question("Fav color?", ["Red", "Blue"], 0)
        q_dict = original_question.to_dict()
        
        # Check dictionary structure and values
        self.assertIsInstance(q_dict, dict)
        self.assertEqual(q_dict["question_text"], "Fav color?")
        self.assertEqual(q_dict["options"], ["Red", "Blue"])
        self.assertEqual(q_dict["correct_answer_index"], 0)

        # Reconstruct Question from dictionary
        reconstructed_question = Question.from_dict(q_dict)
        self.assertIsInstance(reconstructed_question, Question)
        self.assertEqual(reconstructed_question.question_text, original_question.question_text)
        self.assertEqual(reconstructed_question.options, original_question.options)
        self.assertEqual(reconstructed_question.correct_answer_index, original_question.correct_answer_index)

    def test_question_from_dict_missing_keys_raises_error(self):
        """Test from_dict with missing keys."""
        with self.assertRaises(KeyError):
            Question.from_dict({"options": ["a"], "correct_answer_index": 0})
        with self.assertRaises(KeyError):
            Question.from_dict({"question_text": "Q", "correct_answer_index": 0})
        with self.assertRaises(KeyError):
            Question.from_dict({"question_text": "Q", "options": ["a"]})

class TestQuiz(unittest.TestCase):
    """
    Unit tests for the Quiz class.
    Covers initialization, adding/removing questions, and serialization/deserialization.
    """

    def setUp(self):
        """Set up common test data before each test."""
        self.q1 = Question("Q1 text", ["Q1_opt1", "Q1_opt2"], 0)
        self.q2 = Question("Q2 text", ["Q2_opt1", "Q2_opt2"], 1)

    def test_quiz_initialization_valid(self):
        """Test Quiz initialization with valid data."""
        quiz = Quiz("My Awesome Quiz", "A test quiz")
        self.assertEqual(quiz.title, "My Awesome Quiz")
        self.assertEqual(quiz.description, "A test quiz")
        self.assertEqual(len(quiz.questions), 0)

        quiz_with_questions = Quiz("Quiz with Qs", questions=[self.q1, self.q2])
        self.assertEqual(len(quiz_with_questions.questions), 2)
        self.assertEqual(quiz_with_questions.questions[0].question_text, "Q1 text")

    def test_quiz_initialization_empty_title_raises_error(self):
        """Test Quiz initialization with empty title."""
        with self.assertRaisesRegex(ValueError, "Quiz title cannot be empty."):
            Quiz("")
        with self.assertRaisesRegex(ValueError, "Quiz title cannot be empty."):
            Quiz("  ")

    def test_quiz_initialization_invalid_question_type_raises_error(self):
        """Test Quiz initialization with non-Question objects in questions list."""
        with self.assertRaisesRegex(TypeError, "All items in 'questions' must be Question objects."):
            Quiz("Bad Quiz", questions=[self.q1, "not a question"])

    def test_add_question(self):
        """Test adding questions to the quiz."""
        quiz = Quiz("Test Add")
        quiz.add_question(self.q1)
        self.assertEqual(len(quiz.questions), 1)
        self.assertEqual(quiz.questions[0].question_text, "Q1 text")
        quiz.add_question(self.q2)
        self.assertEqual(len(quiz.questions), 2)

    def test_add_question_invalid_type_raises_error(self):
        """Test adding non-Question object raises TypeError."""
        quiz = Quiz("Test Add Invalid")
        with self.assertRaisesRegex(TypeError, "Only Question objects can be added to the quiz."):
            quiz.add_question("not a question object")

    def test_remove_question(self):
        """Test removing questions from the quiz."""
        quiz = Quiz("Test Remove", questions=[self.q1, self.q2])
        self.assertEqual(len(quiz.questions), 2)
        quiz.remove_question(0)
        self.assertEqual(len(quiz.questions), 1)
        self.assertEqual(quiz.questions[0].question_text, "Q2 text")

    def test_remove_question_invalid_index_raises_error(self):
        """Test removing question with out-of-bounds index."""
        quiz = Quiz("Test Remove Invalid", questions=[self.q1])
        with self.assertRaisesRegex(IndexError, "Question index is out of bounds."):
            quiz.remove_question(1) # Index too high
        with self.assertRaisesRegex(IndexError, "Question index is out of bounds."):
            quiz.remove_question(-1) # Negative index

    def test_remove_question_invalid_type_raises_error(self):
        """Test removing question with non-integer index."""
        quiz = Quiz("Test Remove Type Error", questions=[self.q1])
        with self.assertRaisesRegex(TypeError, "Index must be an integer."):
            quiz.remove_question("0")

    def test_quiz_to_dict_from_dict(self):
        """Test conversion to dictionary and back to object."""
        original_quiz = Quiz("My Test Quiz", "A quiz for testing", questions=[self.q1, self.q2])
        quiz_dict = original_quiz.to_dict()

        # Check dictionary structure
        self.assertIsInstance(quiz_dict, dict)
        self.assertEqual(quiz_dict["title"], "My Test Quiz")
        self.assertEqual(quiz_dict["description"], "A quiz for testing")
        self.assertIsInstance(quiz_dict["questions"], list)
        self.assertEqual(len(quiz_dict["questions"]), 2)
        self.assertIsInstance(quiz_dict["questions"][0], dict) # Questions should be dicts

        # Reconstruct Quiz from dictionary
        reconstructed_quiz = Quiz.from_dict(quiz_dict)
        self.assertIsInstance(reconstructed_quiz, Quiz)
        self.assertEqual(reconstructed_quiz.title, original_quiz.title)
        self.assertEqual(reconstructed_quiz.description, original_quiz.description)
        self.assertEqual(len(reconstructed_quiz.questions), len(original_quiz.questions))
        self.assertIsInstance(reconstructed_quiz.questions[0], Question) # Reconstructed to Question objects
        self.assertEqual(reconstructed_quiz.questions[0].question_text, original_quiz.questions[0].question_text)
        self.assertEqual(reconstructed_quiz.questions[1].correct_answer_index, original_quiz.questions[1].correct_answer_index)


# --- Przykład Dziedziczenia w testach ---

class BaseTestUtility(unittest.TestCase):
    """
    Klasa bazowa dla testów pomocniczych, demonstrująca dziedziczenie.
    """
    def setUp(self):
        """Metoda setUp w klasie bazowej."""
        super().setUp() # Wywołuje setUp z unittest.TestCase
        self.base_value = 10
        print(f"\n[BaseTestUtility] setUp for {self._testMethodName}: base_value = {self.base_value}")

    def tearDown(self):
        """Metoda tearDown w klasie bazowej."""
        print(f"[BaseTestUtility] tearDown for {self._testMethodName}: Cleaning up base_value")
        self.base_value = None # Resetowanie wartości
        super().tearDown() # Wywołuje tearDown z unittest.TestCase

    def test_base_feature(self):
        """Test bazowej funkcjonalności."""
        print(f"[BaseTestUtility] Running test_base_feature with base_value = {self.base_value}")
        self.assertEqual(self.base_value, 10)


class DerivedTestUtility(BaseTestUtility):
    """
    Klasa pochodna dziedzicząca z BaseTestUtility, rozszerzająca funkcjonalność.
    """
    def setUp(self):
        """Metoda setUp w klasie pochodnej, rozszerzająca bazową."""
        super().setUp() # Wywołuje setUp z BaseTestUtility
        self.derived_value = 20
        self.total_value = self.base_value + self.derived_value
        print(f"[DerivedTestUtility] setUp for {self._testMethodName}: derived_value = {self.derived_value}, total_value = {self.total_value}")

    def tearDown(self):
        """Metoda tearDown w klasie pochodnej."""
        print(f"[DerivedTestUtility] tearDown for {self._testMethodName}: Cleaning up derived_value")
        self.derived_value = None
        self.total_value = None
        super().tearDown() # Wywołuje tearDown z BaseTestUtility

    def test_derived_feature(self):
        """Test funkcjonalności w klasie pochodnej."""
        print(f"[DerivedTestUtility] Running test_derived_feature with total_value = {self.total_value}")
        self.assertEqual(self.total_value, 30) # 10 (z bazowej) + 20 (z pochodnej)
    
    def test_access_base_feature_from_derived(self):
        """Test dostępu do funkcjonalności bazowej z klasy pochodnej."""
        print(f"[DerivedTestUtility] Running test_access_base_feature_from_derived. base_value = {self.base_value}")
        self.assertEqual(self.base_value, 10) # Dostęp do odziedziczonego atrybutu

def run_pylint_check(file_path: str) -> int:
    """
    Demonstrates how to programmatically run a Pylint check on a given file.
    This fulfills the requirement for code quality testing.

    Args:
        file_path (str): The path to the Python file to check.

    Returns:
        int: The exit code of Pylint (0 if no errors/warnings, >0 otherwise).
    """
    print(f"\n[Code Quality Check] Uruchamiam Pylint dla pliku: {file_path}")
    
    # Ścieżka do skryptu pylint - często jest w PATH, ale można podać pełną ścieżkę
    # pylint_executable = "pylint" 

    # Argumenty dla pylint:
    # --rcfile=none - ignoruje globalne pliki konfiguracyjne (dla czystego przykładu)
    # --disable=all - wyłącza wszystkie wiadomości, a następnie włącza konkretne (przykładowo)
    # --enable=E,W,C - włącza tylko błędy (Error), ostrzeżenia (Warning) i konwencje (Convention)
    # file_path - plik do sprawdzenia
    pylint_args = [file_path, "--reports=no", "--disable=C0114,C0115,C0116"] # Przykładowe wyłączenie brakujących docstringów

    class RealPyLint:
        def run_pylint(self, args):
            # Tutaj można by wykonać rzeczywiste sprawdzenie pylint
            # Na potrzeby przykładu, tylko symulujemy.
            # Rzeczywiste wywołanie wyglądałoby tak:
            # from pylint.lint import Run
            # Run(args)
            print(f"Uruchamiam pylint z argumentami: {args}")
            # Zwracamy kod wyjścia, 0 dla sukcesu, >0 dla błędów
            # Tutaj zwracamy 0 aby nie przerywac testow, ale w rzeczywistosci nalezy zwrocic prawdziwy wynik
            return os.system(f"pylint {' '.join(args)}") # Faktyczne uruchomienie pylint


    pylint_runner = RealPyLint()

    # Wywołanie pylint za pomocą os.system lub pylint.lint.run_pylint
    # Używamy zaimplementowanego obiektu pylint_runner do uruchomienia
    exit_code = pylint_runner.run_pylint(pylint_args)

    if exit_code == 0:
        print(f"[Code Quality Check] Pylint zakończył się sukcesem dla {file_path}. Kod spełnia standardy jakości.")
    else:
        print(f"[Code Quality Check] Pylint znalazł problemy w {file_path}. Kod wyjścia: {exit_code}")
    
    return exit_code



# --- Jak uruchomić te testy (sekcja dla Pythona) ---
if __name__ == '__main__':
    # Jawne tworzenie i uruchamianie testów
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()

    # Dodaj standardowe testy
    suite.addTest(loader.loadTestsFromTestCase(TestQuestion))
    suite.addTest(loader.loadTestsFromTestCase(TestQuiz))

    # Dodaj testy demonstrujące dziedziczenie
    suite.addTest(loader.loadTestsFromTestCase(BaseTestUtility))
    suite.addTest(loader.loadTestsFromTestCase(DerivedTestUtility))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

    run_pylint_check('quiz_player/player.py')
