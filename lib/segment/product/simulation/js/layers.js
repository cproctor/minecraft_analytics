'use strict';

import VoxelWorld from "./voxel_world.js";

export class Layer {
  // A layer is initialized with its initial state and a list of all 
  // the ops it will be expected to handle. This allows us to initialize
  // objects which will be needed later, or to initialize buffers
  // of sufficient size.
  
  static create(type, initial, bb0, bb1, ops) {
    const layerTypes = {
      "terrain": TerrainLayer
    }
    return new layerTypes[type](initial, bb0, bb1, ops);
  }

  constructor(initial, bb0, bb1, ops) {
    this.opIndex = 0;
  }

  getObjects() {
    return [];
  }

  seek(newTs) {
    const opset = this.getOpsBetween(this.ts, newTs);
    this.ts = newTs;
  }

  getOpsBetween(startTs, endTs) {
    const opset = [];
    if (startTs <= endTs) {
      for (; this.ops[this.opIndex][0] < endTs; this.opIndex++) {
        ops.push(this.ops[i]);
      }
    }
    else {
      for (; endTs <= this.ops[this.opIndex][0]; this.opIndex--) {
        ops.push(this.reverseOp(this.ops[i]));
      }
    }
    return opset;
  }

  reverseOp(op) {
    const [ts, loc, before, after] = op;
    return [ts, loc, after, before];
  }
}

export class TerrainLayer extends Layer {
  constructor(initial, bb0, bb1, ops) {
    super()
    const [voxels, palette] = initial;
    this.world = new VoxelWorld(voxels, palette, bb0, bb1, ops);
    this.world.createObjects();
    this.ops = ops;
  }

  getObjects() {
    return this.world.getObjects();
  }

  seek(newTs) {
    const opset = this.getOpsBetween(this.ts, newTs);
    this.world.updateGeometries(opset);
    this.ts = newTs;
  }
}
