from functools import lru_cache

from pyarabic.araby import tokenize, strip_diacritics, strip_tatweel, strip_tashkeel
from tashaphyne.stemming import ArabicLightStemmer


@lru_cache(128)
def get_words_ranges(text: str) -> list[tuple[str, tuple[int, int]]]:
    words = tokenize(text)
    words_ranges = []
    start = 0
    for word in words:
        start = text.find(word, start)
        end = start + len(word)
        words_ranges.append((word, (start, end)))
        start = end
    return words_ranges


@lru_cache(256)
def normalize(text: str) -> str:
    return strip_tashkeel(strip_tatweel(strip_diacritics(text.lower())))


@lru_cache(256)
def segment(word: str) -> tuple[str, str, str]:
    word = normalize(word)
    stem = ArabicLightStemmer().light_stem(word)
    try:
        if stem:
            prefix, suffix = word.split(stem)
        else:
            prefix = suffix = ''
    except ValueError:
        prefix = suffix = ''
    return prefix, stem, suffix
