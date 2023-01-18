'use strict';

import { Vector3 } from "three";

export default class Voxel {
  static faces = [
    {
      uvRow: 0,
      dir: new Vector3(-1, 0, 0),
      corners: [
        {pos: new Vector3(0, 1, 0), uv: [0, 1]},
        {pos: new Vector3(0, 0, 0), uv: [0, 0]},
        {pos: new Vector3(0, 1, 1), uv: [1, 1]},
        {pos: new Vector3(0, 0, 1), uv: [1, 0]},
      ],
    },
    {
      uvRow: 0,
      dir: new Vector3(1, 0, 0),
      corners: [
        {pos: new Vector3(1, 1, 1), uv: [ 0, 1 ]},
        {pos: new Vector3(1, 0, 1), uv: [ 0, 0 ]},
        {pos: new Vector3(1, 1, 0), uv: [ 1, 1 ]},
        {pos: new Vector3(1, 0, 0), uv: [ 1, 0 ]},
      ],
    },
    {
      uvRow: 1,
      dir: new Vector3(0, -1, 0),
      corners: [
        {pos: new Vector3(1, 0, 1), uv: [ 1, 0 ]},
        {pos: new Vector3(0, 0, 1), uv: [ 0, 0 ]},
        {pos: new Vector3(1, 0, 0), uv: [ 1, 1 ]},
        {pos: new Vector3(0, 0, 0), uv: [ 0, 1 ]},
      ]
    },
    {
      uvRow: 2,
      dir: new Vector3(0, 1, 0),
      corners: [
        {pos: new Vector3(0, 1, 1), uv: [ 1, 1 ]},
        {pos: new Vector3(1, 1, 1), uv: [ 0, 1 ]},
        {pos: new Vector3(0, 1, 0), uv: [ 1, 0 ]},
        {pos: new Vector3(1, 1, 0), uv: [ 0, 0 ]},
      ],
    },
    {
      uvRow: 0,
      dir: new Vector3(0, 0, -1),
      corners: [
        {pos: new Vector3(1, 0, 0), uv: [ 0, 0 ]},
        {pos: new Vector3(0, 0, 0), uv: [ 1, 0 ]},
        {pos: new Vector3(1, 1, 0), uv: [ 0, 1 ]},
        {pos: new Vector3(0, 1, 0), uv: [ 1, 1 ]},
      ],
    },
    {
      uvRow: 0,
      dir: new Vector3(0, 0, 1),
      corners: [
        {pos: new Vector3(0, 0, 1), uv: [ 0, 0 ]},
        {pos: new Vector3(1, 0, 1), uv: [ 1, 0 ]},
        {pos: new Vector3(0, 1, 1), uv: [ 0, 1 ]},
        {pos: new Vector3(1, 1, 1), uv: [ 1, 1 ]},
      ],
    }
  ]
}
