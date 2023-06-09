'use strict';

import {
    WebGLRenderer,
    PerspectiveCamera,
    Scene,
    DirectionalLight,
    AmbientLight,
    Color,
    BoxGeometry,
    MeshPhongMaterial,
    Mesh
} from "three";
import { DateTime } from "luxon";
import { OrbitControls } from "./OrbitControls.js";

// Currently, we re-render on the controls 'change' event and on window resize. 
// This is appropriate. However, I also want to implement an onChange hook in
// VoxelWorld so that when Timeline sends opsets to VoxelWorld, it can detect
// whether there were changes and make the appropriate render.

export default class Simulation {
  fov = 75;
  aspect = 2;
  near = 0.1;
  far = 1000;
  backgroundColor = "lightblue";
  ambientLightColor = 0xDDDDFF;
  ambientLightIntensity = 0.5

  constructor(el, layers, bb0, bb1) {
    this.layers = layers;
    this.bb0 = bb0;
    this.bb1 = bb1;
    this.size = bb1.clone().sub(bb0);
    this.center = bb0.clone().add(this.size.clone().divideScalar(2));
    this.canvas = document.querySelector("#simulation");
    this.renderer = new WebGLRenderer({canvas: this.canvas});
    this.camera = new PerspectiveCamera(this.fov, this.aspect, this.near, this.far);
    this.camera.position.set(...this.getInitialCameraPosition());
    this.controls = new OrbitControls(this.camera, this.canvas);
    this.controls.target.set(...this.getInitialControlsTarget());
    this.controls.update();
    this.scene = new Scene();
    this.scene.background = new Color(this.backgroundColor);
    for (const light of this.createLights()) {
      this.scene.add(light);
    }
    for (const [name, layer] of this.layers) {
      for (const object of layer.getObjects()) {
        this.scene.add(object);
      }
    }

    this.showTarget();

    const self = this;
    this.controls.addEventListener('change', () => {
      self.showTarget();
      self.render();
    });
    window.addEventListener('resize', () => {self.render()});
  }

  showTarget() {
    const x = Math.round(this.controls.target.x);
    const y = Math.round(this.controls.target.y);
    const z = Math.round(this.controls.target.z);
    //document.querySelector("#position").innerText = `(${x}, ${y}, ${z})`;
  }

  render() {
    if (this.resizeRendererToDisplaySize()) {
      const canvas = this.renderer.domElement;
      this.camera.aspect = canvas.clientWidth / canvas.clientHeight;
      this.camera.updateProjectionMatrix();
    }
    this.renderer.render(this.scene, this.camera);
  }

  seek(ts) {
    for (const [name, layer] of this.layers) {
      layer.seek(ts);
    }
    const dt = DateTime.fromJSDate(ts)
    const dts = dt.toLocaleString(DateTime.DATETIME_MED_WITH_SECONDS)
    document.querySelector("#time").innerText = dts
    this.render();
  }

  resizeRendererToDisplaySize() {
    const canvas = this.renderer.domElement;
    const width = canvas.clientWidth;
    const height = canvas.clientHeight;
    const needResize = canvas.width !== width || canvas.height !== height;
    if (needResize) {
      this.renderer.setSize(width, height, false);
    }
    return needResize;
  }

  getInitialCameraPosition() {
    return [
      this.bb1.x + this.size.x/3, 
      this.bb1.y + (this.size.x + this.size.z)/6, 
      this.bb1.z + this.size.z/3
    ]
  }

  getInitialControlsTarget() {
    return [this.center.x, this.center.y, this.center.z];
  }

  createLights() {
    const ambientLight = new AmbientLight(0xDDDDFF, 0.5);
    const directionalLight = new DirectionalLight(0xFFFFFF, 1);
    directionalLight.position.set(
      this.bb1.x + this.size.x, 
      this.bb1.y + this.size.y, 
      this.bb0.z - this.size.z
    )
    return [ambientLight, directionalLight];
  }

}
