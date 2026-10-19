

import unittest

from sanitize import clean_sensor_readings


class CleanSensorReadingsTest(unittest.TestCase):
    def test_mixed_input_is_converted_filtered_and_clipped(self):
        raw = ["12.5", 7, None, "abc", -3, "-1.5", 750, "500.1", 0, "  42 "]
        self.assertEqual(
            clean_sensor_readings(raw),
            [12.5, 7.0, 500.0, 500.0, 0.0, 42.0],
        )

    def test_empty_and_none_input_return_empty_list(self):
        self.assertEqual(clean_sensor_readings([]), [])
        self.assertEqual(clean_sensor_readings(None), [])

    def test_all_invalid_entries_return_empty_list(self):
        raw = [None, "error", "", -1, "-99", [1, 2], {"a": 1}, float("nan")]
        self.assertEqual(clean_sensor_readings(raw), [])

    def test_boundary_values(self):
        self.assertEqual(clean_sensor_readings([0, 500, 500.0]), [0.0, 500.0, 500.0])


if __name__ == "__main__":
    unittest.main()
