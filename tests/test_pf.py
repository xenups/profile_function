import unittest
from unittest.mock import MagicMock

from profile_function import ProfileFunction


class TestProfileFunction(unittest.TestCase):
    def setUp(self):
        # Mocking the backend for testing
        self.backend = MagicMock()
        self.backend.name_separator = "."
        self.profile_function = ProfileFunction(self.backend)

    def test_get_name(self):
        name = ProfileFunction.get_name("func_name", "group", "block_name")
        self.assertEqual(name, "group.func_name.block_name")

        name_without_block = ProfileFunction.get_name("func_name", "group")
        self.assertEqual(name_without_block, "group.func_name")

    def test_get_profiling_metric_name(self):
        metric_name = self.profile_function.get_profiling_metric_name("func_name", "group", "block_name")
        expected_metric_name = "functions_profile.time.group.func_name.block_name"
        self.assertEqual(metric_name, expected_metric_name)

    def test_profile_block(self):
        with self.profile_function.profile_block("block_name", "group", "block"):
            pass  # Add any code block you want to profile

        # Ensure backend.timer was called with the correct metric name
        self.backend.timer.assert_called_once_with("functions_profile.time.group.block_name.block")

    def test_profile_function(self):
        # Define a dummy function
        def dummy_function():
            pass

        # Profile the dummy function
        profiled_function = self.profile_function.profile_function()(dummy_function)

        # Call the profiled function
        profiled_function()

        # Ensure backend.timer was called with the correct metric name
        self.backend.timer.assert_called_once_with("functions_profile.time.other.dummy_function")


if __name__ == "__main__":
    unittest.main()
