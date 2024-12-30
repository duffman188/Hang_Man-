"""Game of Hangman with the option to partition (view possible answers by submitting a negative number)"""

"""Created by La'Ron Latin"""


import random
from collections import defaultdict

# Function to load words from a designated file
def load_words(filename):
    """Load words from a text file, one word per line."""
    try:
        with open(filename, 'r') as file:
            words = [line.strip().lower() for line in file if line.strip()]
        return words
    except FileNotFoundError:
        print(f"File '{filename}' not found. Please check the file path.")
        return []

# Function to mask the word
def mask_word(word, guessed):
    """Returns word with all letters not in guessed replaced with hyphens."""
    return ''.join(letter if letter in guessed else '-' for letter in word)

# Function to create partitions based on guessed letters
def partition(words, guessed):
    """Generates partitions of the set words based on guessed letters."""
    partitions = defaultdict(set)
    for word in words:
        masked = mask_word(word, guessed)
        partitions[masked].add(word)
    return partitions

# Function to select the largest partition with the fewest revealed letters
def max_partition(partitions):
    """Selects the hint with the largest partition, fewest revealed letters, or at random if tied."""
    max_size = max(len(words) for words in partitions.values())
    largest_partitions = [mask for mask, words in partitions.items() if len(words) == max_size]

    # Prefer partition with fewer revealed letters
    largest_partitions.sort(key=lambda mask: mask.count('-'))

    # Choose randomly if still tied
    chosen_mask = random.choice(largest_partitions)
    return chosen_mask


# Main game logic
def play_hangman(filename):
    word_list = load_words(filename)
    if not word_list:
        print("Unable to load words. Exiting game.")
        return

    while True:  # Start a new loop for replaying the game
        # Get word length from user and validate word availability
        while True:
            try:
                word_length = input(
                    "Enter word length (positive for regular play, negative for detailed play, or type 'quit' to exit): ")
                if word_length.lower() == 'quit':
                    print("Exiting game, Goodbye!")
                    return

                word_length = int(word_length)

                if word_length == 0:
                    print("Word length must be a positive or negative integer.")
                    continue

                # Filter words by chosen length
                words = {word for word in word_list if len(word) == abs(word_length)}

                if not words:
                    print(f"No words of length {abs(word_length)} found. Please choose a different length.")
                else:
                    break  # Valid length with available words
            except ValueError:
                print("Invalid input. Please enter a valid integer for word length.")

        show_details = word_length < 0
        guessed = set()
        remaining_guesses = 5
        hint = '-' * abs(word_length)
        won = False  # Initialize win flag

        # Main game loop
        while remaining_guesses > 0 and '-' in hint:
            print(f"\nYou have {remaining_guesses} guesses remaining")
            print(f"Guessed letters: {guessed}")
            print(f"Current hint: {hint}")

            if show_details:
                print(f"Potential words: {words}")
                print(f"There are {len(words)} possible words")

            try:
                guess = input("Enter a letter: ").lower()

                # Check if the input is a single letter
                if not guess.isalpha() or len(guess) != 1:
                    raise ValueError("Input must be a single alphabetical letter.")

                if guess in guessed:
                    raise ValueError(f"You have already guessed the letter '{guess}'. Try again.")

                guessed.add(guess)

            except ValueError as ve:
                print(ve)
                continue

            partitions = partition(words, guessed)

            if show_details:
                print("Partitions:")
                for p_hint, p_words in partitions.items():
                    print(f"{p_hint}: {p_words}")

            previous_hint = hint
            hint = max_partition(partitions)
            words = partitions[hint]

            if guess not in hint:
                print(f"I'm sorry '{guess}' is not in the word.")
                remaining_guesses -= 1
            else:
                print(f"Yes! '{guess}' is in the word!")

            # Check if the hint changed; if not, it's an incorrect guess
            if previous_hint == hint:
                print(f"'{guess}' did not change the word.")

            if '-' not in hint:
                print(f"You win! The word was {hint}")
                won = True
                break

        # Only print the loss message if the player didn't win
        if not won:
            print(f"You have lost. The word was {random.choice(list(words))}")

        # Ask the user if they want to play again or quit
        while True:
            try:
                play_again = input("Do you want to play again? (y/n): ").strip().lower()
                if play_again not in ['y', 'n']:
                    raise ValueError("Please enter 'y' or 'n'.")
                if play_again == 'n':
                    print("Thanks for playing! Goodbye!")
                    return
                break
            except ValueError as e:
                print(e)

# Test cases for the game logic

def load_words_for_tests(filename):
    """Helper function to load words for tests."""
    try:
        with open(filename, 'r') as file:
            return [line.strip().lower() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"Test file '{filename}' not found.")
        return []

# Test for mask_word functionality
def test_mask_word():
    """Test the mask_word function."""
    word_list = load_words_for_tests("/Users/laronlatin/Desktop/Python Files/hangman_words.txt")
    if word_list:
        test_word = random.choice(word_list)
        guessed_letters = set(random.sample(test_word, min(3, len(test_word))))
        masked_result = mask_word(test_word, guessed_letters)

        assert all((letter in guessed_letters or mask == '-') for letter, mask in zip(test_word, masked_result)), \
            "mask_word did not correctly apply the mask."


# Test for partition functionality
def test_partition():
    """Test the partition function."""
    word_list = load_words_for_tests("/Users/laronlatin/Desktop/Python Files/hangman_words.txt")
    if word_list:
        test_words = set(random.sample(word_list, min(3, len(word_list))))
        guessed_letters = {letter for word in test_words for letter in random.sample(word, min(2, len(word)))}
        partitions = partition(test_words, guessed_letters)

        for masked, words in partitions.items():
            assert all(mask_word(word, guessed_letters) == masked for word in words), \
                "partition did not correctly group words by mask."


# Test for max_partition functionality
def test_max_partition():
    """Test the max_partition function."""
    word_list = load_words_for_tests("/Users/laronlatin/Desktop/Python Files/hangman_words.txt")
    if word_list:
        test_words = set(random.sample(word_list, min(3, len(word_list))))
        guessed_letters = {letter for word in test_words for letter in random.sample(word, min(2, len(word)))}
        partitions = partition(test_words, guessed_letters)
        max_part = max_partition(partitions)

        assert max_part in partitions, "max_partition did not return a valid partition key."


# Additional test for handling empty word list
def test_partition_with_empty_word_list():
    """Test partition function with an empty word list."""
    empty_word_list = set()
    guessed_letters = {'a', 'e', 'i', 'o', 'u'}
    partitions = partition(empty_word_list, guessed_letters)

    assert len(partitions) == 0, "Partitions should be empty when no words are provided."


# Additional test for guessing all letters
def test_mask_word_all_guessed():
    """Test mask_word when all letters in the word are guessed."""
    test_word = "python"
    guessed_letters = set(test_word)  # Guess all letters in the word
    masked_result = mask_word(test_word, guessed_letters)

    assert masked_result == test_word, "mask_word should reveal the entire word when all letters are guessed."


# Run all tests
if __name__ == "__main__":
    test_mask_word()
    test_partition()
    test_max_partition()
    test_partition_with_empty_word_list()
    test_mask_word_all_guessed()

# Run the game
if __name__ == "__main__":
    # Play the game using the file
    filename = "/Users/laronlatin/Desktop/Python Files/hangman_words.txt"
    play_hangman(filename)

