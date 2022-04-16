import logging
import re
from collections import namedtuple, defaultdict
from datetime import datetime
from pathlib import Path

import pandas as pd

from alpha_parse.exercise import ExerciseSet


class GymSessionParser:
    """
    Parse a gym session
    """
    PLAN_PAT = "^(.+) Week ([0-9]*) (.*)"
    DATE_PAT = "([0-9]{4}-[0-9]{2}-[0-9]{2})"
    EXERCISE_PAT = r"[0-9]+\. (.+)"
    DATE_FORMAT = "%Y-%m-%d"
    COLUMNS = ("date", "plan", "exercise", "weight", "reps")

    def __init__(self, lines: list, separator=";"):
        self.lines = lines
        self.sep = separator

        self._plan = None
        self._date: datetime
        self._exercises = []
        self._sets = defaultdict(list)  # reps[exercise] = [(weight, reps)]

    def parse_session(self):
        self._find_date_plan()
        self._find_exercises()

    def _find_date_plan(self):
        for li in self.lines:
            match = re.search(self.DATE_PAT, li)
            if match:
                self._date = datetime.strptime(match.group(1), self.DATE_FORMAT)
                logging.debug(f"GymSession on {self._date}")
            match = re.match(self.PLAN_PAT, li)
            if match:
                self._plan = match.group(3).rstrip()
                logging.debug(f"GymSession using {self._plan}")

            if self._plan and self._date:
                return

        self._plan = None
        if not self._date:
            raise Exception(
                "Couldn't find date in session" + "\n".join(self.lines))

    def _find_exercises(self):
        i = 0
        while i < len(self.lines):
            match = self.exercise_match(self.lines[i])
            if match:
                self._exercises.append(match.group(1))
                while i + 1 < len(self.lines):
                    i += 1
                    if self.exercise_match(self.lines[i]) or self.date_match(
                            self.lines[i]):
                        break

                    self._sets[self._exercises[-1]].append(self.lines[i])
            else:
                i += 1

        logging.info(f"Found {len(self._exercises)} exercises.")
        self._parse_sets()

    def _parse_sets(self):
        for exercise in self._exercises:
            sets = []
            lines = self._sets[exercise]
            for li in lines:
                match = re.search(f"([0-9]+){self.sep}([0-9]+){self.sep}([0-9]+)", li)
                if match:
                    sets.append(ExerciseSet(*match.groups()))
            self._sets[exercise] = sets

    def __str__(self):
        return self._date.strftime("%D-%M-%Y")

    def to_dataframe(self):
        df = pd.DataFrame(columns=self.COLUMNS)
        for ex in self._exercises:
            for ex_set in self._sets[ex]:
                df = pd.concat((df, GymSessionParser._create_row(self._date,
                                                                 self._plan,
                                                                 ex,
                                                                 ex_set)),
                               ignore_index=True)

        return df

    @staticmethod
    def _create_row(date: datetime, plan, name, exercise: ExerciseSet):
        tmp = dict((k, v) for k, v in zip(GymSessionParser.COLUMNS,
                                          (date.strftime("%Y-%m-%d"),
                                           plan,
                                           name,
                                           exercise.weight,
                                           exercise.reps)
                                          ))
        return pd.DataFrame.from_records(tmp, index=[0])

    @staticmethod
    def exercise_match(line):
        return re.search(GymSessionParser.EXERCISE_PAT, line)

    @staticmethod
    def date_match(line):
        return re.search(GymSessionParser.DATE_PAT, line)


class InputCleaner:
    @staticmethod
    def lines_from_file(file_name):
        with open(Path(file_name), "r") as f:
            lines = [li.strip("\n") for li in f.readlines()]
            lines = [InputCleaner._drop_non_asci_characters(li) for li in lines]
            lines = InputCleaner._clean_lines(lines)

        return lines

    @staticmethod
    def _drop_non_asci_characters(line: str) -> str:
        new_string = []
        for char in line:
            try:
                new_string.append(char.encode("ASCII"))
            except UnicodeEncodeError:
                pass

        return "".join([char.decode("ASCII") for char in new_string])

    @staticmethod
    def _clean_lines(lines):
        return [li.replace('"', '').replace("·", "-").replace("  ", " ").replace("  ", " ") for li in lines]


def parse_input_csv(file_name) -> pd.DataFrame:
    first_date_reached = False
    buffer = []
    sessions = []
    lines = InputCleaner.lines_from_file(file_name)
    for li in lines:
        if not li:
            continue
        if re.search(GymSessionParser.DATE_PAT, li):
            if first_date_reached:
                sessions.append(GymSessionParser(buffer))
                buffer = []
            else:
                first_date_reached = True
        buffer.append(li)

    [s.parse_session() for s in sessions]
    dataframes = [s.to_dataframe() for s in sessions]

    data = pd.concat(dataframes, axis=0, ignore_index=True)
    return data
