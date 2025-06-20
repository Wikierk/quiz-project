# quiz_project/utils/__init__.py
# Plik inicjalizujący pakiet 'utils'. Może być pusty.


# quiz_project/utils/helpers.py
import random
import time
from functools import wraps # Do poprawnego kopiowania metadanych funkcji
from functools import reduce # Importujemy funkcję reduce
import timeit # Nowy import dla testów wydajności
import os # Importujemy os do wykonywania poleceń systemowych

# Należy zainstalować 'memory_profiler': pip install memory_profiler
try:
    from memory_profiler import profile
except ImportError:
    # Zastępczy dekorator, jeśli memory_profiler nie jest zainstalowany,
    # aby uniknąć błędów w działaniu aplikacji.
    def profile(func):
        return func

# Należy zainstalować 'pylint': pip install pylint
try:
    import pylint.lint
except ImportError:
    # Zastępcza klasa, jeśli pylint nie jest zainstalowany,
    # aby uniknąć błędów w działaniu aplikacji.
    class MockPyLint:
        def run_pylint(self, args):
            print("Pylint nie jest zainstalowany. Zainstaluj 'pylint' za pomocą 'pip install pylint' aby korzystać z tej funkcji.")
            return 1 # Symulujemy błąd

    pylint_runner = MockPyLint()
else:
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


def factorial_recursive(n: int) -> int:
    """
    Calculates the factorial of a non-negative integer using recursion.
    This function is an example of a recursive function implementation.

    Args:
        n (int): The non-negative integer for which to calculate the factorial.

    Returns:
        int: The factorial of n.

    Raises:
        ValueError: If the input number is negative.
        TypeError: If the input is not an integer.
    """
    if not isinstance(n, int):
        raise TypeError("Input must be an integer.")
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers.")
    if n == 0:
        # Base case: factorial of 0 is 1
        return 1
    else:
        # Recursive step: n * factorial(n-1)
        return n * factorial_recursive(n - 1)


def select_unique_questions_recursive(
    all_questions: list,
    num_to_select: int,
    _selected_indices: set = None,  # Zbiór indeksów już wybranych pytań
    _result_questions: list = None   # Lista pytań do zwrócenia
) -> list:
    """
    Recursively selects a specified number of unique questions from a list.

    Note: While this demonstrates recursion, for practical purposes,
    an iterative approach using random.sample or a loop with a set
    is often more efficient and less prone to stack overflow for large N.

    Args:
        all_questions (list): The list of all available question objects.
        num_to_select (int): The number of unique questions to select.
        _selected_indices (set, optional): Internal parameter, set of indices
                                           of questions already selected in current path.
                                           Defaults to None (initialized on first call).
        _result_questions (list, optional): Internal parameter, list of question objects
                                            selected so far. Defaults to None.

    Returns:
        list: A list of unique question objects.
    
    Raises:
        ValueError: If num_to_select is negative or greater than available questions.
    """
    if _selected_indices is None:
        _selected_indices = set()
    if _result_questions is None:
        _result_questions = []

    if not isinstance(num_to_select, int) or num_to_select < 0:
        raise ValueError("Number of questions to select must be a non-negative integer.")
    if num_to_select > len(all_questions):
        raise ValueError("Cannot select more questions than available.")

    # Base Case 1: If we have selected enough questions
    if len(_result_questions) == num_to_select:
        return _result_questions

    # Base Case 2: If no more unique questions are available but we still need more
    if len(_selected_indices) == len(all_questions):
        # We've exhausted all questions but haven't met num_to_select
        # This can happen if num_to_select was greater than actual unique questions
        return _result_questions # Return what we could select

    # Recursive Step: Select a random unique question
    available_to_pick_indices = [i for i in range(len(all_questions)) if i not in _selected_indices]

    if not available_to_pick_indices:
        # No more unselected questions (should be caught by Base Case 2, but for robustness)
        return _result_questions

    # Randomly pick one index from the remaining available questions
    chosen_index = random.choice(available_to_pick_indices)
    
    # Add the chosen index to the set of selected indices
    _selected_indices.add(chosen_index)
    
    # Add the corresponding question object to our result list
    _result_questions.append(all_questions[chosen_index])

    # Recursive call: try to select one less question
    return select_unique_questions_recursive(
        all_questions,
        num_to_select,
        _selected_indices=_selected_indices,
        _result_questions=_result_questions
    )


def timing_decorator(func):
    """
    A decorator that measures the execution time of a function.
    This demonstrates the use of decorators in Python.
    """
    @wraps(func) # Zachowuje nazwę funkcji i docstring oryginalnej funkcji
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter() # Precyzyjny pomiar czasu
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        print(f"[{func.__name__}] Czas wykonania: {execution_time:.4f} sekund")
        return result
    return wrapper

# --- Przykład Dziedziczenia ---

class Shape:
    """Klasa bazowa reprezentująca kształt geometryczny."""
    def __init__(self, color: str):
        self.color = color

    def describe(self) -> str:
        """Zwraca opis ogólny kształtu."""
        return f"To jest {self.color} kształt."

class Circle(Shape):
    """Reprezentuje koło, dziedziczące po klasie Shape."""
    def __init__(self, color: str, radius: float):
        # Wywołanie konstruktora klasy bazowej (Shape) za pomocą super()
        super().__init__(color)
        self.radius = radius

    def describe(self) -> str:
        """Nadpisuje metodę describe z klasy bazowej, aby dodać szczegóły koła."""
        # Rozszerzenie zachowania metody z klasy bazowej
        return f"To jest {self.color} koło o promieniu {self.radius}."

    def area(self) -> float:
        """Oblicza pole powierzchni koła."""
        return 3.14159 * self.radius ** 2


# --- Przykład użycia funkcji reduce ---

def sum_list_elements(numbers: list[int]) -> int:
    """
    Uses functools.reduce to sum all elements in a list of numbers.
    This function demonstrates the use of reduce.

    Args:
        numbers (list[int]): A list of integers.

    Returns:
        int: The sum of all elements.
    """
    if not isinstance(numbers, list) or not all(isinstance(n, int) for n in numbers):
        raise TypeError("Input must be a list of integers.")
    return reduce(lambda acc, x: acc + x, numbers, 0) # 0 to początkowa wartość akumulatora

# --- Przykład testu wydajności z timeit ---

def perform_factorial_calculation():
    """Funkcja pomocnicza do wykonania obliczeń silni (do testu wydajności)."""
    factorial_recursive(10) # Testujemy wydajność dla n=10

def measure_function_performance(func_name: str, setup_code: str, num_runs: int = 100000) -> float:
    """
    Measures the execution time of a given function using timeit.
    This demonstrates performance testing using timeit.

    Args:
        func_name (str): The name of the function to measure (as a string).
        setup_code (str): Setup code for the timeit environment (e.g., imports).
        num_runs (int): Number of times to execute the function for measurement.

    Returns:
        float: The average execution time in seconds.
    """
    # timeit.timeit wykonuje dany kod 'number' razy
    # setup to kod, który jest wykonywany raz przed pomiarem
    time_taken = timeit.timeit(stmt=f"{func_name}()", setup=setup_code, number=num_runs)
    average_time = time_taken / num_runs
    print(f"[{func_name}] Średni czas wykonania ({num_runs} przebiegów): {average_time:.6f} sekund")
    return average_time

# --- Przykład testu pamięci z memory_profiler ---

@profile # Dekorator z memory_profiler do mierzenia zużycia pamięci
def generate_large_data(size_mb: int):
    """
    Generates a large list to demonstrate memory usage.
    This function is used for memory profiling with memory_profiler.

    Args:
        size_mb (int): Desired size of the data in megabytes.
    """
    print(f"\n[memory_profiler] Generowanie danych o rozmiarze {size_mb} MB...")
    # Każdy int w Pythonie zajmuje ok. 28 bajtów
    # 1 MB = 1024 * 1024 bajtów
    # Liczba intów potrzebna = size_mb * 1024 * 1024 / 28
    num_elements = int(size_mb * 1024 * 1024 / 28)
    data = [i for i in range(num_elements)]
    print(f"[memory_profiler] Wygenerowano listę z {len(data)} elementami.")
    # Zmienna 'data' zostanie usunięta po zakończeniu funkcji, zwalniając pamięć.

# --- Funkcja do demonstracji testu jakości kodu (Pylint) ---

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

    # Wywołanie pylint za pomocą os.system lub pylint.lint.run_pylint
    # Używamy zaimplementowanego obiektu pylint_runner do uruchomienia
    exit_code = pylint_runner.run_pylint(pylint_args)

    if exit_code == 0:
        print(f"[Code Quality Check] Pylint zakończył się sukcesem dla {file_path}. Kod spełnia standardy jakości.")
    else:
        print(f"[Code Quality Check] Pylint znalazł problemy w {file_path}. Kod wyjścia: {exit_code}")
    
    return exit_code

