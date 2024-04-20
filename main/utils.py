import re
from functools import lru_cache
from typing import Iterable

from pyarabic.araby import DIACRITICS

from indexes.utils import normalize


@lru_cache(64)
def get_diacritics_insensitive_regexp(query: str) -> re.Pattern:
    query = normalize(query)
    return re.compile(''.join(fr'{letter}[{"".join(DIACRITICS)}]*' for letter in query), re.IGNORECASE)


def find_search_query_position(text: str, query: str, start_index=0) -> tuple[int, int]:
    start = -1
    end = -1
    if query.startswith('"') and query.endswith('"'):
        query = query[1:-1]
        match = re.search(fr'\b{get_diacritics_insensitive_regexp(query).pattern}\b', text[start_index:])
        if match:
            start = match.start() + start_index
            end = match.end() + start_index
    else:
        match = re.search(get_diacritics_insensitive_regexp(query), text[start_index:])
        if match:
            start = match.start() + start_index
            end = match.end() + start_index
    return start, end


@lru_cache(128)
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
        for positions in find_all_search_query_positions(text.content, query):
            results.append({'text': text, 'start': positions[0], 'end': positions[1]})
            in_content_frequency += 1
    return results, in_content_frequency
