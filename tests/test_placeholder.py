# Placeholder so pytest collects at least one test (exit code 5 otherwise).
# Remove once the real integration tests exist (T5.1).
import sys


def test_runs_on_python_315() -> None:
    assert sys.version_info[:2] == (3, 15)
