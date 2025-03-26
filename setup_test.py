"""Test setup.py."""

import subprocess
import unittest


class TestSetup(unittest.TestCase):
    """Test setup.py."""

    def test_setup_syntax(self):
        """Test setup.py syntax."""
        result = subprocess.run(["python", "setup.py", "check"], capture_output=True, text=True, check=False)
        assert result.returncode == 0, f"setup.py failed with output:\n{result.stdout}\n{result.stderr}"
        # Allow specific expected output in stderr
        allowed_stderr = "INFO - running check"
        assert not result.stderr or allowed_stderr in result.stderr, f"Unexpected error output:\n{result.stderr}"


if __name__ == "__main__":
    unittest.main()
