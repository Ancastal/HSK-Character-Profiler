import collections
from nltk import sent_tokenize
from jieba import cut

hsk1, hsk2, hsk3, hsk4, hsk5, hsk6, hsk7 = [set() for _ in range(7)]
level_sets = OrderedDict(zip(range(1, 8), [hsk1, hsk2, hsk3, hsk4, hsk5, hsk6, hsk7]))

for hsk_levels in range(1, 8):
    with open('hsk{}.txt'.format(hsk_levels), 'r') as file:
        # Iterate through each line in the file
        hsk_set = set()
        for line in file:
            # Remove any leading or trailing whitespace
            character = line.strip()
            hsk_set.add(character)
            # Sometimes HSK lists present hanzi that are already included in the previous levels
            # Check if the character is already present in any of the previous sets
            found = False
            for i in range(1, hsk_levels):
                if character in level_sets[i]:
                    found = True
                    break
            # This adds the character to the current set only if it is not present in any of the previous sets
            if not found:
                level_set = level_sets[hsk_levels]
                level_set.add(character)

# Print the list of characters
def find_hsk_level(character):
    for level, level_set in level_sets.items():
        if character in level_set:
            return level
    return None

# Open the file in read mode
def profiler(path='characters.txt'):
    n_characters = 0
    with open(path, 'r') as file:
        # Initialize an OrderedDict to count the characters per level
        counter = OrderedDict([(i, 0) for i in range(1, 8)])
        not_found_characters = []
        not_found_number = 0
        # Iterate through the file
        line = file.read()
        # Use jieba.cut to split the line into words
        words = jieba.cut(line)
        # Iterate through each word in the line
        for word in words:
            # Iterate through each character in the word
            for character in word:
                if character not in hsk_set:
                    not_found_number += 1
                n_characters += 1
                # Find the HSK level of the character
                level = find_hsk_level(character)
                # Increment the count for the level
                if level is not None:
                    if level in counter:
                        counter[level] += 1
                    else:
                        counter[level] = 1

    # Print the count for each level
    for level, count in counter.items():
        if (level == 7):
            print(f"HSK level 7-9: {count} characters")
        else:
            print(f"HSK level {level}: {count} characters")


    # Initialize a variable to keep track of the total number of characters
    total_characters = 0

    # Iterate through the counter object and sum the total number of characters per level
    for level, count in counter.items():
        total_characters += count

    # Calculate the average HSK level by dividing the total number of characters per level by the total number of characters
    average_hsk_level = sum(level * count for level, count in counter.items()) / total_characters
    # Print the average HSK level
    print(f"Average HSK level: {average_hsk_level:.2f}")
    print(f'Total number of characters is: {n_characters}')
    print(f'Number of characters found in HSK lists: {total_characters}')
