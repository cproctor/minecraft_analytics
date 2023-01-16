'use strict';

import {
    BoxGeometry,
    BufferGeometry,
    MeshPhongMaterial,
    MeshLambertMaterial,
    BufferAttribute,
    Mesh,
    Vector3
} from "three";

import Voxel from "./voxel.js";

export default class VoxelChunk {

  static size = new Vector3(16, 256, 16);
  size = new Vector3(16, 256, 16);

  constructor(chunkLocation, opLimit, world) {
    this.cLoc = chunkLocation;
    this.world = world;
    this.opLimit = opLimit;
    this.bb0 = this.cLoc.clone().multiply(this.size);
    this.bb1 = this.bb0.clone().add(this.size);
    this.initVoxelArray();
  }

  setVoxel(loc, material) {
    if (this.inChunk(loc)) {
      const local = this.toLocalCoords(loc);
      this.voxels[local.y][local.z][local.x] = material;
    }
    else {
      outOfBounds(loc, "set");
    }
  }

  getVoxel(loc) {
    if (this.inChunk(loc)) {
      const local = this.toLocalCoords(loc);
      return this.voxels[local.y][local.z][local.x];
    }
    else {
      this.world.getVoxel(loc);
    }
  }

  outOfBounds(loc, verb) {
    const locStr = this.vectorToString(loc);
    const cLocStr = this.vectorToString(this.cLoc);
    throw new Error(`Out of bounds. Tried to ${verb} (${locStr}) from chunk (${cLocStr})`);
  }

  vectorToString(vec) {
    return `${vec.x}, ${vec.y}, ${vec.z}`
  }

  inChunk(loc) {
    return (
      this.bb0.x <= loc.x && loc.x < this.bb1.x && 
      this.bb0.y <= loc.y && loc.y < this.bb1.y && 
      this.bb0.z <= loc.z && loc.z < this.bb1.z
    );
  }

  toLocalCoords(loc) {
    return loc.clone().sub(this.bb0);
  }

  initVoxelArray() {
    this.voxels = [];
    const voxels = new Array(this.size.y);
    for (let y = 0; y < this.size.y; y++) {
      this.voxels[y] = new Array(this.size.z);
      for (let z = 0; z < this.size.z; z++) {
        this.voxels[y][z] = new Array(this.size.x);
      }
    }
  }

  createMeshes() {
    const terrain = new MeshLambertMaterial({color:"green"});
    const water = new MeshLambertMaterial({
      color: "blue",
      transparent: true,
      opacity: 0.2
    });
    this.terrainMesh = this.createMesh(...this.getTerrainCoords(), terrain);
    this.waterMesh = this.createMesh(...this.getWaterCoords(), water);
  }

  createMesh(positions, normals, indices, material) {
    const bufferSize = positions.length + this.bufferSpaceForOps();
    const positionsArray = new Float32Array(bufferSize);
    const normalsArray = new Float32Array(bufferSize);
    const geometry = new BufferGeometry();
    geometry.setAttribute('position', new BufferAttribute(positionsArray, 3));
    geometry.setAttribute('normal', new BufferAttribute(normalsArray, 3));
    this.setGeometry(geometry, positions, normals, indices);
    return new Mesh(geometry, material);
  }

  updateGeometries(ops) {
    for (const op of ops) {
      this.setVoxel(op.loc, op.after);
    }
    this.setGeometry(this.terrainMesh.geometry, ...this.getTerrainCoords());
    this.setGeometry(this.waterMesh.geometry, ...this.getWaterCoords());
  }

  setGeometry(geometry, positions, normals, indices) {
    const geometryPositions = geometry.getAttribute('position').array;
    const geometryNormals = geometry.getAttribute('normal').array;
    for (var i = 0; i < geometryPositions.length; i++) {
      geometryPositions[i] = positions[i];
      geometryNormals[i] = normals[i];
    }
    geometry.setIndex(indices);
    geometry.attributes.position.needsUpdate = true;
    geometry.attributes.normal.needsUpdate = true;
  }

  getTerrainCoords() {
    const positions = [];
    const normals = [];
    const indices = [];
    for (const loc of this.iterVoxelLocs()) {
      const voxel = this.getVoxel(loc);
      if (this.isSolid(voxel)) {
        for (const {dir, corners, uvRow} of Voxel.faces) {
          const adjLoc = loc.clone().add(dir);
          const adjVoxel = this.getVoxel(adjLoc);
          if (!this.isSolid(adjVoxel)) {
            const ix = positions.length / 3;
            for (const {cornerVector, uv} of corners) {
              const cornerLoc = loc.clone().add(cornerVector);
              positions.push(cornerLoc.x, cornerLoc.y, cornerLoc.z);
              normals.push(dir.x, dir.y, dir.z);
              indices.push(ix, ix+1, ix+2, ix+2, ix+1, ix+3);
            }
          }
        }
      }
    }
    return [positions, normals, indices];
  }

  getWaterCoords() {
    const positions = [];
    const normals = [];
    const indices = [];
    for (const loc of this.iterVoxelLocs()) {
      const voxel = this.getVoxel(loc);
      if (this.isWater(voxel)) {
        for (const {unitVector, corners, uvRow} of Voxel.faces) {
          const adjLoc = loc.clone().add(unitVector);
          const adjVoxel = this.getVoxel(adjLoc);
          if (!this.isWater(adjVoxel)) {
            // TODO
            // Air interface should get faces in both directions. 
            // Land interface should get a reversed face
            const ix = positions.length / 3;
            for (const {cornerVector, uv} of corners) {
              const cornerLoc = loc.clone().add(cornerVector);
              positions.push(cornerLoc.x, cornerLoc.y, cornerLoc.z);
              normals.push(dir.x, dir.y, dir.z);
              indices.push(ix, ix+1, ix+2, ix+2, ix+1, ix+3);
            }
          }
        }
      }
    }
    return [positions, normals, indices];
  }

  // TODO: This seems to enter an infinite loop
  * iterVoxelLocs() {
    for (let y = this.bb0.y; y < this.bb1.y; y++) {
      for (let z = this.bb0.z; z < this.bb1.z; z++) {
        for (let x = this.bb0.x; x < this.bb1.x; x++) {
          yield new Vector3(x, y, z);
        }
      }
    }
  }

  bufferSpaceForOps() {
    const facesPerVoxel = 6;
    const trianglesPerFace = 2;
    const verticesPerTriangle = 3;
    return this.opLimit * facesPerVoxel * trianglesPerFace * verticesPerTriangle;
  }

  isSolid(material) {
    return !this.isWater(material) && !this.isAir(material);
  }

  isWater(material) {
    return material == 'minecraft:water';
  }

  isAir(material) {
    return (
      material == 'minecraft:air' ||
      material == 'minecraft:cave_air' ||
      material == 'meta:void'
    )
  }
}
