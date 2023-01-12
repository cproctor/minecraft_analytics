from voxel_geometry import VoxelGeometry
from datetime import datetime

server_log_file = "data/df/production.csv"
ts = datetime.fromisoformat("2021-07-17 18:48:02")
outfile = "study_data.json"

vg = VoxelGeometry()
vg.export(server_log_file, ts, outfile)
