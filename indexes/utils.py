from functools import lru_cache

from pyarabic.araby import (tokenize, strip_diacritics, strip_tatweel, strip_tashkeel, is_arabicword, COMMA, SEMICOLON,
                            QUESTION)


@lru_cache(128)
def get_words_ranges(text: str) -> list[tuple[str, tuple[int, int]]]:
    words = split_words(text)
    words_ranges = []
    start = 0
    for word in words:
        start = text.find(word, start)
        if start == -1:
            continue
        end = start + len(word)
        words_ranges.append((word, (start, end)))
        start = end
    return words_ranges


@lru_cache(1024)
def is_arabic_word(word):
    return is_arabicword(word) and all(c not in word for c in (COMMA, SEMICOLON, QUESTION))


@lru_cache(maxsize=1024)
def split_words(text, conditions=is_arabic_word):
    return tokenize(text, conditions=conditions or [])


@lru_cache(256)
def normalize(text: str) -> str:
    return strip_tashkeel(strip_tatweel(strip_diacritics(text.lower())))
