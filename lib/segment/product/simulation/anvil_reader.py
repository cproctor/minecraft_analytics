from anvil import Region, Chunk
from pathlib import Path
from itertools import product
from tqdm import tqdm
import json

class NullRegion:
    pass

class NullChunk:
    def get_block(self, x, y, z):
        return NullBlock()

class NullBlock:
    namespace = "meta"
    id = ''

class AnvilReader:
    """Reads out a region described by the bounding box, and returns an array of integers
    indexing materials. 
    """

    REGION_LENGTH = 512
    CHUNK_LENGTH = 16
    VOID = 'meta:void'

    def __init__(self, source_path):
        self.source_path = Path(source_path)
        self.regions = {}
        self.chunks = {}

    def read(self, bounding_box):
        ((self.x0, self.x1), (self.y0, self.y1), (self.z0, self.z1)) = bounding_box
        indices = []
        palette = {self.VOID: 0}
        coord_iterator = product(
            range(self.y0, self.y1), 
            range(self.z0, self.z1), 
            range(self.x0, self.x1)
        )
        total = (self.y1 - self.y0) * (self.z1 - self.z0) * (self.x1 - self.x0)
        for y, z, x in tqdm(coord_iterator, total=total, desc="Reading voxel data"):
            material = self.get_voxel_material(x, y, z)
            if material not in palette:
                palette[material] = len(palette)
            indices.append(palette[material])
        palette_list = [m for i, m in sorted([(i, m) for m, i in palette.items()])]
        return indices, palette_list

    def get_voxel_material(self, x, y, z):
        chunk = self.get_chunk(x, y, z)
        block = chunk.get_block(x % 16, y, z % 16)
        return f"{block.namespace}:{block.id}"

    def get_chunk(self, x, y, z):
        "Get the right region, then the right chunk."
        rx, rz = self.get_region_coordinates(x, y, z)
        cx, cz = self.get_chunk_coordinates(x, y, z)
        index = (rx, rz, cx, cz)
        if index not in self.chunks:
            region = self.get_region(x, y, z)
            self.chunks[index] = self.create_chunk(region, cx, cz)
        return self.chunks[index]

    def create_chunk(self, region, cx, cz):
        if isinstance(region, NullRegion):
            return NullChunk()
        else:
            return Chunk.from_region(region, cx, cz)

    def get_region(self, x, y, z):
        "Cached region or load from file if available"
        region_x, region_z = self.get_region_coordinates(x, y, z)
        index = (region_x, region_z)
        if index not in self.regions:
            try:
                region = Region.from_file(str(self.source_path / f"r.{region_x}.{region_z}.mca"))
            except FileNotFoundError:
                region = NullRegion()
            self.regions[index] = region
        return self.regions[index]

    def get_region_coordinates(self, x, y, z):
        """Converts global coordinates to the x- and z- indexed region.
        """
        return x // self.REGION_LENGTH, z // self.REGION_LENGTH

    def get_chunk_coordinates(self, x, y, z):
        """Converts global coordinates to the x- and z-indexed chunk within its region. 
        First we mod by the size of a region, to get coordinates within the region. 
        Then we int divide that to get the index of the chunk
        """
        rx, rz = x % self.REGION_LENGTH, z % self.REGION_LENGTH
        return rx // self.CHUNK_LENGTH, rz // self.CHUNK_LENGTH

def usage_demo():
    mc_path = "/Users/chrisp/Repos/MinecraftUtopia/minecraft-analytics/data/server/production-original/region"
    reader = AnvilReader(mc_path, debug=True)
    blocks, palette = reader.read(((1330, 1340), (60, 70), (1100, 1110)))
    print(blocks)
    print(palette)
