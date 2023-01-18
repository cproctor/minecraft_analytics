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
    namespace = "minecraft"
    id = 'air'

class AnvilReader:
    """Reads out a region described by the bounding box, and returns a representation of
    the region's materials. The format is as follows: 

        - An array of ascending y-indexed planes is returned, along with the palette.
          y-values are inferred by the y-index of the plane.
        - Each plane is a list: [method, data]
        - When method is 'sparse', data is a list of (z, x, m) values.
        - When method is 'dense', data is an ascending (z, x) indexed m values. 
        - x, y, and z-values are relative to the bounding box.
        - m values represent the index of a material in palette.
        - minecraft:cave_air is mapped to minecraft:air (palette index 0) to make its
          truthiness consistent.

    The rationale behind this format is that the density (ratio of non-air pixels) varies
    greatly by y. For less-dense planes, a sparse representation is much more efficient. 
    For more-dense planes, a dense representation is much more efficient. The cutoff
    density can be adjusted using MAX_SPARSE_DENSITY.
    """

    REGION_LENGTH = 512
    CHUNK_LENGTH = 16
    MAX_SPARSE_DENSITY = 0.3

    def __init__(self, source_path):
        self.source_path = Path(source_path)
        self.regions = {}
        self.chunks = {}

    def read(self, bounding_box):
        ((x0, x1), (y0, y1), (z0, z1)) = bounding_box
        blocks = []
        palette = {'minecraft:air': 0}
        volume = (y1 - y0) * (z1 - z0) * (x1 - x0)
        with tqdm(total=volume, desc="Reading voxels") as progress_bar:
            for y in range(y0, y1):
                plane = []
                for z in range(z0, z1):
                    for x in range(x0, x1):
                        progress_bar.update(1)
                        material = self.get_voxel_material(x, y, z)
                        if material not in palette:
                            palette[material] = len(palette)
                        plane.append((z - z0, x - x0, palette[material]))
                sparse = [[z, x, m] for z, x, m in plane if m]
                plane_area = (z1 - z0) / (x1 - x0)
                density = len(sparse) / plane_area
                if density <= self.MAX_SPARSE_DENSITY:
                    blocks.append(["sparse", sparse])
                else:
                    blocks.append(["dense", [m for z, x, m in plane]])
        palette_list = [m for i, m in sorted([(i, m) for m, i in palette.items()])]
        return blocks, palette_list

    def get_voxel_material(self, x, y, z):
        chunk = self.get_chunk(x, y, z)
        block = chunk.get_block(x % 16, y, z % 16)
        if block.id == 'cave_air': 
            block.id = 'air'
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

    def is_air(self, material):
        return material == "minecraft:air" or material == "minecraft:cave_air"

def usage_demo():
    mc_path = "/Users/chrisp/Repos/MinecraftUtopia/minecraft-analytics/data/server/production-original/region"
    reader = AnvilReader(mc_path, debug=True)
    blocks, palette = reader.read(((1330, 1340), (60, 70), (1100, 1110)))
    print(blocks)
    print(palette)
