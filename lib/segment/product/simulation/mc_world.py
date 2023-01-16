# What does an op look like?
# Just a list: [layer, location, before, after]
# Example: [0, [x, y, z], <value>, <value>]

from pathlib import Path
import pandas as pd
from collections import defaultdict
from segment.product.simulation.anvil_reader import AnvilReader
from datetime import timedelta
from tqdm import tqdm

DEBUG = False
DEBUG_NROWS = 1000000

class MinecraftWorldView:
    """Models part of Minecraft world, bounded by a 3D bounding box and a timespan.
    Data sources include a directory of MCA files and a log file documenting changes
    to the world.
    """

    base_layer = 0
    air = "minecraft:air"
    time_granularity = "1s"

    def __init__(self, mca_path, logfile, bounding_box, start, duration):
        self.mca_path = mca_path
        self.logfile = logfile
        self.bounding_box = bounding_box
        self.start = start
        self.duration = duration
        self.end = self.start + timedelta(seconds=self.duration)
        self.ops_df = self.get_ops_df()

    def get_initial_base_layer(self):
        reader = AnvilReader(self.mca_path)
        blocks, palette = reader.read(self.bounding_box)
        return blocks, palette

    def get_base_layer_at_start(self):
        """Returns blocks and palette at the start of the segment.
        Also iterates through the ops we will encounter during the segment
        to ensure a consistent order in the palette.
        """
        blocks, palette = self.get_initial_base_layer()
        for ts, row in self.get_base_layer_ops_df("before").iterrows():
            op = self.base_layer_series_to_op(ts, row)
            self.update_base_layer(blocks, palette, op)
        for ts, row in self.get_base_layer_ops_df("during").iterrows():
            op = self.base_layer_series_to_op(ts, row)
            ts, location, before, after = op
            if after not in palette:
                palette.append(after)
        return blocks, palette

    def update_base_layer(self, blocks, palette, op):
        layer, location, before, after = op
        if after not in palette:
            palette.append(after)
        offset = self.get_base_layer_offset(*location)
        blocks[offset] = palette.index(after)

    def get_base_layer_offset(self, x, y, z):
        """Returns the list index for voxel (x, y, z) in 
        The base layer is represented as a list of integers, ordered by y/z/x.
        """
        ((x0, x1), (y0, y1), (z0, z1)) = self.bounding_box
        return (y-y0)*(x1-x0)*(z1-z0) + (z-z0)*(x1-x0) + (x-x0)

    def base_layer_series_to_op(self, ts, series):
        """Converts a df series (row) to an op, a list like (layer, location, before, after).
        """
        location = (series.location_x, series.location_y, series.location_z)
        if series.event == 'BlockBreakEvent':
            return (str(ts), location, series.block, self.air)
        elif series.event == 'BlockPlaceEvent':
            return (str(ts), location, self.air, series.block)

    def get_base_layer_opset(self):
        df = self.get_base_layer_ops_df("during")
        return [self.base_layer_series_to_op(ts, row) for ts, row in df.iterrows()]

    def get_base_layer_ops_df(self, when=None):
        """Given an ops df, filters out relevant the base layer ops.
        """
        ops = self.ops_df
        ops = ops[ops.event.isin(['BlockBreakEvent', 'BlockPlaceEvent'])]
        ops['location_x'] = ops.location_x.astype(int)
        ops['location_y'] = ops.location_y.astype(int)
        ops['location_z'] = ops.location_z.astype(int)
        ((x0, x1), (y0, y1), (z0, z1)) = self.bounding_box
        ops = ops[(x0 <= ops.location_x) & (ops.location_x < x1)]
        ops = ops[(y0 <= ops.location_y) & (ops.location_y < y1)]
        ops = ops[(z0 <= ops.location_z) & (ops.location_z < z1)]

        if when == "before":
            ops = ops[ops.index < self.start]
        elif when == "during":
            ops = ops[self.start <= ops.index]
            ops = ops[ops.index < self.end]
        return ops

    def get_ops_df(self):
        relevant_event_types = [
            'PlayerMoveEvent',
            'BlockPlaceEvent',
            'BlockBreakEvent',
        ]
        ops = pd.read_csv(
            Path(self.logfile), 
            index_col="timestamp", 
            parse_dates=["timestamp"], 
            low_memory=False,
            nrows = DEBUG_NROWS if DEBUG else None,
        )
        ops = ops[ops.event.isin(relevant_event_types)]
        return ops
