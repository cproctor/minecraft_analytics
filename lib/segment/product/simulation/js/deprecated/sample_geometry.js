'use strict';

import {
    BoxGeometry,
    MeshPhongMaterial,
    Mesh
} from "three";

export default function add_geometry_to_scene(scene) { // TEST GEOMETRY
  const geometry = new BoxGeometry(1, 1, 1);

  function makeInstance(geometry, color, x) {
    const material = new MeshPhongMaterial({color});
    const cube = new Mesh(geometry, material);
    scene.add(cube);
    cube.position.x = x;
    return cube;
  }

  makeInstance(geometry, 0x44aa88,  0);
  makeInstance(geometry, 0x8844aa, -2);
  makeInstance(geometry, 0xaa8844,  2);
}

