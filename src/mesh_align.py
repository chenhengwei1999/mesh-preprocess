import trimesh
import os

import math
import yaml
import argparse

from logging_output import logger

def rotate_mesh(vehicle, rotate_angle, logger):
    if type(rotate_angle) == float:
        # change the rotation angle to radian
        rotate_radian = math.radians(rotate_angle)
        logger.info("Rotate the mesh by %f radian", rotate_radian)
        vehicle.apply_transform(trimesh.transformations.rotation_matrix(
            angle=rotate_radian, direction=[0, 1, 0]))
    elif type(rotate_angle) == list:
        rotate_angle_x, rotate_angle_y, rotate_angle_z = rotate_angle
        rotate_radian_x = math.radians(rotate_angle_x)
        rotate_radian_y = math.radians(rotate_angle_y)
        rotate_radian_z = math.radians(rotate_angle_z)
        logger.info("Rotate the mesh by: X-axis %f, Y-axis %f, Z-axis %f", 
                    rotate_radian_x, rotate_radian_y, rotate_radian_z)
        vehicle.apply_transform(trimesh.transformations.rotation_matrix(
            angle=rotate_radian_x, direction=[1, 0, 0]))
        vehicle.apply_transform(trimesh.transformations.rotation_matrix(
            angle=rotate_radian_y, direction=[0, 1, 0]))
        vehicle.apply_transform(trimesh.transformations.rotation_matrix(
            angle=rotate_radian_z, direction=[0, 0, 1]))
    else:
        logger.warning("Check the configuration of the rotation angle in yaml file")

def translate_mesh(vehicle, logger):
    min_bound, max_bound = vehicle.bounds

    # output the maxmimum value in X, Y, Z direction
    max_x, max_y, max_z = max_bound
    min_x, min_y, min_z = min_bound
    
    logger.info("Before translation:")
    logger.info("Max X: %f, Min X %f", max_x, min_x)
    logger.info("Max Y: %f, Min Y %f", max_y, min_y)
    logger.info("Max Z: %f, Min Z %f", max_z, min_z)

    # get the center of the bounding box, the center on the x-z plane
    center_x = (max_x + min_x) / 2
    center_z = (max_z + min_z) / 2
    center_y = (max_y + min_y) / 2

    logger.info("Coordinate of the center: (%f, %f, %f)", center_x, center_y, center_z)

    # translate the mesh
    dx = -center_x
    dy = -min_y
    dz = -center_z

    ### For debugging
    # dx = -center_x
    # dy = 0
    # dz = 20.382050
    ### Debugging ends

    vehicle.vertices += [dx, dy, dz]

    min_bound_aligned, max_bound_aligned = vehicle.bounds
    center_x_aligned = (max_bound_aligned[0] + min_bound_aligned[0]) / 2
    center_z_aligned = (max_bound_aligned[2] + min_bound_aligned[2]) / 2
    center_y_aligned = (max_bound_aligned[1] + min_bound_aligned[1]) / 2

    logger.info("After translation:")
    logger.info("Max X: %f, Min X: %f", max_bound_aligned[0], min_bound_aligned[0])
    logger.info("Max Y: %f, Min Y: %f", max_bound_aligned[1], min_bound_aligned[1])
    logger.info("Max Z: %f, Min Z: %f", max_bound_aligned[2], min_bound_aligned[2])
    logger.info("Center: (%f, %f, %f)", center_x_aligned, center_y_aligned, center_z_aligned)

    logger.info("Height of the vehicle: %f m", (max_bound_aligned[1] - min_bound_aligned[1]) / 10)
    logger.info("Width of the vehicle: %f m", (max_bound_aligned[0] - min_bound_aligned[0]) / 10)
    logger.info("Length of the vehicle: %f m", (max_bound_aligned[2] - min_bound_aligned[2]) / 10)



def parse_args():
    parser = argparse.ArgumentParser(description="Batch Mesh Align")
    parser.add_argument("--yaml_path", type=str, default="./params/mesh_align_params.yaml", help="The path of the yaml file")
    parser.add_argument("--vehicle_meshes_root_dir", type=str,
                        default="/home/chw/Downloads/vehicle_models",
                        help="The root directory of the vehicle meshes")
    parser.add_argument("--vehicle_yaml_name", type=str, default="VEHICLE_1",
                        help="The name of vehicle mesh in yaml file")
    parser.add_argument("--suffix", type=str, default=".obj", help="The suffix of the mesh file")
    args = parser.parse_args()
    return args

def load_yaml_file(yaml_path):
    with open(yaml_path, "r") as file:
        yaml_file = yaml.safe_load(file)
    return yaml_file

def main():
    # 0. Load the hyperparameters

    args = parse_args()

    vehicle_meshes_root_dir = args.vehicle_meshes_root_dir

    yaml_path = args.yaml_path
    yaml_file = load_yaml_file(yaml_path)

    vehicle_yaml_name = args.vehicle_yaml_name

    vehicle_mesh_sub_root_dir = yaml_file[vehicle_yaml_name]["subfolder"]
    vehicle_mesh_name = yaml_file[vehicle_yaml_name]["name"]

    file_suffix = args.suffix
    
    # 1. Load the mesh
    vehicle_mesh_file = os.path.join(vehicle_meshes_root_dir, vehicle_mesh_sub_root_dir, 
                             vehicle_mesh_name + file_suffix)
    scene_mesh = trimesh.load(vehicle_mesh_file) # Scene class or Trimesh class

    logger.info("Type of the scene_mesh: %s", type(scene_mesh))

    vehicle = trimesh.Trimesh()

    if type(scene_mesh) == trimesh.scene.scene.Scene:
        logger.warning("Obtaining many meshes from the scene. Needs to be attached to a single mesh.")
        for mesh in scene_mesh.geometry.values():
            # attach all the meshes to a single mesh
            vehicle += mesh
    elif type(scene_mesh) == trimesh.Trimesh:
        vehicle = scene_mesh

    logger.info("Number of vertices: %d", len(vehicle.vertices))

    vertices = vehicle.vertices
    faces = vehicle.faces

    num_vertices_before = len(vertices)
    logger.info("Before scaling: %d", num_vertices_before)
    logger.info("Vertice example: \t%s", vertices[0:3])

    # 2. Scale the mesh
    # judge whether the mesh needs to be scaled
    if yaml_file[vehicle_yaml_name]["scale"]:
        logger.warning("Scaling the mesh")
        scale_factor = yaml_file[vehicle_yaml_name]["scale_factor"]
        vehicle.vertices *= scale_factor
    else:
        logger.warning("No scaling is needed")

    logger.info("After scaling: %d", len(vehicle.vertices))
    logger.info("Vertice example: %s", vehicle.vertices[0:3])

    # 3. Rotate the mesh
    # judge whether the mesh needs to be rotated
    rotate_angle = yaml_file[vehicle_yaml_name]["rotate_angle"]
    if rotate_angle and type(rotate_angle) == float:
        logger.warning("Rotating the mesh with %f degree", rotate_angle)
        rotate_mesh(vehicle, rotate_angle, logger)
    elif rotate_angle and type(rotate_angle) == list:
        logger.warning("Rotating the mesh with: X-axis %f, Y-axis %f, Z-axis %f", 
                       rotate_angle[0], rotate_angle[1], rotate_angle[2])
        rotate_mesh(vehicle, rotate_angle, logger)
    else:
        logger.warning("No rotation is needed")
    
    # 4. Translate the mesh
    translate_mesh(vehicle, logger)

    # 5. Save the mesh
    output_mesh_file = os.path.join(vehicle_meshes_root_dir, vehicle_mesh_sub_root_dir, 
                                vehicle_mesh_name + "_aligned" + file_suffix)
    vehicle.export(output_mesh_file)
    logger.info("Mesh saved to: %s", output_mesh_file)

    # 6. Visualize the mesh
    scene = trimesh.Scene()
    scene.add_geometry(vehicle)

    ### For debugging
    # logger.info("Minumum of Z is : %f", min(vehicle.vertices[:, 2]))
    ### Debugging ends

    # 计算 vehicle 的边界框
    # 计算 vehicle 的边界框
    min_bound, max_bound = vehicle.bounds
    bbox_center = (max_bound + min_bound) / 2
    bbox_extents = max_bound - min_bound
    bbox_mesh = trimesh.creation.box(extents=bbox_extents, 
                                      transform=trimesh.transformations.translation_matrix(bbox_center))
    scene.add_geometry(bbox_mesh)

    scene.show()



if __name__ == "__main__":
    main()
    