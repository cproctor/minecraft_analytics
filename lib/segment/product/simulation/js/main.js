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
    window.DATA.params.bounding_box,
    window.DATA.layers.base.ops
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
addLight(...world.getLightPosition());
scene.add(new AmbientLight(0xDDDDFF, 0.5));

world.createBaseGeometry()
scene.add(world.geometryLayers['base'])
if (window.DATA.layers.water) {
    world.createWaterGeometry()
    scene.add(world.geometryLayers['water'])
}

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

// TESTING. This should go into the timeline.
function get_opset_for_timespan(a, b) {
  const opset = [];
  if (a <= b) {
    for (var i = a; i < b; i++) {
      for (const op of window.DATA.layers.base.ops[i]) {
        opset.push(op);
      }
    }
  }
  else {
    for (var i = a-1; i >= b; i--) {
      for (const op of window.DATA.layers.base.ops[i]) {
        opset.push(reverse_op(op));
      }
    }
  }
  return opset
}

function reverse_opset(opset) {
  const reversed = [];
  for (var i = opset.length - 1; i >= 0; i--) {
    reversed.append(reverse_op(opset[i]));
  }
  return reversed;
}

function reverse_op(op) {
  const [layer, loc, before, after] = op;
  return [layer, loc, after, before];
}

window.time = 0;
window.goto_time = function(t) {
  if (t < 0) t = 0;
  if (t >= window.DATA.layers.base.ops.length) 
    t = window.DATA.layers.base.ops.length - 1;
  const opset = get_opset_for_timespan(window.time, t);
  console.log(`Moving from time ${window.time} to ${t}.`);
  window.time = t;
  window.world.updateBaseGeometry(opset);
  render();
}

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
