# quiz_project/quiz_creator/creator.py
from models.question import Question
from models.quiz import Quiz
from quiz_data.manager import QuizDataManager
import os

class QuizCreator:
    """
    Manages the interactive process of creating and editing quizzes.
    Provides methods to guide the user through inputting quiz details,
    adding, removing, and modifying questions, and saving the completed quiz to a file.
    It handles basic input validation to ensure data integrity.
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
        QuizCreator._add_questions_to_quiz(new_quiz)

        # Save the quiz if it has questions
        if not new_quiz.questions:
            print("Nie dodano żadnych pytań. Quiz nie zostanie zapisany.")
            return

        # Prompt for filename
        QuizCreator._save_quiz_with_prompt(new_quiz)

    @staticmethod
    def _add_questions_to_quiz(quiz: Quiz):
        """
        Helper method to interactively add questions to a given quiz object.
        Used by both create_new_quiz and edit_existing_quiz.
        """
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
                quiz.add_question(question)
                print("Pytanie dodane pomyślnie!")
            except ValueError as e:
                print(f"Błąd podczas tworzenia pytania: {e}. To pytanie nie zostało dodane.")
            except TypeError as e:
                print(f"Błąd typu podczas dodawania pytania: {e}. To pytanie nie zostało dodane.")
            except Exception as e:
                print(f"Wystąpił nieoczekiwany błąd podczas dodawania pytania do quizu: {e}")

    @staticmethod
    def _save_quiz_with_prompt(quiz: Quiz):
        """
        Helper method to prompt user for filename and save the quiz.
        Handles existing file overwrite confirmation.
        """
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
            QuizDataManager.save_quiz(quiz, filename)
            print("Quiz został pomyślnie zapisany!")
        except Exception as e:
            print(f"Wystąpił błąd podczas zapisywania quizu: {e}")

    @staticmethod
    def edit_existing_quiz():
        """
        Allows the user to select an existing quiz and modify its properties or questions.
        """
        print("\n--- Rozpoczęcie edycji istniejącego quizu ---")
        available_quizzes = QuizDataManager.list_available_quizzes()

        if not available_quizzes:
            print("Brak dostępnych quizów do edycji. Najpierw utwórz quiz.")
            return

        print("Dostępne quizy do edycji:")
        for i, quiz_name in enumerate(available_quizzes):
            print(f"  {i + 1}. {quiz_name}")

        selected_quiz_name = None
        while True:
            try:
                choice = input("Wybierz numer quizu do edycji: ").strip()
                choice_index = int(choice) - 1
                if 0 <= choice_index < len(available_quizzes):
                    selected_quiz_name = available_quizzes[choice_index]
                    break
                else:
                    print("Nieprawidłowy numer. Wpisz numer z listy.")
            except ValueError:
                print("To nie jest liczba. Wpisz numer quizu.")
            except Exception as e:
                print(f"Wystąpił nieoczekiwany błąd podczas wyboru quizu: {e}")

        quiz_to_edit = None
        try:
            quiz_to_edit = QuizDataManager.load_quiz(selected_quiz_name)
            print(f"Quiz '{quiz_to_edit.title}' został wczytany do edycji.")
        except FileNotFoundError:
            print(f"Błąd: Plik quizu '{selected_quiz_name}.json' nie został znaleziony.")
            return
        except Exception as e:
            print(f"Wystąpił błąd podczas ładowania quizu '{selected_quiz_name}': {e}")
            return

        # Main editing loop
        while True:
            print(f"\n--- Edycja quizu: {quiz_to_edit.title} ---")
            print("1. Edytuj tytuł i opis quizu")
            print("2. Dodaj nowe pytanie")
            print("3. Edytuj istniejące pytanie")
            print("4. Usuń pytanie")
            print("5. Zakończ edycję i zapisz zmiany")
            print("6. Anuluj edycję (nie zapisuj zmian)")

            edit_choice = input("Wybierz opcję edycji (1-6): ").strip()

            if edit_choice == '1':
                print("\n--- Edycja tytułu i opisu ---")
                new_title = input(f"Nowy tytuł quizu (obecny: '{quiz_to_edit.title}'): ").strip()
                if new_title:
                    quiz_to_edit.title = new_title
                else:
                    print("Tytuł nie może być pusty, pozostawiono obecny.")

                new_description = input(f"Nowy opis quizu (obecny: '{quiz_to_edit.description}'): ").strip()
                quiz_to_edit.description = new_description
                print("Tytuł i opis zaktualizowane.")

            elif edit_choice == '2':
                print("\n--- Dodawanie nowego pytania do quizu ---")
                QuizCreator._add_questions_to_quiz(quiz_to_edit)
                print("Powrót do menu edycji.")

            elif edit_choice == '3':
                if not quiz_to_edit.questions:
                    print("Brak pytań do edycji w tym quizie.")
                    continue

                print("\n--- Edycja istniejącego pytania ---")
                print("Obecne pytania:")
                for i, q in enumerate(quiz_to_edit.questions):
                    print(f"  {i + 1}. {q.question_text}")

                try:
                    q_index_input = input("Wpisz numer pytania do edycji: ").strip()
                    q_index = int(q_index_input) - 1

                    if 0 <= q_index < len(quiz_to_edit.questions):
                        question_to_edit = quiz_to_edit.questions[q_index]
                        print(f"\nEdytujesz pytanie: {question_to_edit.question_text}")

                        # Edit question text
                        new_q_text = input(f"Nowa treść pytania (obecna: '{question_to_edit.question_text}'): ").strip()
                        if new_q_text:
                            question_to_edit.question_text = new_q_text
                        else:
                            print("Treść pytania nie może być pusta, pozostawiono obecną.")

                        # Edit options
                        print("\nEdytuj opcje odpowiedzi. Naciśnij Enter, aby pozostawić bez zmian.")
                        new_options = []
                        for i, opt in enumerate(question_to_edit.options):
                            edited_opt = input(f"Opcja {i+1} (obecna: '{opt}'): ").strip()
                            new_options.append(edited_opt if edited_opt else opt)
                        
                        # Allow adding new options
                        while True:
                            add_more = input("Dodać nową opcję? (tak/nie): ").lower().strip()
                            if add_more == 'tak':
                                new_opt = input("Wpisz nową opcję: ").strip()
                                if new_opt and new_opt not in new_options:
                                    new_options.append(new_opt)
                                elif new_opt:
                                    print("Opcja już istnieje lub jest pusta.")
                                else:
                                    print("Opcja nie może być pusta.")
                            else:
                                break
                        
                        if len(new_options) < 2 or not all(new_options):
                             print("Błąd: Pytanie musi mieć co najmniej dwie niepuste opcje. Opcje nie zostały zmienione.")
                             # Restore original options or handle error appropriately
                             continue


                        # Edit correct answer index
                        print("Dostępne opcje po edycji/dodaniu:")
                        for i, opt in enumerate(new_options):
                            print(f"  {i + 1}. {opt}")

                        while True:
                            try:
                                current_correct = question_to_edit.correct_answer_index
                                new_correct_input = input(f"Nowy numer poprawnej odpowiedzi (obecny: {current_correct + 1}): ").strip()
                                if not new_correct_input: # If user presses Enter, keep old one
                                    question_to_edit.options = new_options # Update options before setting index
                                    print("Poprawna odpowiedź pozostawiona bez zmian.")
                                    break

                                new_correct_index = int(new_correct_input) - 1
                                if 0 <= new_correct_index < len(new_options):
                                    question_to_edit.options = new_options # Update options first
                                    question_to_edit.correct_answer_index = new_correct_index
                                    print("Pytanie zaktualizowane pomyślnie!")
                                    break
                                else:
                                    print("Nieprawidłowy numer opcji. Wpisz numer z listy.")
                            except ValueError:
                                print("To nie jest liczba. Wpisz numer.")
                                
                    else:
                        print("Nieprawidłowy numer pytania.")
                except ValueError:
                    print("To nie jest liczba. Wpisz numer pytania.")
                except Exception as e:
                    print(f"Wystąpił nieoczekiwany błąd podczas edycji pytania: {e}")

            elif edit_choice == '4':
                if not quiz_to_edit.questions:
                    print("Brak pytań do usunięcia w tym quizie.")
                    continue

                print("\n--- Usuwanie pytania ---")
                print("Obecne pytania:")
                for i, q in enumerate(quiz_to_edit.questions):
                    print(f"  {i + 1}. {q.question_text}")
                
                try:
                    q_index_input = input("Wpisz numer pytania do usunięcia: ").strip()
                    q_index = int(q_index_input) - 1

                    if 0 <= q_index < len(quiz_to_edit.questions):
                        removed_question_text = quiz_to_edit.questions[q_index].question_text
                        quiz_to_edit.remove_question(q_index)
                        print(f"Pytanie '{removed_question_text}' zostało usunięte.")
                    else:
                        print("Nieprawidłowy numer pytania.")
                except ValueError:
                    print("To nie jest liczba. Wpisz numer pytania.")
                except IndexError:
                    print("Nieprawidłowy indeks pytania.") # Should be caught by the if condition
                except Exception as e:
                    print(f"Wystąpił nieoczekiwany błąd podczas usuwania pytania: {e}")

            elif edit_choice == '5':
                # Save changes
                QuizCreator._save_quiz_with_prompt(quiz_to_edit)
                print("Zakończono edycję quizu.")
                break
            elif edit_choice == '6':
                print("Anulowano edycję. Zmiany nie zostaną zapisane.")
                break
            else:
                print("Nieprawidłowy wybór. Proszę wybrać opcję 1-6.")

