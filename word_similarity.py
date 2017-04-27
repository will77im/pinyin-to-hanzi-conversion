import re
from collections import Counter


def levenshtein_distance(s1, s2):
    if len(s1) > len(s2):
        s1, s2 = s2, s1
    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2+1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]


def most_similar_words(word, all_words, threshold):
    similarities = []
    for w in all_words:
        edit_distance = levenshtein_distance(word, w)
        if edit_distance <= threshold:
            similarities.append((w, edit_distance))
    sorted_sim = sorted(similarities, key=lambda sim: sim[1])
    return sorted_sim


def count_all_words(input_file):
    with open(input_file, 'r') as in_file:
        all_words = re.findall(r'\w+', in_file.read().lower())
        return all_words, Counter(all_words)


def fix_typo(word, all_words, word_counts, threshold=1):
    if word in all_words:
        return word
    sim_words = most_similar_words(word, all_words, threshold)
    highest_freq = 0
    best_word = word
    for w in sim_words:
        if word_counts[w] > highest_freq:
            highest_freq = word_counts[w]
            best_word = w
    return best_word
