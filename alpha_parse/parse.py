import re
from pathlib import Path

import pandas as pd
from session import GymSessionParser


def parse_input_csv(file_name) -> pd.DataFrame:
    first_date_reached = False
    with open(Path(file_name), "r") as f:
        lines = [l.strip("\n") for l in f.readlines()]
        buffer = []
        sessions = []
        for l in lines:
            if not l:
                continue
            if re.search("[0-9]{4}-[0-9]{2}-[0-9]{2}", l):
                if first_date_reached:
                    sessions.append(GymSessionParser(buffer))
                    buffer = []
                else:
                    first_date_reached = True
            buffer.append(l)

    [s.parse_session() for s in sessions]
    dataframes = [s.to_dataframe() for s in sessions]

    data = pd.concat(dataframes, axis=0, ignore_index=True)
    return data