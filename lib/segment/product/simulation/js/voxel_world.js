'use strict';

// I think I have a circular problem. 
// OpLimits shouldn't create chunks, because we need to know
// the oplimits before creating chunks.
// instead, oplimits should be indexed by cLocs.

import VoxelChunk from "./voxel_chunk.js";

export default class VoxelWorld {

  constructor(voxels, palette, bb0, bb1, ops) {
    this.bb0 = bb0;
    this.bb1 = bb1;
    this.size = bb1.clone().sub(bb0);
    this.palette = palette;
    this.opLimits = this.getOpLimits(ops);
    this.chunks = new Map();
    this.initializeVoxels(voxels);
  }

  // Voxels and palette are expected to the be same specification as the
  // output of AnvilReader.read()
  initializeVoxels(voxels) {
    for (let y = 0; y < voxels.length; y++) {
      const [method, plane] = voxels[y];
      if (method == "dense") {
        for (let z = 0; z < this.size.z; z++) {
          for (let x = 0; x < this.size.x; x++) {
            const index = z * this.size.x + x;
            this.setVoxel(
              this.bb0.x + x, 
              this.bb0.y + y, 
              this.bb0.z + z, 
              this.palette[plane[index]]
            );
          }
        }
      }
      else if (method == "sparse") {
        for (const [z, x, m] of plane) {
          this.setVoxel(
            this.bb0.x + x, 
            this.bb0.y + y, 
            this.bb0.z + z, 
            this.palette[m]
          );
        }
      }
      else {
        throw new Error(`Unrecognized method ${method}`);
      }
    }
  }

  createObjects() {
    for (const [cKey, chunk] of this.chunks) {
      chunk.createObjects();
    }
  }

  getObjects() {
    const objects = [];
    for (const [cKey, chunk] of this.chunks) {
      for (const object of chunk.getObjects()) {
        objects.push(object);
      }
    }
    return objects;
  }

  updateGeometries(ops) {
    for (const [cKey, chunkOps] of this.groupOpsByChunkLocation(ops)) {
      const chunk = this.chunks.get(cKey);
      chunk.updateGeometries(chunkOps);
    }
  }

  setVoxel(x, y, z, material) {
    const chunk = this.getOrCreateChunk(x, y, z);
    chunk.setVoxel(x, y, z, material);
  }

  getVoxel(x, y, z) {
    const chunk = this.getChunk(x, y, z);
    if (chunk) {
      return chunk.getVoxel(x, y, z);
    }
    else {
      return "meta:void";
    }
  }

  getOrCreateChunk(x, y, z) {
    const chunk = this.getChunk(x, y, z);
    if (chunk) {
      return chunk;
    }
    else {
      return this.createChunk(x, y, z);
    }
  }

  getChunk(x, y, z) {
    const [cx, cy, cz] = this.getChunkLocation(x, y, z);
    const cKey = this.getChunkKey(cx, cy, cz);
    return this.chunks.get(cKey);
  }

  createChunk(x, y, z) {
    const [cx, cy, cz] = this.getChunkLocation(x, y, z);
    const cKey = this.getChunkKey(cx, cy, cz);
    const opLimit = this.opLimits.get(cKey) || 0;
    const chunk = new VoxelChunk(cx, cy, cz, opLimit, this);
    this.chunks.set(cKey, chunk);
    return chunk;
  }

  getChunkLocation(x, y, z) {
    const cx = Math.floor(x / VoxelChunk.size.x);
    const cy = Math.floor(y / VoxelChunk.size.y);
    const cz = Math.floor(z / VoxelChunk.size.z);
    return [cx, cy, cz];
  }

  getChunkKey(cx, cy, cz) {
    return `${cx},${cy},${cz}`;
  }

  getOpLimits(ops) {
    const opLimits = new Map();
    const opsByChunkLoc = this.groupOpsByChunkLocation(ops);
    for (const [cKey, chunkOps] of opsByChunkLoc) {
      opLimits.set(cKey, chunkOps.length);
    }
    return opLimits;
  }

  groupOpsByChunkLocation(ops) {
    const opsByChunkLoc = new Map();
    for (const op of ops) {
      const [x, y, z] = op[1];
      const [cx, cy, cz] = this.getChunkLocation(x, y, z);
      const cKey = this.getChunkKey(cx, cy, cz);
      const opArray = opsByChunkLoc.get(cKey);
      if (opArray) {
        opArray.push(op)
      }
      else {
        opsByChunkLoc.set(cKey, [op]);
      }
    }
    return opsByChunkLoc;
  }
}
