import trimesh
import numpy as np
from shapely.geometry import Polygon

def build_clip_stl():
    # Dimensions (mm)
    shelf_th = 18.0
    clip_gap = 18.2       # clearance at inner base
    prong_len = 28.0      # reach onto shelf
    wall_th = 3.0         # top and bottom wall thickness
    front_th = 3.5        # front mounting plate thickness
    clip_w = 22.0         # width of clip
    
    # 5mm Wood Screw replacement stud
    shank_dia = 4.8       # 4.8 mm shank
    shank_len = 3.2       # 3.2 mm neck clearance for clock backplate
    head_dia = 8.5        # 8.5 mm screw head
    head_len = 2.2        # head thickness
    
    half_gap = clip_gap / 2.0        # 9.1 mm
    half_outer = half_gap + wall_th  # 12.1 mm
    
    # 2D cross-section points in (Y, Z):
    # Shelf front face is at Y = 0. Shelf is in -Y direction (-28 to 0).
    # Front plate extends in +Y direction (0 to front_th = 3.5).
    # Prongs extend in -Y direction (-prong_len to 0).
    pts_yz = [
        (-prong_len, half_outer - 0.8),          # Top outer tip rounded bevel
        (-prong_len + 1.2, half_outer),          # Top outer flat
        (front_th, half_outer),                  # Front top corner
        (front_th, -half_outer),                 # Front bottom corner
        (-prong_len + 1.2, -half_outer),         # Bottom outer flat
        (-prong_len, -half_outer + 0.8),         # Bottom outer tip bevel
        (-prong_len, -half_gap - 1.2),           # Bottom inner lead-in chamfer
        (-prong_len + 3.0, -half_gap + 0.35),    # Bottom positive retention clamp bump
        (0.0, -half_gap),                        # Inner bottom front corner
        (0.0, half_gap),                         # Inner top front corner
        (-prong_len + 3.0, half_gap - 0.35),     # Top positive retention clamp bump
        (-prong_len, half_gap + 1.2)             # Top inner lead-in chamfer
    ]
    
    poly = Polygon(pts_yz)
    clip_mesh = trimesh.creation.extrude_polygon(poly, height=clip_w)
    
    # Center along X:
    clip_mesh.vertices[:, [0, 1, 2]] = clip_mesh.vertices[:, [2, 0, 1]]
    clip_mesh.vertices[:, 0] -= clip_w / 2.0
    
    # Add Screw Stud on front plate (centered at X=0, Z=0, projecting from Y=front_th)
    rot_y = trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0])
    rot_cone = trimesh.transformations.rotation_matrix(-np.pi / 2, [1, 0, 0])
    
    # 1. Base reinforcement collar / fillet (tapered cone)
    collar = trimesh.creation.cone(radius=shank_dia / 2.0 + 1.5, height=1.4)
    collar.apply_transform(rot_cone)
    collar.vertices += [0, front_th + 0.7, 0]
    
    # 2. Screw Shank (diameter 4.8 mm, length 3.2 mm)
    shank = trimesh.creation.cylinder(radius=shank_dia / 2.0, height=shank_len)
    shank.apply_transform(rot_y)
    shank.vertices += [0, front_th + shank_len / 2.0, 0]
    
    # 3. Screw Head (diameter 8.5 mm, thickness 2.2 mm)
    head = trimesh.creation.cylinder(radius=head_dia / 2.0, height=head_len)
    head.apply_transform(rot_y)
    head.vertices += [0, front_th + shank_len + head_len / 2.0, 0]
    
    # 4. Lead-in chamfer on screw head tip
    tip_chamfer = trimesh.creation.cone(radius=head_dia / 2.0, height=1.2)
    tip_chamfer.apply_transform(rot_cone)
    tip_chamfer.vertices += [0, front_th + shank_len + head_len + 0.6, 0]
    
    full_clip = trimesh.util.concatenate([clip_mesh, collar, shank, head, tip_chamfer])
    
    out_dir = "c:/Users/root/Downloads/Fusion360-MCP"
    stl_path = f"{out_dir}/IKEA_BONDTOLVAN_18mm_Shelf_Clip.stl"
    full_clip.export(stl_path)
    print("Exported STL:", stl_path)
    print("Dimensions (X=Width, Y=Depth, Z=Height):", full_clip.extents)
    return full_clip

if __name__ == "__main__":
    build_clip_stl()
