# Process notes

## Calculating voxel faces

We can optimize rendering by merging geometry. Adjacent voxels
don't need the faces which touch each other. The table below 
shows the average faces per voxel as we read more of the dataset.

rows read | voxels | faces per voxel |
--------- | ------ | --------------- |
10000     |   2974 | 4.92            |
100000    |  20459 | 4.21            |
1000000   | 150381 | 3.72            |
