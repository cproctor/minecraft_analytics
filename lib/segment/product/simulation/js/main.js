'use strict';

import {
    WebGLRenderer,
    PerspectiveCamera,
    Scene,
    DirectionalLight,
    Color,
    BoxGeometry,
    MeshPhongMaterial,
    Mesh
} from "three";
//import { createApp } from "vue";
import { OrbitControls } from "./OrbitControls.js";
import VoxelWorld from "./voxel_world.js";
//import Timeline from "./vue/timeline.vue";

//const app = createApp(Timeline);
//app.mount('#timeline');

const canvas = document.querySelector("#simulation");
const renderer = new WebGLRenderer({canvas});
const world = new VoxelWorld(
    window.DATA.layers.base.start, 
    window.DATA.layers.base.palette,
    window.DATA.params.bounding_box
)
const fov = 75;
const aspect = 2;
const near = 0.1;
const far = 1000; // TODO respect bounding box
const camera = new PerspectiveCamera(fov, aspect, near, far);
camera.position.set(...world.getInitialCameraPosition());
const controls = new OrbitControls(camera, canvas);
controls.target.set(...world.getInitialControlsTarget());
controls.update();
const scene = new Scene();
scene.background = new Color('lightblue');

function addLight(x, y, z) {
  const color = 0xFFFFFF;
  const intensity = 1;
  const light = new DirectionalLight(color, intensity);
  light.position.set(x, y, z);
  scene.add(light);
}
// TODO update lighting to match bounding box
addLight(-1,  2,  4);

world.create_base_geometry()
world.create_water_geometry()
scene.add(world.geometry_layers['base'])
scene.add(world.geometry_layers['water'])

function resizeRendererToDisplaySize(renderer) {
  const canvas = renderer.domElement;
  const width = canvas.clientWidth;
  const height = canvas.clientHeight;
  const needResize = canvas.width !== width || canvas.height !== height;
  if (needResize) {
    renderer.setSize(width, height, false);
  }
  return needResize;
}

function render() {
  if (resizeRendererToDisplaySize(renderer)) {
    const canvas = renderer.domElement;
    camera.aspect = canvas.clientWidth / canvas.clientHeight;
    camera.updateProjectionMatrix();
  }
  renderer.render(scene, camera);
}
render();

// Currently, we re-render on the controls 'change' event and on window resize. 
// This is appropriate. However, I also want to implement an onChange hook in
// VoxelWorld so that when Timeline sends opsets to VoxelWorld, it can detect
// whether there were changes and make the appropriate render.
controls.addEventListener('change', () => {
  const x = Math.round(controls.target.x);
  const y = Math.round(controls.target.y);
  const z = Math.round(controls.target.z);
  document.querySelector("#position").innerText = `(${x}, ${y}, ${z})`;
  render();
});
window.addEventListener('resize', render);

// Just for debugging
window.controls = controls;
window.camera = camera;
window.scene = scene;
window.world = world;
