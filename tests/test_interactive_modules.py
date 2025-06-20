import unittest
import os
import sys
import json
import shutil
from unittest.mock import patch, mock_open
from io import StringIO
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.question import Question
from models.quiz import Quiz
from quiz_data.manager import QuizDataManager
from quiz_creator.creator import QuizCreator
from quiz_player.player import QuizPlayer

class TestQuizCreator(unittest.TestCase):
    """
    Unit tests for the QuizCreator class, focusing on its interactive functionality.
    This involves mocking user input and verifying output.
    """

    def setUp(self):
        """
        Set up a temporary directory for test quiz files before each test.
        Also, patch QuizDataManager.save_quiz and redirect stdout.
        """
        print(f"\n--- setUp TestQuizCreator for {self._testMethodName} ---") # Debugging print
        self.test_dir = "test_quizzes_creator"
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir)

        # Patch QuizDataManager.save_quiz to be a simple mock object.
        # We only verify that it's called with the correct arguments, not that it actually saves a file.
        self.patcher_save = patch('quiz_data.manager.QuizDataManager.save_quiz')
        self.mock_save_quiz = self.patcher_save.start()

        # Redirect stdout to capture print statements
        self.held_output = StringIO()
        self.original_stdout = sys.stdout
        sys.stdout = self.held_output


    def tearDown(self):
        """
        Clean up the temporary test directory and restore stdout after each test.
        """
        print(f"--- tearDown TestQuizCreator for {self._testMethodName} ---") # Debugging print
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        self.patcher_save.stop() # Stop the patcher

        # Restore stdout
        sys.stdout = self.original_stdout
        self.held_output.close()

    @patch('builtins.input', side_effect=['Test Quiz Title', 'Test Description',
                                          'Q1 text?', 'Option A', 'Option B', '', '1', # Question 1
                                          '', # End adding questions
                                          'test_quiz_output']) # Filename to save
    def test_create_new_quiz_success(self, mock_input):
        """
        Test successful creation of a new quiz with valid input.
        Verifies that QuizDataManager.save_quiz is called with a Quiz object.
        """
        QuizCreator.create_new_quiz()

        # Verify that QuizDataManager.save_quiz was called
        self.mock_save_quiz.assert_called_once()
        
        # Get the arguments passed to save_quiz
        args, kwargs = self.mock_save_quiz.call_args
        saved_quiz = args[0] # The first argument should be the Quiz object

        self.assertIsInstance(saved_quiz, Quiz)
        self.assertEqual(saved_quiz.title, "Test Quiz Title")
        self.assertEqual(saved_quiz.description, "Test Description")
        self.assertEqual(len(saved_quiz.questions), 1)
        self.assertEqual(saved_quiz.questions[0].question_text, "Q1 text?")
        self.assertEqual(saved_quiz.questions[0].options, ["Option A", "Option B"])
        self.assertEqual(saved_quiz.questions[0].correct_answer_index, 0)

        # Check some print outputs for user feedback
        output = self.held_output.getvalue()
        self.assertIn("Quiz 'Test Quiz Title' został utworzony. Teraz dodaj pytania.", output)
        self.assertIn("Pytanie dodane pomyślnie!", output)
        self.assertIn("Quiz został pomyślnie zapisany!", output)


    @patch('builtins.input', side_effect=['', 'Valid Title', # Empty title then valid (2 inputs for title)
                                          'Test Description', # Brakujące wejście dla opisu
                                          'Q1 text?', 'Opt1', 'Opt2', '', '1', # 1 question (5 inputs)
                                          '', # End adding questions (1 input)
                                          'test_quiz_output']) # Filename to save (1 input)
    def test_create_new_quiz_empty_title_retry(self, mock_input):
        """
        Test that empty quiz title input is handled and retried.
        """
        QuizCreator.create_new_quiz()
        output = self.held_output.getvalue()
        self.assertIn("Tytuł quizu nie może być pusty. Spróbuj ponownie.", output)
        self.mock_save_quiz.assert_called_once() # Should still save after retry

    @patch('builtins.input', side_effect=['Valid Title', 'Valid Description',
                                          'Q1 text?', 'Opt1', '', # Only one option (2 inputs for options)
                                          'Opt2', '', '1', # Then add a second option (3 inputs for options)
                                          '', # End adding questions (1 input)
                                          'test_quiz_output']) # Filename to save (1 input)
    def test_create_new_quiz_less_than_two_options_retry(self, mock_input):
        """
        Test that adding less than two options for a question is handled and retried.
        """
        QuizCreator.create_new_quiz()
        output = self.held_output.getvalue()
        self.assertIn("Pytanie musi mieć co najmniej dwie opcje odpowiedzi.", output)
        self.mock_save_quiz.assert_called_once()


    @patch('builtins.input', side_effect=['Valid Title', 'Valid Description',
                                          'Q1?', 'A', 'A', 'B', '', '1', # Duplicate option 'A' (3 inputs for options)
                                          '', # End adding questions (1 input)
                                          'test_quiz_output']) # Filename to save (1 input)
    def test_create_new_quiz_duplicate_option_retry(self, mock_input):
        """
        Test that duplicate options are handled and retried.
        """
        QuizCreator.create_new_quiz()
        output = self.held_output.getvalue()
        self.assertIn("Ta opcja już istnieje. Wprowadź inną.", output)
        self.mock_save_quiz.assert_called_once()


    @patch('builtins.input', side_effect=['Valid Title', 'Valid Description',
                                          'Q1?', 'A', 'B', '', 'x', '1', # Invalid index then valid (2 inputs for index)
                                          '', # End adding questions (1 input)
                                          'test_quiz_output']) # Filename to save (1 input)
    def test_create_new_quiz_invalid_index_retry(self, mock_input):
        """
        Test that invalid correct answer index input is handled and retried.
        """
        QuizCreator.create_new_quiz()
        output = self.held_output.getvalue()
        self.assertIn("To nie jest liczba. Wpisz numer poprawnej odpowiedzi.", output)
        self.mock_save_quiz.assert_called_once()

    @patch('builtins.input', side_effect=['Valid Title', 'Valid Description',
                                          '', # No questions added (1 input)
                                          'test_quiz_output']) # Filename to save (1 input)
    def test_create_new_quiz_no_questions_saved(self, mock_input):
        """
        Test that quiz is not saved if no questions are added.
        """
        QuizCreator.create_new_quiz()
        output = self.held_output.getvalue()
        self.assertIn("Nie dodano żadnych pytań. Quiz nie zostanie zapisany.", output)
        self.mock_save_quiz.assert_not_called() # save_quiz should not be called

    @patch('builtins.input', side_effect=['Valid Title', 'Valid Description',
                                          'Q1 text?', 'Option A', 'Option B', '', '1', # 1 question (5 inputs)
                                          '', # End adding questions (1 input)
                                          'existing_quiz', # <-- Dodano to wejście dla nazwy pliku
                                          'nie']) # Filename, then 'nie' to not overwrite. (2 inputs)
    @patch('os.path.exists', return_value=True) # Patch os.path.exists to simulate file existing
    def test_create_new_quiz_overwrite_no(self, mock_exists, mock_input):
        """
        Test behavior when user chooses not to overwrite an existing file.
        """
        QuizCreator.create_new_quiz()
        output = self.held_output.getvalue()
        # The expected string for confirmation prompt from input() might not be fully captured.
        # Instead, verify the crucial outcome message.
        self.assertIn("Zapisywanie quizu anulowane.", output)
        self.mock_save_quiz.assert_not_called() # Should not save


class TestQuizPlayer(unittest.TestCase):
    """
    Unit tests for the QuizPlayer class, focusing on its interactive functionality.
    This involves mocking user input and verifying output, and also mocking file loading.
    """

    def setUp(self):
        """
        Set up a temporary directory for test quiz files and a sample quiz.
        Also, patch QuizDataManager and QuizPlayer's chart generation function.
        """
        print(f"\n--- setUp TestQuizPlayer for {self._testMethodName} ---") # Debugging print
        self.test_dir = "test_quizzes_player"
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir)

        self.q1 = Question("Q1?", ["A", "B"], 0)
        self.q2 = Question("Q2?", ["C", "D"], 1)
        self.sample_quiz = Quiz("Player Test Quiz", questions=[self.q1, self.q2])
        self.sample_quiz_filename = "player_test_quiz.json"
        self.sample_quiz_filepath = os.path.join(self.test_dir, self.sample_quiz_filename)
        
        # Save the sample quiz so QuizDataManager can load it (real call for setup)
        # We save it to the *test_dir* but it's loaded via mocked QuizDataManager.load_quiz
        QuizDataManager.save_quiz(self.sample_quiz, self.sample_quiz_filename, self.test_dir)
        
        # Patch QuizDataManager.list_available_quizzes and load_quiz for the tests
        self.patcher_list = patch('quiz_data.manager.QuizDataManager.list_available_quizzes', 
                                  return_value=[os.path.splitext(self.sample_quiz_filename)[0]])
        self.mock_list_quizzes = self.patcher_list.start()
        
        self.patcher_load = patch('quiz_data.manager.QuizDataManager.load_quiz', 
                                  return_value=self.sample_quiz)
        self.mock_load_quiz = self.patcher_load.start()

        # Patch QuizPlayer.generate_and_save_results_chart directly
        self.patcher_chart_gen = patch('quiz_player.player.QuizPlayer.generate_and_save_results_chart')
        self.mock_chart_gen = self.patcher_chart_gen.start()

        # Redirect stdout to capture print statements
        self.held_output = StringIO()
        self.original_stdout = sys.stdout
        sys.stdout = self.held_output


    def tearDown(self):
        """
        Clean up the temporary test directory and stop all patches after each test.
        """
        print(f"--- tearDown TestQuizPlayer for {self._testMethodName} ---") # Debugging print
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        
        # Stop all patchers started in setUp
        self.patcher_list.stop()
        self.patcher_load.stop()
        self.patcher_chart_gen.stop()

        # Restore stdout
        sys.stdout = self.original_stdout
        self.held_output.close()

    @patch('builtins.input', side_effect=['1', # Select the only available quiz (1 input)
                                          '1', # Answer to Q1 (correct) (1 input)
                                          '2']) # Answer to Q2 (correct) (1 input)
    def test_play_quiz_success_all_correct(self, mock_input):
        """
        Test successful playing of a quiz with all correct answers.
        Verifies correct score and chart saving.
        """
        QuizPlayer.play_quiz()

        # Verify load and list methods were called
        self.mock_list_quizzes.assert_called_once()
        self.mock_load_quiz.assert_called_once_with(os.path.splitext(self.sample_quiz_filename)[0])

        # Verify correct print statements
        output = self.held_output.getvalue()
        self.assertIn("Poprawna odpowiedź!", output)
        self.assertIn("--- Koniec quizu! ---", output)
        self.assertIn("Twój wynik: 2/2 poprawnych odpowiedzi.", output)

        # Verify chart generation mock was called with correct arguments
        self.mock_chart_gen.assert_called_once_with(2, 0, "Player Test Quiz")


    @patch('builtins.input', side_effect=['1', # Select the only available quiz (1 input)
                                          '2', # Answer to Q1 (incorrect) (1 input)
                                          '1']) # Answer to Q2 (incorrect) (1 input)
    def test_play_quiz_all_incorrect(self, mock_input):
        """
        Test playing a quiz with all incorrect answers.
        """
        QuizPlayer.play_quiz()
        output = self.held_output.getvalue()
        self.assertIn(f"Niepoprawna odpowiedź. Poprawna to: {self.q1.options[self.q1.correct_answer_index]}", output)
        self.assertIn("Twój wynik: 0/2 poprawnych odpowiedzi.", output)
        self.assertIn("Pytań, na które odpowiedziałeś/aś błędnie:", output)
        self.assertIn("- Q1?", output)
        self.assertIn("- Q2?", output)
        self.mock_chart_gen.assert_called_once_with(0, 2, "Player Test Quiz")

    @patch('builtins.input', side_effect=['99', '1', # Invalid choice, then valid (2 inputs)
                                          '1', # Answer Q1 (1 input)
                                          '2']) # Answer Q2 (1 input)
    def test_play_quiz_invalid_quiz_selection_retry(self, mock_input):
        """
        Test that invalid quiz selection is handled and retried.
        """
        QuizPlayer.play_quiz()
        output = self.held_output.getvalue()
        self.assertIn("Nieprawidłowy numer. Wpisz numer z listy.", output)
        self.mock_load_quiz.assert_called_once() # Should still load after retry

    @patch('builtins.input', side_effect=['1', # Select quiz (1 input)
                                          '99', '1', # Invalid answer index, then valid (2 inputs)
                                          '2']) # Answer Q2 (1 input)
    def test_play_quiz_invalid_answer_input_retry(self, mock_input):
        """
        Test that invalid answer input is handled and retried.
        """
        QuizPlayer.play_quiz()
        output = self.held_output.getvalue()
        self.assertIn("Nieprawidłowy numer opcji. Wpisz numer z listy.", output)
        # Ensure the quiz continued and was ultimately saved/processed
        self.mock_chart_gen.assert_called_once()

    @patch('quiz_data.manager.QuizDataManager.list_available_quizzes', return_value=[])
    def test_play_quiz_no_quizzes_available(self, mock_list_quizzes):
        """
        Test behavior when no quizzes are available to play.
        """
        QuizPlayer.play_quiz()
        output = self.held_output.getvalue()
        self.assertIn("Brak dostępnych quizów. Najpierw utwórz quiz w trybie kreatora.", output)
        self.mock_load_quiz.assert_not_called()


    @patch('quiz_data.manager.QuizDataManager.load_quiz', side_effect=FileNotFoundError("Mocked File Not Found"))
    @patch('builtins.input', side_effect=['1']) # Select existing quiz that mock will fail (1 input)
    def test_play_quiz_load_error(self, mock_input, mock_load_quiz):
        """
        Test handling of FileNotFoundError during quiz loading.
        """
        # We need a list of quizzes for the player to select one,
        # even if the load fails.
        self.patcher_list_available = patch('quiz_data.manager.QuizDataManager.list_available_quizzes', 
                                            return_value=["mocked_quiz"])
        self.mock_list_available = self.patcher_list_available.start()
        
        QuizPlayer.play_quiz()
        output = self.held_output.getvalue()
        self.assertIn("Błąd: Plik quizu 'mocked_quiz.json' nie został znaleziony.", output)
        self.mock_list_available.assert_called_once()
        mock_load_quiz.assert_called_once()
        self.patcher_list_available.stop() # Stop this patcher too


if __name__ == '__main__':
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    suite.addTest(loader.loadTestsFromTestCase(TestQuizCreator))
    suite.addTest(loader.loadTestsFromTestCase(TestQuizPlayer))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
