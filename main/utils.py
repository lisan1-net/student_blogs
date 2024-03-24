import re
from collections import Counter
from typing import Iterable
from functools import lru_cache

from pyarabic.araby import strip_tatweel, strip_diacritics, tokenize, is_arabicword, COMMA, SEMICOLON, QUESTION


def find_search_query_position(text: str, query: str, start_index=0) -> tuple[int, int]:
    text = normalize(text)
    query = normalize(query)
    start = -1
    if query.startswith('"') and query.endswith('"'):
        query = query[1:-1]
        match = re.search(fr'\b{query}\b', text[start_index:])
        if match:
            start = match.start() + start_index
    else:
        start = text.find(query, start_index)
    if start == -1:
        return -1, -1
    end = start + len(query)
    return start, end


def find_all_search_query_positions(text: str, query: str) -> list[tuple[int, int]]:
    positions = []
    start = 0
    while start != -1:
        start, end = find_search_query_position(text, query, start)
        if start != -1:
            positions.append((start, end))
            start = end
    return positions


def find_search_results(query: str, texts: Iterable) -> tuple[list[dict], int]:
    in_content_frequency = 0
    results = []
    for text in texts:
        for positions in find_all_search_query_positions(text.content_normalized, query):
            results.append({'text': text, 'start': positions[0], 'end': positions[1]})
            in_content_frequency += 1
    words = query.split()
    if len(words) > 1:
        for word in words:
            r, c = find_search_results(word, texts)
            results += r
            in_content_frequency += c
    return results, in_content_frequency


@lru_cache(maxsize=1024)
def normalize(text):
    return strip_tatweel(strip_diacritics(text.lower()))


@lru_cache(maxsize=1024)
def split_words(text):
    return tokenize(text, conditions=is_arabic_word)


def is_arabic_word(word):
    return is_arabicword(word) and all(c not in word for c in (COMMA, SEMICOLON, QUESTION))


@lru_cache(maxsize=1024)
def get_word_frequencies(texts):
    frequencies = Counter()
    for text in texts:
        frequencies.update(split_words(text.content_normalized))
    return frequencies
