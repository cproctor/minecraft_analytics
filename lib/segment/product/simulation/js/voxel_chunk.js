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
  size =        new Vector3(16, 256, 16);

  constructor(cx, cy, cz, opLimit, world) {
    this.world = world;
    this.opLimit = opLimit;
    this.bb0 = new Vector3(cx, cy, cz).multiply(this.size);
    this.bb1 = this.bb0.clone().add(this.size);
    this.voxels = new Map();
  }

  setVoxel(x, y, z, material) {
    if (this.inChunk(x, y, z)) {
      const vKey = this.getVoxelKey(x, y, z);
      this.voxels.set(vKey, material);
    }
    else {
      throw new Error(`Out of bounds: (${x}, ${y}, ${z})`);
    }
  }

  getVoxel(x, y, z) {
    if (this.inChunk(x, y, z)) {
      const vKey = this.getVoxelKey(x, y, z);
      return this.voxels.get(vKey);
    }
    else {
      return this.world.getVoxel(x, y, z);
    }
  }

  inChunk(x, y, z) {
    return (
      this.bb0.x <= x && x < this.bb1.x && 
      this.bb0.y <= y && y < this.bb1.y && 
      this.bb0.z <= z && z < this.bb1.z
    );
  }

  createObjects() {
    const terrain = new MeshLambertMaterial({color:"green"});
    const water = new MeshLambertMaterial({
      color: "blue",
      transparent: true,
      opacity: 0.2
    });
    this.terrain = this.createObject(...this.getTerrainCoords(), terrain);
    this.water = this.createObject(...this.getWaterCoords(), water);
  }

  getObjects() {
    return [this.terrain, this.water];
  }

  createObject(positions, normals, indices, material) {
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
    for (const [ts, [x, y, z], before, after] of ops) {
      const vKey = this.getVoxelKey(x, y, z);
      this.setVoxel(vKey, after);
    }
    this.setGeometry(this.terrain.geometry, ...this.getTerrainCoords());
    this.setGeometry(this.water.geometry, ...this.getWaterCoords());
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
    for (const [vKey, material] of this.voxels) {
      if (this.isSolid(material)) {
        const [x, y, z] = this.voxelKeyToCoords(vKey);
        for (const {dir, corners, uvRow} of Voxel.faces) {
          const [ax, ay, az] = [x+dir.x, y+dir.y, z+dir.z];
          const adjMaterial = this.getVoxel(ax, ay, az);
          if (!this.isSolid(adjMaterial)) {
            const ix = positions.length / 3;
            for (const {pos, uv} of corners) {
              positions.push(x+pos.x, y+pos.y, z+pos.z);
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
    for (const [vKey, material] of this.voxels) {
      if (this.isWater(material)) {
        const [x, y, z] = this.voxelKeyToCoords(vKey);
        for (const {dir, corners, uvRow} of Voxel.faces) {
          const [ax, ay, az] = [x+dir.x, y+dir.y, z+dir.z];
          const adjMaterial = this.getVoxel(ax, ay, az);
          // TODO
          // Air interface should get faces in both directions. 
          // Land interface should get a reversed face
          if (!this.isWater(adjMaterial)) {
            const ix = positions.length / 3;
            for (const {pos, uv} of corners) {
              positions.push(x+pos.x, y+pos.y, z+pos.z);
              normals.push(dir.x, dir.y, dir.z);
              indices.push(ix, ix+1, ix+2, ix+2, ix+1, ix+3);
            }
          }
        }
      }
    }
    return [positions, normals, indices];
  }

  getVoxelKey(x, y, z) {
    return `${x},${y},${z}`;
  }

  voxelKeyToCoords(vKey) {
    return vKey.split(',').map((s) => Number(s));
  }

  bufferSpaceForOps() {
    const facesPerVoxel = 6;
    const trianglesPerFace = 2;
    const verticesPerTriangle = 3;
    return this.opLimit * facesPerVoxel * trianglesPerFace * verticesPerTriangle;
  }

  isSolid(material) {
    return !!material && !this.isWater(material) && !this.isAir(material);
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
