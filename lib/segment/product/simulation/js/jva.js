'use strict';

import {
  SphereGeometry,
  MeshLambertMaterial,
  BufferGeometry,
  Mesh,
  Vector3
} from "three";

export default class JVA {
  radius = 0.5;

  constructor(initial, bb0, bb1) {
    this.name = initial.name;
    this.bb0 = bb0;
    this.bb1 = bb1;
    this.createObjects(initial);
  }
  createObjects(initial) {
    const geometry = new SphereGeometry(this.radius);
    const material = new MeshLambertMaterial({
      color:"#ffff00",
      transparent: true,
      opacity: 1
    });
    this.object = new Mesh(geometry, material);
    const [visible, px, py, pz] = initial;
    this.object.position.set(px, py, pz);
    this.object.visible = visible;
    this.object.geometry.needsUpdate = true;
  }

  getObjects() {
    return [this.object];
  }

  updateGeometries(ops) {
    for (const [ts, before, after] of ops) {
      const [visible, x, y, z] = after;
      this.object.visible = visible;
      this.object.position.set(x, y, z);
    }
  }
}



