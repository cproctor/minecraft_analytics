from pathlib import Path
import json
import re
from datetime import datetime
import pandas as pd
import code

class LogReader:
    """
    Parses one or more log files and streams dicts. 
    Expected log format is [isoTimestamp][eventType] data, 
    where data is in JSON format without surrounding curly braces. 
    For example:

        [2021-06-26T13:37:26.0801][PlayerMoveEvent]: "player": "thispettypace", "location": [33, 71, 99], "eye_location": [33, 71, 98], "eye_direction": [45.60006, 129.45012], "target_block": [32, 71, 98]
    """
    log_line_pattern = "^\[(?P<timestamp>.+?)\]\[(?P<event>.+?)\](\[Cancelled\])?: (?P<data>.*)$"
    command_pattern = '"command":\s*(".*")'
    log_timestamp_format = "%Y-%m-%dT%H:%M:%S.%f"
    streams = None

    def __init__(self, logs_path, log_suffix=".log"):
        """Logspath should be a single file or a directory. If `logs_path` is a
        directory, all files ending in `log_suffix` will be parsed. 
        """
        logs_path = Path(logs_path)
        if not logs_path.exists():
            raise ValueError("logs_path {} does not exist".format(logs_path))
        if logs_path.is_dir():
            self.log_files = list(logs_path.glob("**/*" + log_suffix))
        else:
            self.log_files = logs_path
        if len(self.log_files) == 0:
            raise ValueError("No matching log files found")

    def to_df(self):
        """Returns a dataframe from all log files.
        Currently, this is done in memory and ignores the fact that each log
        file is sorted (we could merge logs in O(n) instead of O(nlog(n)) but 
        we'd lose built-in sort optimizations). The dataframe can be cached as
        CSV so this doesn't need to happen every run.
        """
        logs = []
        for f in self.log_files:
            with open(f) as fh:
                for linenum, line in enumerate(fh):
                    logs.append(self.parse_line(line, linenum+1, f))
        df = pd.DataFrame.from_records(logs, index="timestamp")
        list_cols = [
            ["location", ["location_x", "location_y", "location_z"]],
            ["eye_location", ["eye_location_x", "eye_location_y", "eye_location_z"]],
            ["eye_direction",["eye_direction_pitch", "eye_direction_yaw"]],
            ["target_block", ["target_block_x", "target_block_y", "target_block_z"]],
        ]
        for oldcol, newcols in list_cols:
            if oldcol in df.columns:
                values = [(v if isinstance(v, list) else [None] * len(newcols)) for v in df[oldcol].tolist()]
                df[newcols] = pd.DataFrame(values, columns=newcols, index=df.index)
                df = df.drop(columns=oldcol)
        return df

    def parse_line(self, line, linenum, path):
        """Tries to parse a line.
        Raises LogReader.ParseError if there's trouble.
        """
        match = re.match(self.log_line_pattern, line)
        loc = "{}:{}".format(path, linenum)
        if not match:
            raise self.ParseError("Error reading {}: {}".format(loc, line))
        try:
            json_string = '{' + match.group('data') + '}'
            json_string = json_string.replace('Unknown', 'null')
            data = json.loads(json_string)
        except json.decoder.JSONDecodeError as e:
            # Maybe there was unescaped content in the command field?
            command_match = re.search(self.command_pattern, json_string)
            if command_match:
                command_value = command_match.group(1)
                json_string = json_string.replace(command_value, json.dumps(command_value))
                data = json.loads(json_string)
            else:
                raise self.ParseError("Error decoding data at {}. JSON error: {}. Line:\n{}".format(loc, e, line))
        try:
            ts = datetime.strptime(match.group('timestamp'), self.log_timestamp_format)
        except ValueError:
            raise self.ParseError("Could not parse timestamp at {}: {}".format(
                    loc, match.group('timestamp')))
        data["timestamp"] = ts
        data["event"] = match.group('event')
        return data

    class ParseError(Exception):
        "Custom error class for problems reading logs"

