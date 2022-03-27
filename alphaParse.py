"""
Parsing Alpha Progression Workout Output
"""

import argparse
from collections import defaultdict, namedtuple
import logging
from pathlib import Path
from datetime import datetime
import re

import pandas as pd

ExerciseSet = namedtuple("ExerciseSet", ["n", "weight", "reps"])


class GymSession:
    PLAN_PAT = "^Day [0-9]+ · Week [0-9]* · (.*)"
    DATE_PAT = "([0-9]{4}-[0-9]{2}-[0-9]{2})"
    EXERCISE_PAT = "[0-9]+\. (.+)"
    DATE_FORMAT = "%Y-%m-%d"
    COLUMNS = ("date", "plan", "exercise", "weight", "reps")

    def __init__(self, lines: list):
        self.lines = lines

        self._plan = None
        self._date: datetime = None
        self._exercises = []
        self._sets = defaultdict(list)  # reps[exercise] = [(weight, reps)]

    def parse_session(self):
        self._find_date_plan()
        self._find_exercises()

    def _find_date_plan(self):
        for l in self.lines:
            match = re.search(self.DATE_PAT, l)
            if match:
                self._date = datetime.strptime(match.group(1), self.DATE_FORMAT)
                logging.debug(f"GymSession on {self._date}")
            match = re.match(self.PLAN_PAT, l)
            if match:
                self._plan = match.group(1)
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
            for l in lines:
                match = re.search("([0-9]+);([0-9]+);([0-9]+)", l)
                if match:
                    sets.append(ExerciseSet(*match.groups()))
            self._sets[exercise] = sets

    def __str__(self):
        return self._date.strftime("%D-%M-%Y")

    def to_dataframe(self):
        df = pd.DataFrame(columns=self.COLUMNS)
        for ex in self._exercises:
            for ex_set in self._sets[ex]:
                df = df.append(GymSession._create_row(self._date,
                                                      self._plan,
                                                      ex,
                                                      ex_set),
                               ignore_index=True)

        return df

    @staticmethod
    def _create_row(date: datetime, plan, name, exercise: ExerciseSet):
        tmp = dict((k, v) for k, v in zip(GymSession.COLUMNS,
                                          (date.strftime("%Y-%m-%d"),
                                           plan,
                                           name,
                                           exercise.weight,
                                           exercise.reps)
                                          ))
        return pd.DataFrame.from_records(tmp, index=[0])

    @staticmethod
    def exercise_match(line):
        return re.search(GymSession.EXERCISE_PAT, line)

    @staticmethod
    def date_match(line):
        return re.search(GymSession.DATE_PAT, line)


def parse_exported_csv(file_name) -> pd.DataFrame:
    first_date_reached = False
    with open(Path(file_name), "r") as f:
        lines = [l.strip("\n").replace('"', '').replace("·", "-") for
                 l in f.readlines()]
        buffer = []
        sessions = []
        for l in lines:
            if not l:
                continue
            if re.search("[0-9]{4}-[0-9]{2}-[0-9]{2}", l):
                if first_date_reached:
                    sessions.append(GymSession(buffer))
                    buffer = []
                else:
                    first_date_reached = True
            buffer.append(l)

    [s.parse_session() for s in sessions]
    dataframes = [s.to_dataframe() for s in sessions]

    data = pd.concat(dataframes, axis=0, ignore_index=True)
    return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", "-i", type=Path, required=True,
                        help="Input file")
    parser.add_argument("--output", "-o", type=Path,
                        help="Output file")

    logging.basicConfig()

    args = parser.parse_args()

    df_csv = parse_exported_csv(args.input)

    df_csv.to_csv(args.output, index=False)
