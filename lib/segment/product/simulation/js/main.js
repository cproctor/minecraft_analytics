'use strict';

import { Vector3 } from "three";
import Simulation from "./simulation.js";
import { Layer } from "./layers.js";
import Op from "./op.js";

const [[x0, x1], [y0, y1], [z0, z1]] = window.DATA.params.bounding_box;
const bb0 = new Vector3(x0, y0, z0);
const bb1 = new Vector3(x1, y1, z1);

const layers = new Map();
for (const key in window.DATA.layers) {
  const layer = window.DATA.layers[key];
  layers.set(key, Layer.create(layer.type, layer.initial, bb0, bb1, layer.ops));
}

window.sim = new Simulation("#simulation", layers, bb0, bb1);
window.sim.render()

//import { createApp } from "vue";
//import Timeline from "./vue/timeline.vue";
//const app = createApp(Timeline);
//app.mount('#timeline');

// TEMP
window.speed = 15;
window.go = function() {
  const playstart = new Date();
  const start = Date.parse(window.DATA.params.timespan[0]);
  const end = Date.parse(window.DATA.params.timespan[1]);

  function getRelativeTime() {
    const now = new Date();
    const elapsed = (now - playstart) * window.speed;
    const simspan = end - start;
    const elapsedRatio = Math.min(1, elapsed / simspan);
    return new Date(start + elapsedRatio * simspan);
  }

  const animate = function() {
    requestAnimationFrame(animate);
    const rt = getRelativeTime();
    window.sim.seek(rt);
  }
  animate()
}

go();
