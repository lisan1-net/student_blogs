import re
from functools import lru_cache

from pyarabic.araby import (tokenize, strip_diacritics, strip_tatweel, strip_tashkeel, is_arabicword, COMMA, SEMICOLON,
                            QUESTION)

tagging_pattern = re.compile(r'(<[^>]+>)([^<]+)(</[^>]+>)')


@lru_cache(128)
def get_words_ranges(text: str) -> list[tuple[str, tuple[int, int]]]:
    text = re.sub(tagging_pattern, r'\2', text)
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


@lru_cache(256)
def separate_tags_positions_and_text(text: str) -> tuple[list[tuple[int, str]], str]:
    """
    Extract opening and closing XML tags with their positions, along with the text without these tags.
    The positions are relative to the text without the tags.
    :param text: the text to extract tags from
    :return: a tuple of two elements:
        - a list of tuples, each containing the position of the tag and the tag itself
        - the text without the tags

    Example:
    >>> separate_tags_positions_and_text("قل <p>الحمد لله</p> <span>رب العالمين</span> الرحمن الرحيم")
    ([(3, '<p>'), (12, '</p>'), (13, '<span>'), (24, '</span>')], 'قل الحمد لله رب العالمين الرحمن الرحيم')
    """
    tags_positions = []
    tags = []
    search_index = 0
    text_without_tags = ''
    while True:
        match = tagging_pattern.search(text, search_index)
        if not match:
            text_without_tags += text[search_index:]
            break
        opening_tag, tag_content, closing_tag = match.groups()
        tags.extend((opening_tag, closing_tag))
        text_without_tags += text[search_index:match.start()]
        tags_positions.append((len(text_without_tags), opening_tag))
        text_without_tags += tag_content
        tags_positions.append((len(text_without_tags), closing_tag))
        search_index = match.end()
    return tags_positions, text_without_tags
