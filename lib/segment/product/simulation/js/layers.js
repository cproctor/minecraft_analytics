'use strict';

import VoxelWorld from "./voxel_world.js";
import Player from "./player.js";

export class Layer {
  // A layer is initialized with its initial state and a list of all 
  // the ops it will be expected to handle. This allows us to initialize
  // objects which will be needed later, or to initialize buffers
  // of sufficient size.
  
  static create(type, initial, bb0, bb1, ops) {
    const layerTypes = {
      "terrain": TerrainLayer,
      "players": PlayersLayer
    }
    return new layerTypes[type](initial, bb0, bb1, ops);
  }

  constructor() {
  }

  getObjects() {
    return [];
  }

  seek(newTs) {
    const opset = this.getOpsBetween(this.ops, this.ts, newTs);
    this.ts = newTs;
  }

  getOpsBetween(ops, startTs, endTs) {
    const opset = [];
    if (startTs <= endTs) {
      for (const op of ops) {
        if (endTs <= op[0]) {
          break;
        }
        if (startTs <= op[0]) {
          opset.push(op);
        }
      }
    }
    else {
      for (const op of ops) {
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
    for (const op of this.ops) {
       op[0] = Date.parse(op[0]);
    }
    this.ts = ops.length ? this.ops[0][0] : 0;
  }

  getObjects() {
    return this.world.getObjects();
  }

  seek(newTs) {
    const opset = this.getOpsBetween(this.ops, this.ts, newTs);
    this.world.updateGeometries(opset);
    this.ts = newTs;
  }
}

export class PlayersLayer extends Layer {
  constructor(initial, bb0, bb1, ops) {
    super();
    this.players = new Map();
    for (const name in initial) {
      this.players.set(name, new Player(initial[name], bb0, bb1));
    }
    this.ops = ops;
    for (const name in this.ops) {
      for (const op of this.ops[name]) {
        op[0] = Date.parse(op[0]);
      }
    }
  }

  getObjects() {
    const objects = [];
    for (const [name, player] of this.players) {
      for (const object of player.getObjects()) {
        objects.push(object);
      }
    }
    return objects;
  }

  seek(newTs) {
    for (const [name, player] of this.players) {
      const opset = this.getOpsBetween(this.ops[name], this.ts, newTs);
      player.updateGeometries(opset);
    }
    this.ts = newTs;
  }

  reverseOp(op) {
    const [ts, before, after] = op;
    return [ts, after, before];
  }
}
