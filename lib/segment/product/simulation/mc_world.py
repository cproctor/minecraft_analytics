# What does an op look like?
# Just a list: [layer, location, before, after]
# Example: [0, [x, y, z], <value>, <value>]

from pathlib import Path
import pandas as pd
from segment.product.simulation.anvil_reader import AnvilReader

DEBUG = True
DEBUG_NROWS = 10000

class MinecraftWorldView:
    """Models part of Minecraft world, bounded by a 3D bounding box and a timespan.
    Data sources include a directory of MCA files and a log file documenting changes
    to the world.
    """

    def __init__(self, mca_path, logfile, bounding_box, start, duration):
        self.mca_path = mca_path
        self.logfile = logfile
        self.bounding_box = bounding_box
        self.start = start
        self.duration = duration
        self.ops_df = self.get_ops_df()

    def get_initial_base_layer(self):
        reader = AnvilReader(self.mca_path)
        blocks, palette = reader.read(self.bounding_box)
        return blocks, palette

    def get_base_layer_at_start(self):
        blocks, palette = self.get_initial_base_layer()
        for op in self.get_base_layer_ops_before_start():
            self.update_base_layer(blocks, palette, op)
        return blocks, palette

    def update_base_layer(self, blocks, palette, op):
        layer, location, before, after = op
        if self.in_bounding_box(*location):
            if after not in palette:
                palette.append(after)
            offset = self.get_base_layer_offset(*location)
            blocks[offset] = palette.index(after)

    def get_base_layer_offset(self, x, y, z):
        """The base layer is represented as a list of integers, ordered by y/z/x.
        """
        ((x0, x1), (y0, y1), (z0, z1)) = self.bounding_box
        return (y-y0)*(x1-x0)*(z1-z0) + (z-z0)*(x1-x0) + (x-x0)

    def get_base_layer_ops_before_start(self):
        """Yields ops for the base layer.
        """
        past_ops = self.ops_df.loc[self.ops_df.index <= self.start]
        base_layer = 0
        air = "minecraft:air"
        for ts, op in past_ops.iterrows():
            if op.event == 'BlockBreakEvent':
                location = (op.target_block_x, op.target_block_y, op.target_block_z)
                yield (base_layer, location, op.block, air)
            elif op.event == 'BlockPlaceEvent':
                location = (op.target_block_x, op.target_block_y, op.target_block_z)
                yield (base_layer, location, air, op.block)

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
        ops = ops[~ops.target_block_x.isnull()]
        ops['target_block_x'] = ops['target_block_x'].astype(int)
        ops['target_block_y'] = ops['target_block_y'].astype(int)
        ops['target_block_z'] = ops['target_block_z'].astype(int)
        return ops
