import unittest

from app.ranges import redis_range_to_python_slice

# prefix + index, so each item names its own position
LST = ["a0", "a1", "a2", "a3", "a4", "a5", "a6", "a7"]


def lrange(start, stop):
    py_start, py_stop = redis_range_to_python_slice(start, stop, len(LST))
    return LST[py_start:py_stop]


def items(lo, hi):
    """Expected items a<lo>..a<hi>, inclusive."""
    return [f"a{i}" for i in range(lo, hi + 1)]


class TestRedisRangeToSlice(unittest.TestCase):
    def test_zero_to_minus_seven_gives_first_two(self):
        self.assertEqual(lrange(0, -7), ["a0", "a1"])

    def test_segment1_happy_path(self):
        cases = [
            (0, 0, items(0, 0)),
            (0, 5, items(0, 5)),
            (0, 7, items(0, 7)),
            (3, 3, items(3, 3)),
            (3, 5, items(3, 5)),
            (3, 7, items(3, 7)),
            (7, 7, items(7, 7)),
        ]
        for start, stop, expected in cases:
            with self.subTest(start=start, stop=stop):
                self.assertEqual(lrange(start, stop), expected)

    def test_segment2_stop_past_end(self):
        cases = [
            (0, 8, items(0, 7)),
            (0, 10, items(0, 7)),
            (3, 8, items(3, 7)),
            (3, 10, items(3, 7)),
            (7, 8, items(7, 7)),
            (7, 10, items(7, 7)),
        ]
        for start, stop, expected in cases:
            with self.subTest(start=start, stop=stop):
                self.assertEqual(lrange(start, stop), expected)

    def test_segment3_start_past_end(self):
        cases = [
            (8, 0, []),
            (8, 4, []),
            (8, 7, []),
        ]
        for start, stop, expected in cases:
            with self.subTest(start=start, stop=stop):
                self.assertEqual(lrange(start, stop), expected)

    def test_segment4_both_past_end(self):
        cases = [
            (8, 8, []),
            (8, 10, []),
        ]
        for start, stop, expected in cases:
            with self.subTest(start=start, stop=stop):
                self.assertEqual(lrange(start, stop), expected)

    def test_segment5_negative_stop(self):
        cases = [
            (0, -1, items(0, 7)),
            (0, -5, items(0, 3)),
            (0, -7, items(0, 1)),
            (0, -8, items(0, 0)),
            (4, -1, items(4, 7)),
            (4, -4, items(4, 4)),
            (4, -5, []),  # normalizes to 4,3: start > stop
            (4, -7, []),
            (4, -8, []),
        ]
        for start, stop, expected in cases:
            with self.subTest(start=start, stop=stop):
                self.assertEqual(lrange(start, stop), expected)

    def test_segment6_negative_start_and_beyond_range(self):
        cases = [
            (-1, -1, items(7, 7)),
            (-4, -1, items(4, 7)),  # last 4
            (-3, -5, []),  # 5,3: direction never reverses
            (-9, -1, items(0, 7)),  # start before list -> clamp to 0
            (-100, 2, items(0, 2)),
            (0, -9, []),  # stop before list -> empty
            (0, -10, []),
            (-100, -100, []),
        ]
        for start, stop, expected in cases:
            with self.subTest(start=start, stop=stop):
                self.assertEqual(lrange(start, stop), expected)


if __name__ == "__main__":
    unittest.main()
