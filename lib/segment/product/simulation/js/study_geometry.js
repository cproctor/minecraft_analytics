import {
    BufferGeometry,
    MeshLambertMaterial,
    BufferAttribute,
    Mesh
} from "three";

function triangle_indices(base) {
    return [base, base + 1, base + 2, base + 2, base + 1, base + 3]
}

export default function add_geometry_to_scene(scene) {
  const positions = [];
  const normals = [];
  const indices = [];

  for (const voxelId in window.DATA["faces"]) {
      const faces = window.DATA["faces"][voxelId];
      for (const face of faces) {
          for (const corner of face) {
              const index = positions.length / 3;
              positions.push(...corner.position);
              normals.push(...corner.normal);
              indices.push(...triangle_indices(index));
          }
      }
  }
    
  const geometry = new BufferGeometry();
  geometry.setAttribute('position', new BufferAttribute(new Float32Array(positions), 3));
  geometry.setAttribute('normal', new BufferAttribute(new Float32Array(normals), 3));
  geometry.setIndex(indices);

  const material = new MeshLambertMaterial({color: 'green'});
  const mesh = new Mesh(geometry, material);
  scene.add(mesh);
}
