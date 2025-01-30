# What needs to be done now?
# - Get the anvil data.
#   - Base64 encode it. 
#   - Drop it into the template.

from subprocess import run, DEVNULL
from collections.abc import Iterator
from segment.product.logs import SegmentLogs
from jinja2 import FileSystemLoader, Environment
import shutil
from pathlib import Path
import json
from hashlib import md5
from base64 import b64encode
from collections import defaultdict
from itertools import combinations
from datetime import timedelta
from segment.product.simulation.mc_world import MinecraftWorldView
from segment.product.joint_attention import SegmentJointAttention

def tuples(iterator):
    """Yields pairs of items.
    """
    if not isinstance(iterator, Iterator):
        iterator = iter(iterator)
    item0 = next(iterator)
    for item1 in iterator:
        yield item0, item1
        item0 = item1

class SegmentSimulation(SegmentLogs):
    """A three.js simulation.
    - Use the full log to compute the world's initial state.
    """
    expected_params = [
        "format",
        "export_filename",
        "bounding_box",
        "layers",
    ]

    optional_params = [
        "title",
        "use_cache",
        "lookback",
        "distance_threshold",
        "window_seconds",
    ]

    here = Path(__file__).parent
    bundle_path = here / 'js' / 'bundle.js'
    template_dir = here / 'html'
    template = 'template.html'
    initial_production_mca_path = "data/server/production-original/region"
    world_height = 256

    def export(self):
        if not (self.params.get("use_cache", True) and self.get_cached_study_data_path().exists()):
            self.generate_study_data_json()
        run('npm run build', cwd=self.here / 'js', shell=True)
        env = Environment(loader=FileSystemLoader(self.template_dir))
        template = env.get_template(self.template)
        simulation_js = self.bundle_path.read_text()
        study_json = self.get_cached_study_data_path().read_text()

        with open(self.export_filename(), 'w') as fh:
            with open(self.bundle_path) as js_fh:
                fh.write(template.render({
                    'simulation_js': simulation_js,
                    'study_json': study_json,
                    'title': self.params.get('title', '')
                }))

    def generate_study_data_json(self):
        world = MinecraftWorldView(
            self.initial_production_mca_path,
            self.main_log_file,
            self.params['bounding_box'],
            self.segment_params['start'],
            self.segment_params['duration'],
        )
        start = self.segment_params['start']
        end = start + timedelta(seconds=self.segment_params['duration'])
        data = {}
        data['params'] = {
            'bounding_box': self.params['bounding_box'],
            'timespan': [str(start), str(end)]
        }
        data['layers'] = {}
        data['layers']['terrain'] = self.get_terrain_layer(world)
        p_param = self.params['layers'].get('players')
        if p_param == 'all':
            p_df = self.filter_players_df(world.ops_df)
            p_layer = self.get_players_layer(p_df, all_players=True)
        elif isinstance(self.params['layers']['players'], list):
            p_df = self.filter_players_df(world.ops_df)
            p_layer = self.get_players_layer(p_df, players=p_param)
        else:
            raise ValueError(f"Invalid players layer arg: {p_param}")
        data['layers']['players'] = p_layer
        if self.params['layers'].get('jva'):
            player_list = p_layer['initial'].keys()
            data['layers']['jva'] = self.get_jva_layer(player_list)
        with open(self.get_cached_study_data_path(), 'w') as fh:
            json.dump(data, fh)

    def get_jva_layer(self, players):
        jva_params = {k:v for k, v in self.params.items() if k in 
                SegmentJointAttention.optional_params}
        jva_params['format'] = "joint_attention"
        jva_params['export_filename'] = '_'
        jva_params['players'] = {p:p for p in players}
        jva_params['measure'] = "joint_attention_schneider_pea_2013"
        jva_product = SegmentJointAttention(self.segment_params, jva_params)
        df = jva_product.get_joint_attention_schneider_pea_2013_df()
        player_pairs = list(combinations(sorted(players), 2))
        initial = {f"{p0}-{p1}": self.row_to_jva_state(df.iloc[0], p0, p1) for p0, p1 in player_pairs}
        ops = {f"{p0}-{p1}": self.player_pair_ops(df, p0, p1) for p0, p1 in player_pairs}
        return {"type": "jva", "initial": initial, "ops": ops}

    def player_pair_ops(self, df, p0, p1):
        ops = []
        for (ts0, row0), (ts1, row1) in tuples(df.iterrows()):
            if row0[f"{p0}-{p1}"] or row1[f"{p0}-{p1}"]:
                s0 = self.row_to_jva_state(row0, p0, p1)
                s1 = self.row_to_jva_state(row1, p0, p1)
                if not (s0[1] == s1[1] and s0[2] == s1[2] and s0[3] == s1[3]):
                    ops.append([str(ts1), s0, s1])
        return ops

    def row_to_jva_state(self, row, player0, player1):
        """Given a df produced by SegmentJointAttention, returns a 4-tuple
        (jva_bool, x, y, z), indicating the shared gaze point of the players
        if they have JVA.
        .Zora299629_target_block_x'
        """
        jva_bool = bool(row[f"{player0}-{player1}"])
        if jva_bool:
            jva_x = (row[f"{player0}_target_block_x"] + row[f"{player1}_target_block_x"]) / 2
            jva_y = (row[f"{player0}_target_block_y"] + row[f"{player1}_target_block_y"]) / 2
            jva_z = (row[f"{player0}_target_block_z"] + row[f"{player1}_target_block_z"]) / 2
        else:
            jva_x = 0
            jva_y = 0
            jva_z = 0
        return (jva_bool, jva_x, jva_y, jva_z)
        
    def filter_players_df(self, df):
        start = self.segment_params['start']
        end = start + timedelta(seconds=self.segment_params['duration'])
        df = df[df.event == 'PlayerMoveEvent']
        df['location_x'] = df.location_x.astype(int)
        df['location_y'] = df.location_y.astype(int)
        df['location_z'] = df.location_z.astype(int)
        ((x0, x1), (y0, y1), (z0, z1)) = self.params['bounding_box']
        df = df[(x0 <= df.location_x) & (df.location_x < x1)]
        df = df[(y0 <= df.location_y) & (df.location_y < y1)]
        df = df[(z0 <= df.location_z) & (df.location_z < z1)]
        df = df[start <= df.index]
        df = df[df.index < end]
        return df.sort_index()

    def get_terrain_layer(self, world):
        voxels, palette = world.get_base_layer_at_start()
        return {
            "type": "terrain",
            "initial": [voxels, palette],
            "ops": world.get_base_layer_opset(),
        }

    def get_players_layer(self, df, players=None, all_players=False):
        if not (players or all_players):
            raise ValueError("player names or all_players must be specified")
        if players and all_players:
            raise ValueError("Player names and all_players cannot both be specified")
        if players:
            df = df[df.player.isin(players)]
        initial = {}
        grouper = df.groupby('player')
        for name, row in grouper.first().iterrows():
            initial[name] = self.row_to_player_state(row)
        ops = {}
        for name, index in df.groupby('player').groups.items():
            ops[name] = self.get_player_ops(df.loc[index])
        return {
            "type": "players",
            "initial": initial,
            "ops": ops
        }

    # TODO: This is wildly inefficient. I don't want no-op ops.
    # Could be easily simplified by filtering out ops where before and after are identical.
    def get_player_ops(self, df):
        ops = []
        for (ts0, row0), (ts1, row1) in tuples(df.iterrows()):
            ops.append([
                str(ts1), 
                self.row_to_player_state(row0), 
                self.row_to_player_state(row1)
            ])
        return ops

    def row_to_player_state(self, row):
        return {
            "position": [row.location_x, row.location_y, row.location_z],
            "eyeDirection": [row.eye_direction_pitch, row.eye_direction_yaw],
            "eyeTarget": [row.target_block_x, row.target_block_y, row.target_block_z]
        }

    def get_cached_study_data_path(self):
        ((x0, x1), (y0, y1), (z0, z1)) = self.params['bounding_box']
        start, end = self.get_start_end_times()
        params = {
            'p': self.params, 
            'start': str(self.segment_params['start']), 
            'duration': self.segment_params['duration']
        }
        cache_hash = md5(json.dumps(params, sort_keys=True).encode('utf-8')).hexdigest()
        return Path("data/cache") / f"simulation-{cache_hash}.json"

    def get_bounding_box_center(self):
        return [i0 + (i1 - i0) / 2 for i0, i1 in self.params['bounding_box']]

