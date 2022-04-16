"""
Unit tests for input-file parsing
"""
from datetime import datetime
import os.path
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(__file__, "..")))

from alpha_parse.parse import GymSessionParser, InputCleaner
import pytest


@pytest.fixture()
def session_from_file():
    def f(file_name):
        lines = InputCleaner.lines_from_file(file_name)
        session = GymSessionParser(lines)

        session.parse_session()
        return session

    return f


class TestSessionParsing:
    @pytest.mark.parametrize("input_file,attr, exp", [
        ("legs_session.txt", "_date", datetime(year=2022, month=3, day=31)),
        ("legs_session.txt", "_plan", "Bro split"),
        ("day3_session.txt", "_date", datetime(year=2022, month=3, day=10)),
        ("day3_session.txt", "_plan", "3 + Sundays")])
    def test_attr(self, input_file, attr, exp, session_from_file):
        session = session_from_file(Path("test_data") / input_file)
        assert getattr(session, attr) == exp


if __name__ == '__main__':
    pass
