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
  bodyRadius = 0.5;
  gazeRadiusEye = 0.1;
  gazeRadiusTarget = 0.2
  eyeHeight = 1.75
  up = new Vector3(0, 1, 0);

  constructor(initial, bb0, bb1) {
    this.name = initial.name;
    this.bb0 = bb0;
    this.bb1 = bb1;
    this.createObjects(initial);
  }
  createObjects(initial) {
    const bodyGeometry = new CylinderGeometry(this.bodyRadius, this.bodyRadius, this.height);
    const bodyMaterial = new MeshLambertMaterial({color:"#c0392b"});
    this.body = new Mesh(bodyGeometry, bodyMaterial);
    const [px, py, pz] = initial.position;
    const [tx, ty, tz] = initial.eyeTarget;
    this.body.position.set(px, py + 1, pz);

    const gazeGeometry = new CylinderGeometry(this.gazeRadiusTarget, this.gazeRadiusEye, 1)
      .translate(0, 0.5, 0)
      .rotateX(Math.PI * 0.5);
    const gazeMaterial = new MeshLambertMaterial({
      color:"#c0392b", 
      transparent: true, 
      opacity: 0.4
    });
    this.gaze = new Mesh(gazeGeometry, gazeMaterial);
    const eye = new Vector3(px, py + this.eyeHeight, pz);
    const target = new Vector3(tx, ty + 0.5, tz);
    this.gaze.position.set(eye);
    this.gaze.scale.z = eye.distanceTo(target);
    this.gaze.lookAt(target);
    this.gaze.geometry.needsUpdate = true;
  }

  getObjects() {
    return [this.body, this.gaze];
  }

  updateGeometries(ops) {
    for (const [ts, before, after] of ops) {
      const [x, y, z] = after.position;
      this.body.position.set(x, y + 1, z);
      const [tx, ty, tz] = after.eyeTarget;
      const eye = new Vector3(x, y + this.eyeHeight, z);
      const target = new Vector3(tx, ty + 0.5, tz);
      this.gaze.position.copy(eye);
      this.gaze.scale.z = eye.distanceTo(target);
      this.gaze.lookAt(target);
      this.gaze.geometry.needsUpdate = true;
    }
  }
}


