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

  constructor() {
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
      for (const op of this.ops) {
        if (endTs <= op[0]) {
          break;
        }
        if (startTs <= op[0]) {
          opset.push(op);
        }
      }
    }
    else {
      for (const op of this.ops) {
        if (startTs <= op[0]) {
          break;
        }
        if (endTs <= op[0]) {
          opset.push(this.reverseOp(op));
        }
      }
      opset.reverse();
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
    super();
    const [voxels, palette] = initial;
    this.world = new VoxelWorld(voxels, palette, bb0, bb1, ops);
    this.world.createObjects();
    this.opIndex = 0;
    this.ops = ops;
    this.ts = ops.length ? this.ops[0][0] : 0;
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
