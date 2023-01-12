from pathlib import Path
import pandas as pd

DEBUG = True
DEBUG_NROWS = 10000

class OpReader:
    """Reads a Minecraft server log and yields ops.
    """
    def __init__(self, logfile):
        self.events = pd.read_csv(
            Path(server_log_file), 
            index_col="timestamp", 
            parse_dates=["timestamp"], 
            low_memory=False,
            nrows = DEBUG_NROWS if DEBUG else None,
        )
