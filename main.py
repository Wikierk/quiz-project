# quiz_project/main.py
import sys
import os

# Dodaj katalog główny projektu do ścieżki Pythona, aby umożliwić importy z pakietów
# To jest ważne, gdy uruchamiasz main.py bezpośrednio z katalogu quiz_project/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from quiz_creator.creator import QuizCreator
from quiz_player.player import QuizPlayer
from quiz_data.manager import QuizDataManager # Aby pokazać, że manager działa

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def display_menu():
    """Displays the main menu options to the user."""
    print("\n--- Menu Główne ---")
    print("1. Utwórz nowy quiz")
    print("2. Odtwórz quiz")
    print("3. Edytuj istniejący quiz") # Nowa opcja
    print("4. Wyjdź")
    print("-------------------")

def main():
    """
    Main function to run the Quiz Application.
    It provides a menu for the user to choose between creating a quiz,
    playing a quiz, editing a quiz, or exiting the application.
    """
    print("Witaj w Aplikacji Quizowej!")

    while True:
        display_menu()
        choice = input("Wybierz opcję (1-4): ").strip() # Zmieniono zakres wyboru

        clear_screen() # Clear screen for cleaner interaction

        if choice == '1':
            QuizCreator.create_new_quiz()
        elif choice == '2':
            QuizPlayer.play_quiz()
        elif choice == '3': # Nowa logika dla edycji
            QuizCreator.edit_existing_quiz()
        elif choice == '4': # Zmieniono numer opcji wyjścia
            print("Dziękujemy za skorzystanie z aplikacji. Do widzenia!")
            break
        else:
            print("Nieprawidłowy wybór. Proszę wybrać opcję 1, 2, 3 lub 4.") # Zmieniono komunikat
        
        # Optional: Pause before showing menu again for better readability
        if choice in ['1', '2', '3']: # Zmieniono warunek
            input("\nNaciśnij Enter, aby kontynuować...")
            clear_screen()


if __name__ == "__main__":
    main()

