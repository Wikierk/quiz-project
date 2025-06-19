from models.question import Question
from models.quiz import Quiz
from quiz_data.manager import QuizDataManager
import os

class QuizCreator:
    """
    Manages the interactive process of creating new quizzes.

    This class provides methods to guide the user through inputting quiz details,
    adding questions, and saving the completed quiz to a file. It handles basic
    input validation to ensure data integrity.
    """

    @staticmethod
    def create_new_quiz():
        """
        Guides the user through creating a new quiz, question by question.
        Collects quiz title, description, and then iteratively collects questions
        until the user decides to stop. Finally, it saves the quiz.
        """
        print("\n--- Rozpoczęcie tworzenia nowego quizu ---")

        # Get quiz title
        while True:
            title = input("Podaj tytuł quizu (np. 'Geografia Polski'): ").strip()
            if title:
                break
            else:
                print("Tytuł quizu nie może być pusty. Spróbuj ponownie.")

        # Get quiz description (optional)
        description = input("Podaj krótki opis quizu (opcjonalnie): ").strip()

        new_quiz = Quiz(title, description)
        print(f"Quiz '{title}' został utworzony. Teraz dodaj pytania.")

        # Add questions
        while True:
            print("\n--- Dodawanie nowego pytania ---")
            question_text = input("Wpisz treść pytania (naciśnij Enter, aby zakończyć dodawanie pytań): ").strip()

            if not question_text:
                print("Zakończono dodawanie pytań.")
                break

            options = []
            option_count = 1
            print("Wpisuj opcje odpowiedzi. Naciśnij Enter na pustej linii, aby zakończyć dodawanie opcji.")
            while True:
                option = input(f"Opcja {option_count}: ").strip()
                if not option:
                    if len(options) < 2: # A question needs at least 2 options
                        print("Pytanie musi mieć co najmniej dwie opcje odpowiedzi.")
                        continue
                    else:
                        break
                if option in options:
                    print("Ta opcja już istnieje. Wprowadź inną.")
                else:
                    options.append(option)
                    option_count += 1

            correct_answer_index = -1
            while True:
                try:
                    # Display options with numbers for user to choose
                    print("Dostępne opcje:")
                    for i, opt in enumerate(options):
                        print(f"  {i + 1}. {opt}")

                    user_input = input("Wpisz numer poprawnej odpowiedzi: ").strip()
                    correct_answer_index = int(user_input) - 1 # Convert to 0-based index

                    if 0 <= correct_answer_index < len(options):
                        break
                    else:
                        print("Nieprawidłowy numer opcji. Wpisz numer z listy.")
                except ValueError:
                    print("To nie jest liczba. Wpisz numer poprawnej odpowiedzi.")
                except Exception as e:
                    print(f"Wystąpił nieoczekiwany błąd podczas wyboru poprawnej odpowiedzi: {e}")

            try:
                question = Question(question_text, options, correct_answer_index)
                new_quiz.add_question(question)
                print("Pytanie dodane pomyślnie!")
            except ValueError as e:
                print(f"Błąd podczas tworzenia pytania: {e}. To pytanie nie zostało dodane.")
            except TypeError as e:
                print(f"Błąd typu podczas dodawania pytania: {e}. To pytanie nie zostało dodane.")
            except Exception as e:
                print(f"Wystąpił nieoczekiwany błąd podczas dodawania pytania do quizu: {e}")

        # Save the quiz if it has questions
        if not new_quiz.questions:
            print("Nie dodano żadnych pytań. Quiz nie zostanie zapisany.")
            return

        # Prompt for filename
        while True:
            filename = input("Podaj nazwę pliku, pod którą zapisać quiz (bez rozszerzenia .json): ").strip()
            if not filename:
                print("Nazwa pliku nie może być pusta.")
                continue
            if not all(c.isalnum() or c in ['-', '_'] for c in filename):
                print("Nazwa pliku może zawierać tylko litery, cyfry, myślniki i podkreślenia.")
                continue
            
            # Check for existing file and ask for overwrite confirmation
            full_path = os.path.join("data/quiz_examples", filename + ".json")
            if os.path.exists(full_path):
                overwrite = input(f"Plik '{filename}.json' już istnieje. Czy chcesz go nadpisać? (tak/nie): ").lower()
                if overwrite != 'tak':
                    print("Zapisywanie quizu anulowane.")
                    return # Exit without saving if user doesn't want to overwrite
            break

        try:
            QuizDataManager.save_quiz(new_quiz, filename)
            print("Quiz został pomyślnie zapisany!")
        except Exception as e:
            print(f"Wystąpił błąd podczas zapisywania quizu: {e}")
