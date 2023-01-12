'use strict';

import {
    BoxGeometry,
    MeshPhongMaterial,
    Mesh
} from "three";

export default class VoxelWorld {
    constructor(b64, palette, bounding_box) {
        this.palette = palette
        this.bounding_box = bounding_box
        const binary = window.atob(b64);
        const len = binary.length;
        this.buffer = new Uint8Array(len);
        for (var i = 0; i < len; i++) {
            this.buffer[i] = binary.charCodeAt(i);
        }
    }

    generate_faces_for_all_voxels() {
        const [[x0, x1], [y0, y1], [z0, z1]] = this.bounding_box;
        for (var y = y0; y < y1; y++) {
            for (var z = z0; z < z1; z++) {
                for (var x = x0; x < x1; x++) {
                    this.generate_faces_for_voxel(x, y, z);
                }
            }
        }
    }

    add_geometry(scene) {
        const cube_geometry = new BoxGeometry(1, 1, 1);
        const [[x0, x1], [y0, y1], [z0, z1]] = this.bounding_box;
        for (var y = y0; y < y1; y++) {
            for (var z = z0; z < z1; z++) {
                for (var x = x0; x < x1; x++) {
                    const material = this.get_voxel_material(x, y, z);
                    console.log(x, y, z, material)
                    if (material != 'minecraft:air' && material != 'meta:void') {
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

    generate_faces_for_voxel(x, y, z) {
    }

    get_voxel_material(x, y, z) {
        const [[x0, x1], [y0, y1], [z0, z1]] = this.bounding_box;
        const offset =  (y-y0)*(x1-x0)*(z1-z0) + (z-z0)*(x1-x0) + (x-x0);
        return this.palette[this.buffer[offset]];
    }
}
