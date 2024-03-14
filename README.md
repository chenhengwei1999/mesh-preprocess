# Mesh Preprocess with Convenient Interface

This is a tool with convenient interface to align mesh to specified coordinate system, handling displacement transformations and dimensional conversion.

## Enviornment Setup

Create a conda virtual env is recommended. And download some packages which are required.

```bash
git clone https://github.com/chenhengwei1999/mesh-preprocess.git
cd mesh-preprocess
pip install -r requirements.txt
```

## Usage Guide

### Mesh Alignment

Until now, this repo implemented alignment function for mesh translation, mesh rotation, and mesh dimensional conversion.

Firstly, check the parameters that can be used.

```bash
python src/mesh_align.py --help
```

The terminal will output the following information.

```bash
usage: mesh_align.py [-h] [--yaml_path YAML_PATH] [--vehicle_meshes_root_dir VEHICLE_MESHES_ROOT_DIR] [--vehicle_yaml_name VEHICLE_YAML_NAME] [--suffix SUFFIX]

Batch Mesh Align

optional arguments:
  -h, --help            show this help message and exit
  --yaml_path YAML_PATH
                        The path of the yaml file
  --vehicle_meshes_root_dir VEHICLE_MESHES_ROOT_DIR
                        The root directory of the vehicle meshes
  --vehicle_yaml_name VEHICLE_YAML_NAME
                        The name of vehicle mesh in yaml file
  --suffix SUFFIX       The suffix of the mesh file
```

- `yaml_path`: The path of the yaml file. This file contains information on how all meshes need to be processed, such as rotation angle, size scaling ratio, sub folder name, etc.

- `vehicle_meshes_root_dir`: The root directory of the vehicle meshes.

- `vehicle_yaml_name`: The name of the vehicle mesh when reading from the yaml file is only used to distinguish different meshes.

- `suffix`: The suffix for mesh files currently only supports **.obj** format files.

### Code Tutorial

Assuming you have many vehicle meshes saved in folder `~/Documents/mesh-preprocess`, there are many meshes under this **root directory**, and the directory structure refers to the following tree structure:

```bash
# ~/Documents/mesh-preprocess
.
├── ford-mustang
│   └── mustang.obj
├── sport_car_3.obj
└── sport_car.obj
```

There are two things you need to do. Firstly, you need to define the parameters for processing the mesh in `params/mesh_align_params.yaml`, such as:

```yaml
VEHICLE_3:
  subfolder: "25-ford-mustang"
  name: "mustang"
  # whether needs to be rotated, angles (not radian)
  rotate_angle: [0.0, 0.0, 90.0]
  # whether needs to be scaled
  scale: false
  scale_factor: 0.1
```

Among them, `subfolder` corresponds to the sub root directory name of the corresponding mesh, `name` refers to the file name, `rotate_angle` is a list containing 3 floating-point numbers, `scale` represents whether to scale, and `scale_factor` is the corresponding scaling ratio.

Secondly, adjust `rotate_angle` based on the visualized results with ``trimesh``, and then adjust `scale_factor` based on the output of the terminal (colored logs).

Here is a simple example of terminal usage.

```bash
cd mesh-preprocess/
python src/mesh_align.py --vehicle_yaml VEHICLE_1
```

*Tip: In the visualization interface, the following keyboard buttons can be used to switch display effects.*


- `mouse click + drag` rotates the view

- `ctl + mouse click + drag` pans the view

- `mouse wheel` zooms

- `z` returns to the base view

- `w` toggles wireframe mode

- `c` toggles backface culling

- `g` toggles an XY grid with Z set to lowest point

- `a` toggles an XYZ-RGB axis marker between: off, at world frame, or at every frame and world, and at every frame

- `f` toggles between fullscreen and windowed mode

- `m` maximizes the window

- `q` closes the window

Finally, the aligned file will be saved in the root directory corresponding to the mesh file.

## Reference

- [Trimesh Documentation](https://trimesh.org/index.html)