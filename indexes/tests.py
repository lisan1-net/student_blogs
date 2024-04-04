from django.test import SimpleTestCase

from indexes.utils import *


class TestGetWordsRanges(SimpleTestCase):

    def test_get_words_ranges_diacritized(self):
        # Test with a diacritized Arabic sentence
        sentence = "بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ"
        expected_ranges = [("بِسْمِ", (0, 6)), ("اللَّهِ", (7, 14)), ("الرَّحْمَنِ", (15, 26)), ("الرَّحِيمِ", (27, 37))]
        self.assertEqual(get_words_ranges(sentence), expected_ranges)

        # Test with another diacritized Arabic sentence
        sentence = "الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ"
        expected_ranges = [("الْحَمْدُ", (0, 9)), ("لِلَّهِ", (10, 17)), ("رَبِّ", (18, 23)), ("الْعَالَمِينَ", (24, 37))]
        self.assertEqual(get_words_ranges(sentence), expected_ranges)

    def test_get_words_ranges_non_diacritized(self):
        # Test with a non-diacritized Arabic sentence
        sentence = "الحمد لله رب العالمين"
        expected_ranges = [("الحمد", (0, 5)), ("لله", (6, 9)), ("رب", (10, 12)), ("العالمين", (13, 21))]
        self.assertEqual(get_words_ranges(sentence), expected_ranges)

    def test_get_words_ranges_mixed(self):
        # Test with a mixed Arabic sentence
        sentence = "الْحَمْدُ لِلَّهِ رب الْعَالَمِينَ"
        expected_ranges = [("الْحَمْدُ", (0, 9)), ("لِلَّهِ", (10, 17)), ("رب", (18, 20)), ("الْعَالَمِينَ", (21, 34))]
        self.assertEqual(get_words_ranges(sentence), expected_ranges)

    def test_get_words_ranges_punctuation(self):
        # Test with an Arabic sentence with punctuation
        sentence = "الْحَمْدُ لِلَّهِ، رب الْعَالَمِينَ."
        expected_ranges = [("الْحَمْدُ", (0, 9)), ("لِلَّهِ", (10, 17)), ("رب", (19, 21)), ("الْعَالَمِينَ", (22, 35))]
        self.assertEqual(get_words_ranges(sentence), expected_ranges)

    def test_get_words_ranges_numbers(self):
        # Test with an Arabic sentence with numbers
        sentence = "الْحَمْدُ لِلَّهِ 123 رب الْعَالَمِينَ"
        expected_ranges = [("الْحَمْدُ", (0, 9)), ("لِلَّهِ", (10, 17)), ("رب", (22, 24)), ("الْعَالَمِينَ", (25, 38))]
        self.assertEqual(get_words_ranges(sentence), expected_ranges)

    def test_get_words_ranges_empty(self):
        # Test with an empty string
        sentence = ""
        expected_ranges = []
        self.assertEqual(get_words_ranges(sentence), expected_ranges)

    def test_get_words_ranges_single(self):
        # Test with a single word
        sentence = "الله"
        expected_ranges = [("الله", (0, 4))]
        self.assertEqual(get_words_ranges(sentence), expected_ranges)


class TestNormalize(SimpleTestCase):

    def test_normalize_diacritized(self):
        # Test with a diacritized Arabic word
        word = "اللَّهِ"
        expected_normalized = "الله"
        self.assertEqual(normalize(word), expected_normalized)

    def test_normalize_non_diacritized(self):
        # Test with a non-diacritized Arabic word
        word = "الله"
        self.assertEqual(normalize(word), word)

    def test_normalize_mixed(self):
        # Test with a mixed Arabic word
        word = "رب الْعَالَمِينَ"
        expected_normalized = "رب العالمين"
        self.assertEqual(normalize(word), expected_normalized)

    def test_normalize_punctuation(self):
        # Test with an Arabic word with punctuation
        word = "الْعَالَمِينَ."
        expected_normalized = "العالمين."
        self.assertEqual(normalize(word), expected_normalized)

        # Test with another Arabic word with punctuation
        word = "الْحَمْدُ،"
        expected_normalized = "الحمد،"
        self.assertEqual(normalize(word), expected_normalized)

    def test_normalize_numbers(self):
        # Test with an Arabic word with numbers
        word = "123"
        self.assertEqual(normalize(word), word)

        # Test with another Arabic word with numbers
        word = "١٢٣"
        self.assertEqual(normalize(word), word)

    def test_normalize_empty(self):
        # Test with an empty string
        word = ""
        self.assertEqual(normalize(word), word)


class TestSegment(SimpleTestCase):

    def test_segment_diacritized(self):
        # Test with a diacritized Arabic word
        word = "اللَّهِ"
        expected_segments = ("ال", "له", "")
        self.assertEqual(segment(word), expected_segments)

    def test_segment_non_diacritized(self):
        # Test with a non-diacritized Arabic word
        word = "الله"
        expected_segments = ("ال", "له", "")
        self.assertEqual(segment(word), expected_segments)

    def test_segment_mixed(self):
        # Test with a mixed Arabic word
        word = "الْعَالَمِين"
        expected_segments = ("ال", "عالم", "ين")
        self.assertEqual(segment(word), expected_segments)

    def test_segment_numbers(self):
        # Test with an Arabic word with numbers
        word = "123"
        expected_segments = ("", "123", "")
        self.assertEqual(segment(word), expected_segments)

        # Test with another Arabic word with numbers
        word = "١٢٣"
        expected_segments = ("", "١٢٣", "")
        self.assertEqual(segment(word), expected_segments)

    def test_segment_empty(self):
        # Test with an empty string
        word = ""
        expected_segments = ("", "", "")
        self.assertEqual(segment(word), expected_segments)
