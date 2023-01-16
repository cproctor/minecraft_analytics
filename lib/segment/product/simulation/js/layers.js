'use strict';

import VoxelWorld from "./voxel_world.js";

export class Layer {
  // A layer is initialized with its initial state and a list of all 
  // the ops it will be expected to handle. This allows us to initialize
  // objects which will be needed later, or to initialize buffers
  // of sufficient size.
  
  static create(type, initial, ops) {
    const layerTypes = {
      "terrain": TerrainLayer
    }
    return new layerTypes[type](initial, ops);
  }

  constructor() {
  }

  getMeshes() {
    return [];
  }

  seek(newTs) {
    const opset = this.getOpsBetween(this.ts, newTs);
    this.ts = newTs;
  }

  getOpsBetween(startTs, endTs) {
    const opset = [];
    if (startTs <= endTs) {
      for (; this.ops[this.opIndex].ts < endTs; this.opIndex++) {
        ops.push(this.ops[i]);
      }
    }
    else {
      for (; endTs <= this.ops[this.opIndex].ts; this.opIndex--) {
        ops.push(this.ops[i].reversed());
      }
    }
    return opset;
  }
}

export class TerrainLayer extends Layer {
  constructor(initial, ops) {
    super()
    const [worldState, palette] = initial;
    this.world = new VoxelWorld(worldState, palette, ops);
    this.world.createMeshes();
    this.ops = ops;
  }

  getMeshes() {
    return this.world.getMeshes();
  }

  seek(newTs) {
    const opset = this.getOpsBetween(this.ts, newTs);
    this.world.updateGeometries(opset);
    this.ts = newTs;
  }
}
