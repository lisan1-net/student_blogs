from typing import Iterable

from main.models import Text


def find_search_query_position(text: str, query: str, start_index=0) -> tuple[int, int]:
    text = text.lower()
    query = query.lower()
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


def find_search_results(query: str, search_in_content: bool, texts: Iterable[Text]) -> tuple[list[dict], int, int]:
    in_title_frequency = 0
    in_content_frequency = 0
    results = []
    for text in texts:
        for positions in find_all_search_query_positions(text.title_normalized, query):
            results.insert(
                in_title_frequency,
                {'text': text, 'start': positions[0], 'end': positions[1], 'field': 'title'}
            )
            in_title_frequency += 1
        if search_in_content:
            for positions in find_all_search_query_positions(text.content_normalized, query):
                results.append({'text': text, 'start': positions[0], 'end': positions[1], 'field': 'content'})
                in_content_frequency += 1
    return results, in_title_frequency, in_content_frequency
