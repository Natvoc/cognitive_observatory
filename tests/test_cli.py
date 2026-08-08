import subprocess
import sys


def test_cli_version() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "core.cli", "--version"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "cognitive-observatory" in result.stdout
