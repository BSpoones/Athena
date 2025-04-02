import unittest
from typing import List
from lib.util.list_extensions import group_by, chunked, parse_list_response

# TODO -> Separate out tests properly
# TODO -> Comment code
# TODO -> Ensure full test coverage

class TestGroupBy(unittest.TestCase):
    def test_group_by_normal_strings(self):
        items = ['apple', 'apricot', 'banana', 'blueberry']
        result = group_by(items, key_func=lambda x: x[0])
        expected = {
            'a': ['apple', 'apricot'],
            'b': ['banana', 'blueberry']
        }
        self.assertEqual(result, expected)

    def test_group_by_integers_modulo(self):
        items = [1, 2, 3, 4, 5, 6]
        result = group_by(items, key_func=lambda x: x % 2)
        expected = {
            1: [1, 3, 5],
            0: [2, 4, 6]
        }
        self.assertEqual(result, expected)

    def test_group_by_each_unique_key(self):
        items = [10, 20, 30]
        result = group_by(items, key_func=lambda x: x)
        expected = {10: [10], 20: [20], 30: [30]}
        self.assertEqual(result, expected)

    def test_group_by_all_same_key(self):
        items = ['x', 'y', 'z']
        result = group_by(items, key_func=lambda x: 'same')
        expected = {'same': ['x', 'y', 'z']}
        self.assertEqual(result, expected)

    def test_group_by_empty_list(self):
        items: List[str] = []
        result = group_by(items, key_func=lambda x: x)
        expected = {}
        self.assertEqual(result, expected)

    def test_group_by_key_func_is_none(self):
        items = ['a', 'b']
        with self.assertRaises(TypeError):
            group_by(items, None)  # type: ignore

    def test_group_by_key_func_raises_exception(self):
        items = [1, 2, 3]

        def faulty_key_func(x):
            if x == 2:
                raise ValueError("Invalid item")
            return x

        with self.assertRaises(ValueError):
            group_by(items, faulty_key_func)

    def test_group_by_key_func_returns_non_hashable(self):
        items = ['a', 'b']

        def list_key_func(x):
            return [x]  # lists are not hashable

        with self.assertRaises(TypeError):
            group_by(items, list_key_func)

    def test_group_by_key_func_returns_none(self):
        items = [1, 2, 3]
        result = group_by(items, key_func=lambda x: None)
        expected = {None: [1, 2, 3]}
        self.assertEqual(result, expected)

    def test_group_by_objects_with_attributes(self):
        class Obj:
            def __init__(self, category, name):
                self.category = category
                self.name = name

        items = [
            Obj("fruit", "apple"),
            Obj("fruit", "banana"),
            Obj("veg", "carrot")
        ]
        result = group_by(items, key_func=lambda o: o.category)
        expected_keys = {"fruit", "veg"}
        self.assertEqual(set(result.keys()), expected_keys)
        self.assertEqual([obj.name for obj in result["fruit"]], ["apple", "banana"])
        self.assertEqual([obj.name for obj in result["veg"]], ["carrot"])

class TestChunked(unittest.TestCase):

    def test_even_chunks(self):
        values = [1, 2, 3, 4]
        size = 2
        expected = [[1, 2], [3, 4]]
        result = list(chunked(values, size))
        self.assertEqual(result, expected)

    def test_uneven_chunks(self):
        values = [1, 2, 3, 4, 5]
        size = 2
        expected = [[1, 2], [3, 4], [5]]
        result = list(chunked(values, size))
        self.assertEqual(result, expected)

    def test_chunk_size_larger_than_list(self):
        values = [1, 2]
        size = 10
        expected = [[1, 2]]
        result = list(chunked(values, size))
        self.assertEqual(result, expected)

    def test_chunk_size_equal_to_list_length(self):
        values = [1, 2, 3]
        size = 3
        expected = [[1, 2, 3]]
        result = list(chunked(values, size))
        self.assertEqual(result, expected)

    def test_empty_list(self):
        values: List[int] = []
        size = 3
        expected = []
        result = list(chunked(values, size))
        self.assertEqual(result, expected)

    def test_chunk_size_is_one(self):
        values = [1, 2, 3]
        size = 1
        expected = [[1], [2], [3]]
        result = list(chunked(values, size))
        self.assertEqual(result, expected)

    def test_chunk_size_zero_raises(self):
        values = [1, 2, 3]
        with self.assertRaises(ValueError):
            list(chunked(values, 0))

    def test_chunk_size_negative_raises(self):
        values = [1, 2, 3]
        with self.assertRaises(ValueError):
            list(chunked(values, -2))

    def test_non_integer_chunk_size_raises(self):
        values = [1, 2, 3]
        with self.assertRaises(TypeError):
            list(chunked(values, "two"))  # type: ignore

class TestParseListResponse(unittest.TestCase):

    def test_single_group_single_line(self):
        response = "Hello"
        expected = [["Hello"]]
        self.assertEqual(parse_list_response(response), expected)

    def test_single_group_multiple_lines(self):
        response = "Hi\nThere"
        expected = [["Hi", "There"]]
        self.assertEqual(parse_list_response(response), expected)

    def test_multiple_groups(self):
        response = "A1\nA2\n\nB1\nB2"
        expected = [["A1", "A2"], ["B1", "B2"]]
        self.assertEqual(parse_list_response(response), expected)

    def test_null_handling(self):
        response = "null"
        expected = [[]]
        self.assertEqual(parse_list_response(response), expected)

    def test_null_with_whitespace(self):
        response = "  null  "
        expected = [[]]
        self.assertEqual(parse_list_response(response), expected)

    def test_null_among_other_lines(self):
        response = "Line1\nnull\nLine2"
        expected = [[]]  # Entire group is considered null if any line is "null"
        self.assertEqual(parse_list_response(response), expected)

    def test_mixed_valid_and_null_groups(self):
        response = "A1\nA2\n\nnull\n\nB1"
        expected = [["A1", "A2"], [], ["B1"]]
        self.assertEqual(parse_list_response(response), expected)

    def test_empty_string(self):
        response = ""
        expected = [[]]
        self.assertEqual(parse_list_response(response), expected)

    def test_whitespace_only(self):
        response = "   \n  "
        expected = [[]]
        self.assertEqual(parse_list_response(response), expected)

    def test_group_with_empty_lines(self):
        response = "\n\n\nHello\n\n\nWorld"
        expected = [["Hello"], ["World"]]
        self.assertEqual(parse_list_response(response), expected)

    def test_uppercase_NULL(self):
        response = "NULL"
        expected = [[]]
        self.assertEqual(parse_list_response(response), expected)

    def test_group_with_mixed_case_null(self):
        response = "NuLl"
        expected = [[]]
        self.assertEqual(parse_list_response(response), expected)

    def test_leading_and_trailing_whitespace(self):
        response = "  line1  \n  line2  \n\n null \n\n  line3  "
        expected = [["line1", "line2"], [], ["line3"]]
        self.assertEqual(parse_list_response(response), expected)