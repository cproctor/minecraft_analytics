'use strict';

// I think I have a circular problem. 
// OpLimits shouldn't create chunks, because we need to know
// the oplimits before creating chunks.
// instead, oplimits should be indexed by cLocs.

import {
    Vector3
} from "three";
import VoxelChunk from "./voxel_chunk.js";

export default class VoxelWorld {

  // Ops is required in the constructor for two reasons:
  // First, to ensure that all chunks which will be required are initially
  // created (update doesn't expect to add new meshes);
  constructor(voxelData, palette, ops) {
    this.palette = palette;
    this.opLimits = this.getOpLimits(ops);
    this.voxelBuffer = voxelData;
    this.chunks = new Map();
    for (const op of ops) {
      this.getOrCreateChunk(op.loc);
    }
  }

  createMeshes() {
    for (const [cLoc, chunk] of this.chunks) {
      chunk.createMeshes();
    }
  }

  getMeshes() {
    const meshes = [];
    for (const [cLoc, chunk] of this.chunks) {
      for (const mesh in chunk.meshes) {
        meshes.push(mesh);
      }
    }
    return meshes;
  }

  updateGeometries(ops) {
    for (const [cLoc, chunkOps] of this.groupOpsByChunkLocation(ops)) {
      const chunk = this.chunks.get(cLoc);
      chunk.updateGeometries(ops);
    }
  }

  setVoxel(loc, material) {
    const chunk = this.getOrCreateChunk(loc);
    chunk.setVoxel(loc, material);
  }

  getVoxel(loc) {
    const chunk = this.getChunk(loc);
    if (chunk) {
      return chunk.getVoxel(loc);
    }
    else {
      return "meta:void";
    }
  }

  getOrCreateChunk(loc) {
    const chunk = this.getChunk(loc);
    if (chunk) {
      return chunk;
    }
    else {
      return this.createChunk(loc);
    }
  }

  getChunkLocation(loc) {
    const cx = Math.floor(loc.x / VoxelChunk.size.x);
    const cy = Math.floor(loc.y / VoxelChunk.size.y);
    const cz = Math.floor(loc.z / VoxelChunk.size.z);
    return new Vector3(cx, cy, cz);;
  }

  getChunk(loc) {
    const cLoc = this.getChunkLocation(loc);
    return this.chunks.get(cLoc);
  }

  createChunk(loc) {
    const cLoc = this.getChunkLocation(loc);
    const chunk = new VoxelChunk(cLoc, this.opLimits.get, this);
    return this.chunks.set(cLoc, chunk);
    return chunk;
  }

  getOpLimits(ops) {
    const opLimits = new Map();
    const opsByChunkLoc = this.groupOpsByChunkLocation(ops);
    for (const [cLoc, chunkOps] of opsByChunkLoc) {
      opLimits.set(cLoc, chunkOps.length);
    }
    return opLimits;
  }

  groupOpsByChunkLocation(ops) {
    const opsByChunkLoc = new Map();
    for (const op of ops) {
      const cLoc = this.getChunkLocation(op.loc);
      const opArray = opsByChunkLoc.get(cLoc);
      if (opArray) {
        opArray.push(op)
      }
      else {
        opsByChunkLoc.set(cLoc, [op]);
      }
    }
    return opsByChunkLoc;
  }
}
