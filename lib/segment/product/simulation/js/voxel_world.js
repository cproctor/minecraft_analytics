'use strict';

// Next up: 
// - Add ops (granularity: 1s) to the exported data.
// - Have Voxel World process an op set.
//   - See whether processing an opset (and therefore rebuilding the geometry) 
//     takes too long. Possible optimization: Let each chunk be its own geometry; 
//     rebuild each when there are changes.
// - Add a people layer

import {
    BoxGeometry,
    BufferGeometry,
    MeshPhongMaterial,
    MeshLambertMaterial,
    BufferAttribute,
    Mesh,
    Vector3
} from "three";

export default class VoxelWorld {

  constructor(b64, palette, boundingBox, ops) {
    this.palette = palette;
    this.boundingBox = boundingBox;
    this.ops = ops;
    // TODO Re-implement B64 decoding. 
    // See the pair comment in __init__.py. 
    // For now, b64 is a literal array, no decoding needed.
    /*
    const binary = window.atob(b64);
    const len = binary.length;
    this.voxelBuffer = new Uint8Array(len);
    for (var i = 0; i < len; i++) {
      this.voxelBuffer[i] = binary.charCodeAt(i);
    }
    */
    this.voxelBuffer = b64
    this.geometryLayers = {}
  }

  getFaceData() {
    const positions = [];
    const normals = [];
    //const uvs = [];
    const indices = [];
    const [[x0, x1], [y0, y1], [z0, z1]] = this.boundingBox;
    for (var y = y0; y < y1; y++) {
      for (var z = z0; z < z1; z++) {
        for (var x = x0; x < x1; x++) {
          const material = this.getVoxelMaterial(x, y, z);
          if (this.isSolid(material)) {
            for (const {dir, corners, uvRow} of this.faces) {
              const [dx, dy, dz] = dir
              const [nx, ny, nz] = [x+dx, y+dy, z+dz]
              const neighbor = this.getVoxelMaterial(nx, ny, nz)
              if (!this.isSolid(neighbor)) {
                const nix = positions.length / 3;
                for (const {pos, uv} of corners) {
                  const [px, py, pz] = pos;
                  positions.push(x+px, y+py, z+pz);
                  normals.push(...dir);
                  indices.push(nix, nix+1, nix+2, nix+2, nix+1, nix+3);
                }
              }
            }
          }
        }
      }
    }
    return [positions, normals, indices]
  }

  createBaseGeometry() {
    const [positions, normals, indices] = this.getFaceData();
    const geometry = new BufferGeometry();
    const extraSpace = this.facesCreatedByOpsUpperBound()
    this.geometryLength = positions.length + extraSpace;
    const positionsArray = new Float32Array(this.geometryLength);
    const normalsArray = new Float32Array(this.geometryLength);
    for (var i = 0; i < positions.length; i++) {
      positionsArray[i] = positions[i];
      normalsArray[i] = normals[i];
    }
    geometry.setAttribute('position', new BufferAttribute(positionsArray, 3));
    geometry.setAttribute('normal', new BufferAttribute(normalsArray, 3));
    geometry.setIndex(indices);
    const material = new MeshLambertMaterial({color:"green"});
    const mesh = new Mesh(geometry, material);
    this.geometryLayers['base'] = mesh;
  }

  updateBaseGeometry(opset) {
    for (const op of opset) {
      const [layer, [x, y, z], before, after] = op;
      this.setVoxelMaterial(x, y, z, after);
    }
    const [positions, normals, indices] = this.getFaceData();
    const geometry = this.geometryLayers['base'].geometry
    const positionsArray = geometry.getAttribute('position').array;
    const normalsArray = geometry.getAttribute('normal').array;
    for (var i = 0; i < positions.length; i++) {
      positionsArray[i] = positions[i];
      normalsArray[i] = normals[i];
    }
    geometry.attributes.position.needsUpdate = true;
    geometry.attributes.normal.needsUpdate = true;
    geometry.setIndex(indices);
  }

  createWaterGeometry() {
    const positions = [];
    const normals = [];
    const indices = [];
    const [[x0, x1], [y0, y1], [z0, z1]] = this.boundingBox;
    for (var y = y0; y < y1; y++) {
      for (var z = z0; z < z1; z++) {
        for (var x = x0; x < x1; x++) {
          const material = this.getVoxelMaterial(x, y, z);
          if (this.isWater(material)) {
            for (const {dir, corners, uvRow} of this.faces) {
              const [dx, dy, dz] = dir
              const [nx, ny, nz] = [x+dx, y+dy, z+dz]
              const neighbor = this.getVoxelMaterial(nx, ny, nz)
              if (!this.isWater(neighbor)) {
                const nix = positions.length / 3;
                for (const {pos, uv} of corners) {
                  const [px, py, pz] = pos;
                  positions.push(x+px, y+py, z+pz);
                  normals.push(...dir);
                  indices.push(nix, nix+1, nix+2, nix+2, nix+1, nix+3);
                }
              }
            }
          }
        }
      }
    }
    const geometry = new BufferGeometry();
    geometry.setAttribute('position', new BufferAttribute(new Float32Array(positions), 3));
    geometry.setAttribute('normal', new BufferAttribute(new Float32Array(normals), 3));
    geometry.setIndex(indices);
    const material = new MeshLambertMaterial({color:"blue"});
    material.transparent = true;
    material.opacity = 0.2;
    const mesh = new Mesh(geometry, material);
    this.geometryLayers['water'] = mesh;
  }

  getVoxelMaterial(x, y, z) {
    if (!this.inBounds(x, y, z)) return undefined;
    const [[x0, x1], [y0, y1], [z0, z1]] = this.boundingBox;
    const offset =  (y-y0)*(x1-x0)*(z1-z0) + (z-z0)*(x1-x0) + (x-x0);
    const paletteIndex = this.voxelBuffer[offset]
    return this.palette[paletteIndex];
  }

  setVoxelMaterial(x, y, z, material) {
    const [[x0, x1], [y0, y1], [z0, z1]] = this.boundingBox;
    const materialId = this.palette.indexOf(material);
    const offset =  (y-y0)*(x1-x0)*(z1-z0) + (z-z0)*(x1-x0) + (x-x0);
    this.voxelBuffer[offset] = materialId;
  }

  facesCreatedByOpsUpperBound() {
    const facesPerVoxel = 6;
    const trianglesPerFace = 2;
    let nOps = 0;
    for (const opset of this.ops) {
        nOps += opset.length;
    }
    return nOps * facesPerVoxel * trianglesPerFace;
  }

  isSolid(material) {
    return !!material && !this.isAir(material) && !this.isWater(material);
  }

  isWater(material) {
    return material == 'minecraft:water';
  }

  isAir(material) {
    return material == 'minecraft:air' || material == 'minecraft:cave_air';
  }

  inBounds(x, y, z) {
    const [[x0, x1], [y0, y1], [z0, z1]] = this.boundingBox;
    return x0 <= x && x < x1 && y0 <= y && y < y1 && z0 <= z && z < z1
  }

  getInitialCameraPosition() {
    const [[x0, x1], [y0, y1], [z0, z1]] = this.boundingBox;
    return [x1+(x1-x0)/3, y1+(x1-x0+z1-z0)/6, z1+(z1-z0)/3]
  }

  getInitialControlsTarget() {
    const [[x0, x1], [y0, y1], [z0, z1]] = this.boundingBox;
    return [x0+(x1-x0)/2, y0+(y1-y0)/2, z0+(z1-z0)/2];
  }

  // Positions a light at the (+x, +y, -z) corner of the bounding box 
  getLightPosition() {
    const [[x0, x1], [y0, y1], [z0, z1]] = this.boundingBox;
    const [xLen, yLen, zLen] = [x1-x0, y1-y0, z1-z0];
    return [x1 + xLen, y1 + yLen, z0 - zLen];
  }

  faces = [
    { // left
      uvRow: 0,
      dir: [ -1,  0,  0, ],
      corners: [
        { pos: [ 0, 1, 0 ], uv: [ 0, 1 ], },
        { pos: [ 0, 0, 0 ], uv: [ 0, 0 ], },
        { pos: [ 0, 1, 1 ], uv: [ 1, 1 ], },
        { pos: [ 0, 0, 1 ], uv: [ 1, 0 ], },
      ],
    },
    { // right
      uvRow: 0,
      dir: [  1,  0,  0, ],
      corners: [
        { pos: [ 1, 1, 1 ], uv: [ 0, 1 ], },
        { pos: [ 1, 0, 1 ], uv: [ 0, 0 ], },
        { pos: [ 1, 1, 0 ], uv: [ 1, 1 ], },
        { pos: [ 1, 0, 0 ], uv: [ 1, 0 ], },
      ],
    },
    { // bottom
      uvRow: 1,
      dir: [  0, -1,  0, ],
      corners: [
        { pos: [ 1, 0, 1 ], uv: [ 1, 0 ], },
        { pos: [ 0, 0, 1 ], uv: [ 0, 0 ], },
        { pos: [ 1, 0, 0 ], uv: [ 1, 1 ], },
        { pos: [ 0, 0, 0 ], uv: [ 0, 1 ], },
      ],
    },
    { // top
      uvRow: 2,
      dir: [  0,  1,  0, ],
      corners: [
        { pos: [ 0, 1, 1 ], uv: [ 1, 1 ], },
        { pos: [ 1, 1, 1 ], uv: [ 0, 1 ], },
        { pos: [ 0, 1, 0 ], uv: [ 1, 0 ], },
        { pos: [ 1, 1, 0 ], uv: [ 0, 0 ], },
      ],
    },
    { // back
      uvRow: 0,
      dir: [  0,  0, -1, ],
      corners: [
        { pos: [ 1, 0, 0 ], uv: [ 0, 0 ], },
        { pos: [ 0, 0, 0 ], uv: [ 1, 0 ], },
        { pos: [ 1, 1, 0 ], uv: [ 0, 1 ], },
        { pos: [ 0, 1, 0 ], uv: [ 1, 1 ], },
      ],
    },
    { // front
      uvRow: 0,
      dir: [  0,  0,  1, ],
      corners: [
        { pos: [ 0, 0, 1 ], uv: [ 0, 0 ], },
        { pos: [ 1, 0, 1 ], uv: [ 1, 0 ], },
        { pos: [ 0, 1, 1 ], uv: [ 0, 1 ], },
        { pos: [ 1, 1, 1 ], uv: [ 1, 1 ], },
      ],
    }
  ]

  // Not currently used. 
  getTargetVoxel(camera) {
    const start = new Vector3();
    const end = new Vector3();
    start.setFromMatrixPosition(camera.matrixWorld);
    end.set(0, 0, 1).unproject(camera);
    const result = this.intersectRay(start, end);
    return result;
  }

  // Not currently used. 
  // from
  // https://r105.threejsfundamentals.org/threejs/lessons/threejs-voxel-geometry.html
  // http://www.cse.chalmers.se/edu/year/2010/course/TDA361/grid.pdf
  intersectRay(start, end) {
    let dx = end.x - start.x;
    let dy = end.y - start.y;
    let dz = end.z - start.z;
    const lenSq = dx * dx + dy * dy + dz * dz;
    const len = Math.sqrt(lenSq);

    dx /= len;
    dy /= len;
    dz /= len;

    let t = 0.0;
    let ix = Math.floor(start.x);
    let iy = Math.floor(start.y);
    let iz = Math.floor(start.z);

    const stepX = (dx > 0) ? 1 : -1;
    const stepY = (dy > 0) ? 1 : -1;
    const stepZ = (dz > 0) ? 1 : -1;

    const txDelta = Math.abs(1 / dx);
    const tyDelta = Math.abs(1 / dy);
    const tzDelta = Math.abs(1 / dz);

    const xDist = (stepX > 0) ? (ix + 1 - start.x) : (start.x - ix);
    const yDist = (stepY > 0) ? (iy + 1 - start.y) : (start.y - iy);
    const zDist = (stepZ > 0) ? (iz + 1 - start.z) : (start.z - iz);

    // location of nearest voxel boundary, in units of t
    let txMax = (txDelta < Infinity) ? txDelta * xDist : Infinity;
    let tyMax = (tyDelta < Infinity) ? tyDelta * yDist : Infinity;
    let tzMax = (tzDelta < Infinity) ? tzDelta * zDist : Infinity;

    let steppedIndex = -1;

    // main loop along raycast vector
    while (t <= len) {
      if (this.isSolid(ix, iy, iz)) {
        return {
          position: [
            start.x + t * dx,
            start.y + t * dy,
            start.z + t * dz,
          ],
          normal: [
            steppedIndex === 0 ? -stepX : 0,
            steppedIndex === 1 ? -stepY : 0,
            steppedIndex === 2 ? -stepZ : 0,
          ],
          voxel: [ix, iy, iz],
        };
      }

      // advance t to next nearest voxel boundary
      if (txMax < tyMax) {
        if (txMax < tzMax) {
          ix += stepX;
          t = txMax;
          txMax += txDelta;
          steppedIndex = 0;
        } else {
          iz += stepZ;
          t = tzMax;
          tzMax += tzDelta;
          steppedIndex = 2;
        }
      } else {
        if (tyMax < tzMax) {
          iy += stepY;
          t = tyMax;
          tyMax += tyDelta;
          steppedIndex = 1;
        } else {
          iz += stepZ;
          t = tzMax;
          tzMax += tzDelta;
          steppedIndex = 2;
        }
      }
    }
    return null;
  }
}
