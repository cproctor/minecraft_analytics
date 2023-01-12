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
import { OrbitControls } from "./OrbitControls.js";
import add_geometry_to_scene from "./study_geometry.js";
import add_cube_geometry_to_scene from "./study_cubes.js";
import add_sample_geometry_to_scene from "./sample_geometry.js";
import VoxelWorld from "./voxel_world.js";

const canvas = document.querySelector("#simulation");
const renderer = new WebGLRenderer({canvas});

const world = new VoxelWorld(
    window.DATA.layers.base.start, 
    window.DATA.layers.base.palette,
    window.DATA.params.bounding_box
)
window.world = world;

const fov = 75;
const aspect = 2;  // the canvas default
const near = 0.1;
const far = 1000; // TODO respect bounding box
const camera = new PerspectiveCamera(fov, aspect, near, far);
camera.position.set(...world.get_initial_camera_position());

const controls = new OrbitControls(camera, canvas);
controls.target.set(...world.get_initial_controls_target());
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
addLight( 1, -1, -2);

//add_geometry_to_scene(scene)
//add_sample_geometry_to_scene(scene)
//add_cube_geometry_to_scene(scene)

world.add_geometry(scene);

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

controls.addEventListener('change', render);
window.addEventListener('resize', render);

window.controls = controls;
window.camera = camera;
window.scene = scene;

console.log(window.DATA);


