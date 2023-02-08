import collections
from jieba import cut

level_sets = [set() for _ in range(7)]

for hsk_levels in range(1, 8):
    with open(f'hsk{hsk_levels}.txt', 'r') as file:
        hsk_set = set()
        for line in file:
            character = line.strip()
            hsk_set.add(character)
            found = False
            for i in range(1, hsk_levels):
                if character in level_sets[i-1]:
                    found = True
                    break
            if not found:
                level_sets[hsk_levels-1].add(character)

def find_hsk_level(character):
    for level, level_set in enumerate(level_sets):
        if character in level_set:
            return level+1
    return None

def profiler(path='characters.txt'):
    n_characters = 0
    counter = [0 for i in range(7)]
    not_found_characters = []
    not_found_number = 0
    with open(path, 'r') as file:
        line = file.read()
        words = jieba.cut(line)
        for word in words:
            for character in word:
                if character not in hsk_set:
                    not_found_number += 1
                n_characters += 1
                level = find_hsk_level(character)
                if level is not None:
                    counter[level-1] += 1

    for level, count in enumerate(counter):
        print(f"HSK level {level+1}: {count} characters")
    print(f"HSK level 7-9: {count} characters")

    total_characters = sum(counter)
    average_hsk_level = sum((level+1) * count for level, count in enumerate(counter)) / total_characters
    print(f"Average HSK level: {average_hsk_level:.2f}")
    print(f'Total number of characters is: {n_characters}')
    print(f'Number of characters found in HSK lists: {total_characters}')
