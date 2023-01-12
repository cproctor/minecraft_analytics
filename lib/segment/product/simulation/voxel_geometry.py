# This module solves a problem we no longer have. 
# Nevertheless, much of its code is used elsewhere.
# Originally, we did not have access to the .mca files
# for initial world state, so I was trying to infer the state
# from logs.
#

# Note: Currently, we do not log the texture of the target block. 
# Textures sometimes have important semantic meaning (especially flags
# and banners), but capturing the texture adds an additional layer of 
# complexity, as BlockPlaceEvents don't come with coordinates.

# NEXT UP: Refactor--I want to drop in the json data on my own.

from pathlib import Path
import pandas as pd
import numpy as np
from tqdm import tqdm
import json
from segment.product.simulation.vectors import *

DEBUG = True
DEBUG_NROWS = 100000

GENERIC_BLOCK = 'generic'

class VoxelGeometry:

    def __init__(self, debug=False):
        self.debug = debug

    def export(self, server_log_file, time, outfile):
        """Generates a js file of the voxel geometry computed from the logfile.
        This file defines a contstant 'study_data'
        """
        data = self.get_data_for_json(server_log_file, time)
        with open(outfile, 'w') as fh:
            json.dump(data, fh)

    def get_data_for_json(self, server_log_file, time):
        """Generates data ready for jsonification.
        """
        voxels = self.get_initial_voxels(server_log_file, time)
        voxel_ids = {vox: i for i, vox in enumerate(voxels.keys())}
        voxel_coords = {i: vox for vox, i in voxel_ids.items()}
        voxel_materials = {i: voxels[vox] for vox, i in voxel_ids.items()}
        faces = self.get_exposed_faces(voxels)
        voxel_faces = {voxel_ids[vox]: voxel_faces for vox, voxel_faces in faces.items()}

        # TEMP
        vc = np.array([vc for vc in voxel_coords.values()])
        print('MIN ', vc.min(axis=0))
        print('MEAN', vc.mean(axis=0))
        print('MAX ', vc.max(axis=0))

        return {
            "voxels": voxel_coords,
            #"materials": voxel_materials,
            "faces": voxel_faces,
            "params": {
                "center": tuple(vc.mean(axis=0))
            }
        }

    def get_initial_voxels(self, server_log_file, time):
        """Builds voxel geometry of a Minecraft world using a server log file.
        `server_log_file` should be a path to a csv of server log events.
        `time` should be a datetime.datetime indicating the moment at which
        to calculate the world.
        """
        # Invoke can find server_log as: Path(c.local.dataframe_path) / df_fn
        # See tasks/__init__.py:61
        relevant_event_types = [
            'PlayerMoveEvent',
            'BlockPlaceEvent',
            'BlockBreakEvent',
        ]
        events = pd.read_csv(
            Path(server_log_file), 
            index_col="timestamp", 
            parse_dates=["timestamp"], 
            low_memory=False,
            nrows = DEBUG_NROWS if DEBUG else None,
        )
        events = events[events.event.isin(relevant_event_types)]
        events = events[~events.target_block_x.isnull()]
        events['target_block_x'] = events['target_block_x'].astype(int)
        events['target_block_y'] = events['target_block_y'].astype(int)
        events['target_block_z'] = events['target_block_z'].astype(int)
        past = events.loc[events.index <= time]
        future = events.loc[events.index > time]
        player_targets = {}
        voxels = {}
        past_iterator = tqdm(past.iterrows()) if self.debug else past.iterrows()
        for ts, event in past_iterator:
            if event.event == 'PlayerMoveEvent':
                coords = self.get_coords(event)
                player_targets[event.player] = coords
                if coords not in voxels: 
                    voxels[coords] = GENERIC_BLOCK
            elif event.event == 'BlockPlaceEvent':
                if event.player in player_targets:
                    coords = player_targets[event.player]
                    voxels[coords] = event.block
            elif event.event == 'BlockBreakEvent':
                if event.player in player_targets:
                    coords = player_targets[event.player]
                    if coords in voxels:
                        del voxels[coords]
        future_voxels = voxels.copy()
        future_iterator = tqdm(future.iterrows()) if self.debug else future.iterrows()
        for ts, event in future_iterator:
            if event.event == 'PlayerMoveEvent':
                coords = self.get_coords(event)
                player_targets[event.player] = coords
                if coords not in future_voxels: 
                    voxels[coords] = GENERIC_BLOCK
                    future_voxels[coords] = GENERIC_BLOCK
            elif event.event == 'BlockPlaceEvent':
                if event.player in player_targets:
                    coords = player_targets[event.player]
                    future_voxels[coords] = event.block
            elif event.event == 'BlockBreakEvent':
                if event.player in player_targets:
                    coords = player_targets[event.player]
                    if coords in future_voxels:
                        pass
                    elif coords not in voxels:
                        voxels[coords] = GENERIC_BLOCK
        return voxels

    def get_exposed_faces(self, voxels):
        """Given a collection of voxels, generates exposed faces.
        Voxels is a dict like {(x, y, z): "material"}.
        Returns a dict mapping faces to voxels like {(x, y, z): [(c0, c1, c2, c3)]}, 
        where cx is a point (x, y, z). This allows us to identify all the faces belonging 
        to a voxel.
        """
        vs = set(voxels.keys())
        faces = {}
        voxel_iterator = tqdm(voxels.keys()) if self.debug else voxels.keys()
        for voxel in voxel_iterator:
            voxel_faces = []
            for vector, face in zip(VECTORS, FACES):
                if translate(voxel, vector) not in vs:
                    voxel_faces.append(get_face(voxel, vector, face))
            faces[voxel] = tuple(voxel_faces)
        return faces

    def get_coords(self, event):
        return (event.target_block_x, event.target_block_y, event.target_block_z)

    def get_mean_faces(self, faces):
        """Returns the average number of faces per voxel.
        """
        voxel_faces = [len(vf) for vf in faces.values()]
        return sum(voxel_faces) / len(voxel_faces)
