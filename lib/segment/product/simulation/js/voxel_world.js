'use strict';

// Optimization: Let each chunk be its own geometry; rebuild each when 
// there are changes.

import {
    BoxGeometry,
    BufferGeometry,
    MeshPhongMaterial,
    MeshLambertMaterial,
    BufferAttribute,
    Mesh
} from "three";

export default class VoxelWorld {

  unrendered_materials = [
    'minecraft:air',
    'minecraft:cave_air',
    'meta:void'
  ];

  constructor(b64, palette, bounding_box) {
    this.palette = palette
    this.cache_unrendered_material_indices()
    this.bounding_box = bounding_box
    const binary = window.atob(b64);
    const len = binary.length;
    this.voxel_buffer = new Uint8Array(len);
    for (var i = 0; i < len; i++) {
      this.voxel_buffer[i] = binary.charCodeAt(i);
    }
    this.geometry_layers = {}
  }

  create_base_geometry() {
    const positions = [];
    const normals = [];
    const uvs = [];
    const indices = [];
    const [[x0, x1], [y0, y1], [z0, z1]] = this.bounding_box;
    for (var y = y0; y < y1; y++) {
      for (var z = z0; z < z1; z++) {
        for (var x = x0; x < x1; x++) {
          const material = this.get_voxel_material(x, y, z);
          if (this.is_solid(material)) {
            console.log(material);
            for (const {dir, corners, uvRow} of this.faces) {
              const [dx, dy, dz] = dir
              const [nx, ny, nz] = [x+dx, y+dy, z+dz]
              const neighbor = this.get_voxel_material(nx, ny, nz)
              if (!this.is_solid(neighbor)) {
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
    const material = new MeshLambertMaterial({color:"green"});
    const mesh = new Mesh(geometry, material);
    this.geometry_layers['base'] = mesh;
  }

  create_water_geometry() {
    const positions = [];
    const normals = [];
    const indices = [];
    const [[x0, x1], [y0, y1], [z0, z1]] = this.bounding_box;
    for (var y = y0; y < y1; y++) {
      for (var z = z0; z < z1; z++) {
        for (var x = x0; x < x1; x++) {
          const material = this.get_voxel_material(x, y, z);
          if (this.is_water(material)) {
            for (const {dir, corners, uvRow} of this.faces) {
              const [dx, dy, dz] = dir
              const [nx, ny, nz] = [x+dx, y+dy, z+dz]
              const neighbor = this.get_voxel_material(nx, ny, nz)
              if (!this.is_water(neighbor)) {
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
    material.opacity = 0.3;
    const mesh = new Mesh(geometry, material);
    this.geometry_layers['water'] = mesh;
  }

  add_cube_geometry() {
    const cube_geometry = new BoxGeometry(1, 1, 1);
    const [[x0, x1], [y0, y1], [z0, z1]] = this.bounding_box;
    for (var y = y0; y < y1; y++) {
      for (var z = z0; z < z1; z++) {
        for (var x = x0; x < x1; x++) {
          const material = this.get_voxel_material(x, y, z);
          //console.log(x, y, z, material)
          if (material) {
            const cube = this.make_cube(cube_geometry, "green", x, y, z)
            scene.add(cube);
          }
        }
      }
    }
  }

  make_cube(geometry, color, x, y, z) {
    const material = new MeshPhongMaterial({color});
    const cube = new Mesh(geometry, material);
    cube.position.x = x;
    cube.position.y = y;
    cube.position.z = z;
    return cube;
  }

  get_voxel_material(x, y, z) {
    if (!this.in_bounds(x, y, z)) return undefined;
    const [[x0, x1], [y0, y1], [z0, z1]] = this.bounding_box;
    const offset =  (y-y0)*(x1-x0)*(z1-z0) + (z-z0)*(x1-x0) + (x-x0);
    const palette_index = this.voxel_buffer[offset]
    return this.palette[palette_index];
  }

  is_solid(material) {
    return !!material && !this.is_air(material) && !this.is_water(material);
  }

  is_water(material) {
    return material == 'minecraft:water';
  }

  is_air(material) {
    return material == 'minecraft:air' || material == 'minecraft:cave_air';
  }

  in_bounds(x, y, z) {
    const [[x0, x1], [y0, y1], [z0, z1]] = this.bounding_box;
    return x0 <= x && x < x1 && y0 <= y && y < y1 && z0 <= z && z < z1
  }

  get_initial_camera_position() {
    const [[x0, x1], [y0, y1], [z0, z1]] = this.bounding_box;
    return [x1+(x1-x0)/3, y1+(x1-x0+z1-z0)/6, z1+(z1-z0)/3]
  }

  get_initial_controls_target() {
    const [[x0, x1], [y0, y1], [z0, z1]] = this.bounding_box;
    return [x0+(x1-x0)/2, y0+(y1-y0)/2, z0+(z1-z0)/2];
  }

  cache_unrendered_material_indices() {
    this.unrendered_material_indices = new Set();
    for (const m of this.unrendered_materials) {
      this.unrendered_material_indices.add(this.palette.indexOf(m));
    }
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
}
