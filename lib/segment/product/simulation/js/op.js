'use strict';

import {
  Vector3
} from "three";

export default class Op {
  constructor(ts, loc, before, after) {
    this.ts = ts;
    this.loc = loc instanceof Vector3 ? loc : new Vector3(...loc);
    this.before = before;
    this.after = after;
  }

  reversed() {
    return new Op(this.ts, this.loc, this.after, this.before);
  }
}
