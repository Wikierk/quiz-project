import unittest
import os
import sys
import json
import shutil

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.question import Question
from models.quiz import Quiz
from quiz_data.manager import QuizDataManager

class TestQuizDataManager(unittest.TestCase):
    """
    Unit tests for the QuizDataManager class.
    Covers saving, loading, and listing quiz files, including error handling.
    """

    def setUp(self):
        """
        Set up a temporary directory for test quiz files before each test.
        This ensures tests are isolated and don't interfere with actual quiz data.
        """
        self.test_dir = "test_quizzes"
        # Ensure the test directory is clean before each test
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir)

        # Create a sample quiz for testing
        self.q1 = Question("What is the capital of Poland?", ["Warsaw", "Krakow", "Berlin"], 0)
        self.q2 = Question("Which planet is known as the Red Planet?", ["Earth", "Mars", "Jupiter"], 1)
        self.sample_quiz = Quiz("Science Basics", "Basic science questions", questions=[self.q1, self.q2])
        self.sample_quiz_filename = "sample_science_quiz.json"
        self.sample_quiz_filepath = os.path.join(self.test_dir, self.sample_quiz_filename)

    def tearDown(self):
        """
        Clean up the temporary test directory after each test.
        """
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_save_quiz_success(self):
        """Test successful saving of a Quiz object to a JSON file."""
        QuizDataManager.save_quiz(self.sample_quiz, self.sample_quiz_filename, self.test_dir)
        self.assertTrue(os.path.exists(self.sample_quiz_filepath))

        # Verify content
        with open(self.sample_quiz_filepath, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        self.assertEqual(loaded_data["title"], self.sample_quiz.title)
        self.assertEqual(len(loaded_data["questions"]), len(self.sample_quiz.questions))
        self.assertEqual(loaded_data["questions"][0]["question_text"], self.q1.question_text)

    def test_save_quiz_creates_directory(self):
        """Test that save_quiz creates the directory if it doesn't exist."""
        # Remove the directory created in setUp to ensure it's recreated
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

        QuizDataManager.save_quiz(self.sample_quiz, self.sample_quiz_filename, self.test_dir)
        self.assertTrue(os.path.exists(self.test_dir))
        self.assertTrue(os.path.exists(self.sample_quiz_filepath))

    def test_save_quiz_invalid_quiz_type_raises_error(self):
        """Test saving with an object that is not a Quiz instance."""
        with self.assertRaisesRegex(TypeError, "Only Quiz objects can be saved."):
            QuizDataManager.save_quiz("not a quiz", self.sample_quiz_filename, self.test_dir)

    def test_save_quiz_filename_no_json_extension(self):
        """Test saving a quiz when filename does not include .json extension."""
        filename_no_ext = "my_quiz_no_ext"
        filepath_with_ext = os.path.join(self.test_dir, filename_no_ext + ".json")
        QuizDataManager.save_quiz(self.sample_quiz, filename_no_ext, self.test_dir)
        self.assertTrue(os.path.exists(filepath_with_ext))
        # Clean up this specific file for this test's isolation
        if os.path.exists(filepath_with_ext):
            os.remove(filepath_with_ext)


    def test_load_quiz_success(self):
        """Test successful loading of a Quiz object from a JSON file."""
        QuizDataManager.save_quiz(self.sample_quiz, self.sample_quiz_filename, self.test_dir)
        loaded_quiz = QuizDataManager.load_quiz(self.sample_quiz_filename, self.test_dir)

        self.assertIsInstance(loaded_quiz, Quiz)
        self.assertEqual(loaded_quiz.title, self.sample_quiz.title)
        self.assertEqual(len(loaded_quiz.questions), len(self.sample_quiz.questions))
        self.assertEqual(loaded_quiz.questions[0].question_text, self.sample_quiz.questions[0].question_text)
        self.assertEqual(loaded_quiz.questions[1].correct_answer_index, self.sample_quiz.questions[1].correct_answer_index)

    def test_load_quiz_file_not_found(self):
        """Test loading a non-existent quiz file."""
        with self.assertRaisesRegex(FileNotFoundError, "Quiz file not found:"):
            QuizDataManager.load_quiz("non_existent_quiz.json", self.test_dir)

    def test_load_quiz_invalid_json(self):
        """Test loading a file with invalid JSON content."""
        bad_json_filename = "bad_format.json"
        bad_json_filepath = os.path.join(self.test_dir, bad_json_filename)
        with open(bad_json_filepath, 'w', encoding='utf-8') as f:
            f.write("{invalid json}") # Write malformed JSON

        with self.assertRaises(json.JSONDecodeError):
            QuizDataManager.load_quiz(bad_json_filename, self.test_dir)

    def test_load_quiz_missing_keys_in_json(self):
        """Test loading a JSON file with missing required keys for Quiz."""
        missing_keys_filename = "missing_keys.json"
        missing_keys_filepath = os.path.join(self.test_dir, missing_keys_filename)
        with open(missing_keys_filepath, 'w', encoding='utf-8') as f:
            json.dump({"description": "incomplete"}, f) # Missing 'title'

        with self.assertRaises(KeyError):
            QuizDataManager.load_quiz(missing_keys_filename, self.test_dir)
        
        # Test with missing keys for a question
        missing_question_keys_filename = "missing_q_keys.json"
        missing_q_keys_filepath = os.path.join(self.test_dir, missing_question_keys_filename)
        with open(missing_q_keys_filepath, 'w', encoding='utf-8') as f:
            json.dump({
                "title": "Valid Quiz",
                "questions": [
                    {"question_text": "Q1", "options": ["A", "B"]}, # Missing correct_answer_index
                ]
            }, f)
        with self.assertRaises(KeyError):
            QuizDataManager.load_quiz(missing_question_keys_filename, self.test_dir)


    def test_list_available_quizzes_empty_directory(self):
        """Test listing quizzes in an empty directory."""
        # self.test_dir is already empty after setUp, except if save_quiz was called
        # Ensure it's empty for this specific test
        shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir)

        quizzes = QuizDataManager.list_available_quizzes(self.test_dir)
        self.assertEqual(quizzes, [])

    def test_list_available_quizzes_non_existent_directory(self):
        """Test listing quizzes in a non-existent directory."""
        non_existent_dir = "non_existent_test_dir"
        if os.path.exists(non_existent_dir):
            shutil.rmtree(non_existent_dir)

        quizzes = QuizDataManager.list_available_quizzes(non_existent_dir)
        self.assertEqual(quizzes, [])

    def test_list_available_quizzes_with_files(self):
        """Test listing quizzes with multiple quiz files present."""
        # Save a few quizzes
        QuizDataManager.save_quiz(self.sample_quiz, "quiz_a.json", self.test_dir)
        QuizDataManager.save_quiz(self.sample_quiz, "quiz_c.json", self.test_dir)
        QuizDataManager.save_quiz(self.sample_quiz, "quiz_b.json", self.test_dir)
        
        # Add a non-json file to ensure it's ignored
        with open(os.path.join(self.test_dir, "temp.txt"), 'w') as f:
            f.write("Some text")

        quizzes = QuizDataManager.list_available_quizzes(self.test_dir)
        self.assertIn("quiz_a", quizzes)
        self.assertIn("quiz_b", quizzes)
        self.assertIn("quiz_c", quizzes)
        self.assertEqual(len(quizzes), 3)
        # Verify alphabetical order
        self.assertEqual(quizzes, ["quiz_a", "quiz_b", "quiz_c"])


if __name__ == '__main__':
    unittest.main()