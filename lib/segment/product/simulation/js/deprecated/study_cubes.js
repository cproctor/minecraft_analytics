import {
    BoxGeometry,
    MeshPhongMaterial,
    Mesh
} from "three";

export default function add_geometry_to_scene(scene) {
  const cube_geometry = new BoxGeometry(1, 1, 1);

  function makeInstance(geometry, color, x, y, z) {
    const material = new MeshPhongMaterial({color});
    const cube = new Mesh(geometry, material);
    scene.add(cube);
    cube.position.x = x;
    cube.position.y = y;
    cube.position.z = z;
    return cube;
  }

  for (const voxelId in window.DATA["voxels"]) {
      const [x, y, z] = window.DATA["voxels"][voxelId];
      makeInstance(cube_geometry, "green", x, y, z)
  }
}

