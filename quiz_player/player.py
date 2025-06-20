import matplotlib
matplotlib.use('Agg') # Ustawia nieinteraktywny backend, aby zapobiec problemom z GUI w testach/środowiskach bez GUI
import matplotlib.pyplot as plt
import os
from models.quiz import Quiz
from quiz_data.manager import QuizDataManager

# Globalna zmienna na poziomie modułu
# (jest dostępna dla wszystkich funkcji i metod w tym module)
REPORTS_DIRECTORY = "reports"


class QuizPlayer:
    """
    Manages the process of playing a quiz, including displaying questions,
    collecting answers, calculating scores, and presenting results.
    It utilizes functional programming concepts (map, filter, lambda) for analysis
    and matplotlib for result visualization.
    """

    @staticmethod
    def play_quiz():
        """
        Allows the user to select and play an existing quiz.
        It loads the quiz, presents questions, records answers, and shows results.
        """
        print("\n--- Rozpoczęcie odtwarzania quizu ---")

        # List available quizzes
        available_quizzes = QuizDataManager.list_available_quizzes()

        if not available_quizzes:
            print("Brak dostępnych quizów. Najpierw utwórz quiz w trybie kreatora.")
            return

        print("Dostępne quizy:")
        for i, quiz_name in enumerate(available_quizzes):
            print(f"  {i + 1}. {quiz_name}")

        selected_quiz_name = None
        while True:
            try:
                choice = input("Wybierz numer quizu do odtworzenia: ").strip()
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

        quiz = None
        try:
            quiz = QuizDataManager.load_quiz(selected_quiz_name)
        except FileNotFoundError:
            print(f"Błąd: Plik quizu '{selected_quiz_name}.json' nie został znaleziony.")
            return
        except Exception as e:
            print(f"Wystąpił błąd podczas ładowania quizu '{selected_quiz_name}': {e}")
            return

        if not quiz.questions:
            print(f"Quiz '{quiz.title}' nie zawiera żadnych pytań. Nie można go odtworzyć.")
            return

        print(f"\n--- Rozpoczęcie quizu: {quiz.title} ---")
        if quiz.description:
            print(f"Opis: {quiz.description}")

        user_answers = []
        correct_answers_count = 0
        total_questions = len(quiz.questions)

        for i, question in enumerate(quiz.questions):
            print(f"\n--- Pytanie {i + 1}/{total_questions} ---")
            print(question.display())

            while True:
                try:
                    user_input = input("Wpisz numer odpowiedzi: ").strip()
                    answer_index = int(user_input) - 1 # Convert to 0-based index
                    if 0 <= answer_index < len(question.options):
                        user_answers.append({
                            "question_text": question.question_text,
                            "user_choice_index": answer_index,
                            "is_correct": question.is_correct(answer_index),
                            "correct_answer_index": question.correct_answer_index,
                            "options": question.options
                        })
                        if question.is_correct(answer_index):
                            print("Poprawna odpowiedź!")
                            correct_answers_count += 1
                        else:
                            print(f"Niepoprawna odpowiedź. Poprawna to: {question.options[question.correct_answer_index]}")
                        break
                    else:
                        print("Nieprawidłowy numer opcji. Wpisz numer z listy.")
                except ValueError:
                    print("To nie jest liczba. Wpisz numer odpowiedzi.")
                except Exception as e:
                    print(f"Wystąpił nieoczekiwany błąd podczas udzielania odpowiedzi: {e}")

        print("\n--- Koniec quizu! ---")
        print(f"Twój wynik: {correct_answers_count}/{total_questions} poprawnych odpowiedzi.")

        # --- Analiza wyników z użyciem programowania funkcyjnego ---
        # 1. Użycie filter do pobrania tylko poprawnych odpowiedzi
        # filtered_correct_answers = list(filter(lambda ans: ans["is_correct"], user_answers))
        # correct_count_functional = len(filtered_correct_answers)

        # 2. Użycie map do mapowania wyników na prosty format True/False
        # is_correct_list = list(map(lambda ans: ans["is_correct"], user_answers))

        # Re-calculating with functional programming for demonstration
        # Filter for correct answers
        correct_results = list(filter(lambda ans: ans["is_correct"], user_answers))
        num_correct = len(correct_results)

        # Filter for incorrect answers
        incorrect_results = list(filter(lambda ans: not ans["is_correct"], user_answers))
        num_incorrect = len(incorrect_results)

        # Using map to get the texts of incorrect questions (example of map usage)
        incorrect_question_texts = list(map(lambda ans: ans["question_text"], incorrect_results))
        if incorrect_question_texts:
            print("\nPytań, na które odpowiedziałeś/aś błędnie:")
            for text in incorrect_question_texts:
                print(f"- {text}")

        # --- Wizualizacja danych (matplotlib) ---
        QuizPlayer.generate_and_save_results_chart(num_correct, num_incorrect, quiz.title)

        print("\nSzczegółowe wyniki zostały zapisane w raporcie graficznym.")


    @staticmethod
    def generate_and_save_results_chart(correct_count: int, incorrect_count: int, quiz_title: str):
        """
        Generates a pie chart showing the distribution of correct vs. incorrect answers
        and saves it to the 'reports' directory.

        Args:
            correct_count (int): Number of correct answers.
            incorrect_count (int): Number of incorrect answers.
            quiz_title (str): The title of the quiz for chart labeling.
        """
        # Użycie krotki do przechowywania stałych etykiet
        labels: tuple[str, str] = ('Poprawne', 'Niepoprawne')
        sizes = [correct_count, incorrect_count]
        
        # Użycie krotki do przechowywania stałych kodów kolorów
        colors: tuple[str, str] = ('#4CAF50', '#F44336') # Green for correct, Red for incorrect
        
        explode = (0.1, 0) # explode the 1st slice (Correct)

        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, explode=explode, labels=labels, colors=colors,
                autopct='%1.1f%%', shadow=True, startangle=90, textprops={'fontsize': 12, 'color': 'white'})
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        plt.title(f'Wyniki quizu: {quiz_title}', fontsize=16, color='black')
        
        # Save the chart using the global variable for the directory
        # REPORTS_DIRECTORY jest zmienną globalną na poziomie modułu
        if not os.path.exists(REPORTS_DIRECTORY):
            os.makedirs(REPORTS_DIRECTORY)
            print(f"Created directory: {REPORTS_DIRECTORY}")

        chart_filename = f"wyniki_{quiz_title.replace(' ', '_').lower()}.png"
        chart_filepath = os.path.join(REPORTS_DIRECTORY, chart_filename)

        try:
            plt.savefig(chart_filepath, bbox_inches='tight', dpi=100)
            print(f"Wykres wyników został zapisany w: {chart_filepath}")
        except Exception as e:
            print(f"Błąd podczas zapisywania wykresu: {e}")
        finally:
            plt.close(fig1) # Close the plot to free up memory