'use strict';

import { Vector3 } from "three";
import Simulation from "./simulation.js";
import { Layer } from "./layers.js";
import Op from "./op.js";

const layers = new Map();
for (const key in window.DATA.layers) {
  const layer = window.DATA.layers[key];
  const ops = [];
  for (const opData of layer.ops) {
    ops.push(new Op(...opData));
  }
  layers.set(key, Layer.create(layer.type, layer.initial, ops));
}

const [[x0, x1], [y0, y1], z0, z1] = window.DATA.params.bounding_box;
const bb0 = new Vector3(x0, y0, z0);
const bb1 = new Vector3(x1, y1, z1);
window.sim = new Simulation("#simulation", layers, bb0, bb1);
window.sim.render()

//import { createApp } from "vue";
//import Timeline from "./vue/timeline.vue";
//const app = createApp(Timeline);
//app.mount('#timeline');

