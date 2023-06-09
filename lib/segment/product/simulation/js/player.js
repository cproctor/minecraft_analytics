'use strict';

import {
  CylinderGeometry,
  MeshLambertMaterial,
  LineBasicMaterial,
  BufferGeometry,
  Mesh,
  Line,
  Vector3
} from "three";

export default class Player {

  height = 2;
  radius = 0.5;
  up = new Vector3(0, 1, 0);

  constructor(initial, bb0, bb1) {
    this.name = initial.name;
    this.bb0 = bb0;
    this.bb1 = bb1;
    this.createObjects(initial);
  }
  createObjects(initial) {
    const bodyGeometry = new CylinderGeometry(this.radius, this.radius, this.height);
    const bodyMaterial = new MeshLambertMaterial({color:"#c0392b"});
    this.body = new Mesh(bodyGeometry, bodyMaterial);
    const [px, py, pz] = initial.position;
    const [tx, ty, tz] = initial.eyeTarget;
    this.body.position.set(px, py + 1, pz);

    const gazeGeometry = new BufferGeometry();
    // TODO there's a three.js issue preventing linewidth from changing. 
    // If I want this different, it has to be a cylinder.
    const gazeMaterial = new LineBasicMaterial({
      color: "red",
      transparent: true,
      opacity: 0.5
    });
    this.gaze = new Line(gazeGeometry, gazeMaterial);
    this.gaze.visible = false;
    if (true || tx instanceof Number) {
      const eye = new Vector3(px, py + 2, pz);
      const target = new Vector3(tx, ty + 0.5, tz);
      this.gaze.geometry.setFromPoints([eye, target]);
      this.gaze.geometry.needsUpdate = true;
      this.gaze.visible = true;
    }
    else {
      this.gaze.visible = false;
    }
  }

  getObjects() {
    return [this.body, this.gaze];
  }

  updateGeometries(ops) {
    for (const [ts, before, after] of ops) {
      const [x, y, z] = after.position;
      this.body.position.set(x, y + 1, z);
      if (true || after.eyeTarget[0] instanceof Number) {
        const [tx, ty, tz] = after.eyeTarget;
        const eye = new Vector3(x, y + 2, z);
        const target = new Vector3(tx, ty + 0.5, tz);
        this.gaze.geometry.setFromPoints([eye, target]);
        this.gaze.geometry.needsUpdate = true;
        this.gaze.visible = true;
      }
      else {
        this.gaze.visible = false;
      }
    }
  }
}


