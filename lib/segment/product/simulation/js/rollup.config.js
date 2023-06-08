import replace from '@rollup/plugin-replace'
import json from '@rollup/plugin-json';
import { nodeResolve } from '@rollup/plugin-node-resolve';
import postcss from 'rollup-plugin-postcss';
import vue from 'rollup-plugin-vue'

export default {
  input: 'main.js',
  output: {
    file: 'bundle.js',
    format: 'iife',
  },
  plugins: [
    replace({
      preventAssignment: true,
      "process.browser": true,
      "process.env.NODE_ENV": true,
      "__VUE_OPTIONS_API__": true,
      "__VUE_PROD_DEVTOOLS__": false
    }),
    json(), 
    nodeResolve(),
    vue({preprocessStyles: true}),
    postcss()
  ]
};

