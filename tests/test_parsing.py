"""
Unit tests for input-file parsing
"""
import os.path

from alpha_parse.alpha_parse import GymSession
from datetime import datetime

import pytest


@pytest.fixture()
def session_from_file():
    def f(file_name):
        with open(os.path.join("test_data", file_name), "r") as input_txt:
            lines = input_txt.readlines()
            session = GymSession(lines)

            session.parse_session()
            return session

    return f


class TestSession:
    @pytest.mark.parametrize("input_file,attr, exp", [
        ("legs_session.txt", "_date", datetime(year=2022, month=3, day=31)),
        ("legs_session.txt", "_plan", "Bro split"),
        ("day3_session.txt", "_date", datetime(year=2022, month=3, day=10)),
        ("day3_session.txt", "_plan", "3 + Sundays")])
    def test_attr(self, input_file, attr, exp, session_from_file):
        session = session_from_file(input_file)
        assert getattr(session, attr) == exp


if __name__ == '__main__':
    pass