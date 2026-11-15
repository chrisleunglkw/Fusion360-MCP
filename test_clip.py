import trimesh
import numpy as np

def create_shelf_clip():
    # Dimensions (mm)
    shelf_th = 18.0       # 18 mm shelf
    clip_gap = 18.2       # 0.2 mm clearance for snug fit
    prong_len = 28.0      # reach onto shelf
    wall_th = 3.0         # wall thickness of clip
    clip_w = 22.0         # width of clip
    
    # 5mm Wood Screw replacement stud
    shank_dia = 4.8       # 4.8 mm shank (fits 5.0mm-5.5mm keyhole slot)
    shank_len = 3.5       # standoff gap for clock backplate
    head_dia = 8.5        # 8.5 mm screw head (fits keyhole entry hole, locks in slot)
    head_len = 2.2        # head thickness
    
    # Let's create the U-clip body by extrusion of 2D profile
    # Profile in YZ plane:
    # Outer bounds: Y from -prong_len to 0, Z from -(wall_th + clip_gap/2) to +(wall_th + clip_gap/2)
    # Inner slot: Y from -prong_len to -wall_th (or front face at Y=0, inner slot from -prong_len to 0)
    # Let's align:
    # Front face of shelf is at Y = 0.
    # Shelf extends in -Y from 0 to -prong_len, Z from -9 to +9 mm.
    # Clip front wall: Y from 0 to +wall_th (from 0 to 3.5 mm)
    # Clip top prong: Z from +9.1 to +12.1 mm, Y from -prong_len to 0
    # Clip bottom prong: Z from -12.1 to -9.1 mm, Y from -prong_len to 0
    # Screw stud projects forward in +Y from the front wall (Y = 3.5 to Y = 3.5 + shank_len + head_len)
    
    # Let's build via 2D polygon extrusion along X (width = clip_w)
    half_gap = clip_gap / 2.0 # 9.1 mm
    half_outer_z = half_gap + wall_th # 12.1 mm
    front_th = 3.5
    
    # 2D cross-section points in (Y, Z):
    # Start at top prong tip, outer surface
    pts_yz = [
        (-prong_len, half_outer_z),             # Top prong tip top
        (front_th, half_outer_z),               # Front top outer corner
        (front_th, -half_outer_z),              # Front bottom outer corner
        (-prong_len, -half_outer_z),            # Bottom prong tip bottom
        (-prong_len, -half_gap),                # Bottom prong tip inner
        (-prong_len + 3.0, -half_gap + 0.4),    # Bottom clamping bump
        (0.0, -half_gap),                       # Inner bottom front corner
        (0.0, half_gap),                        # Inner top front corner
        (-prong_len + 3.0, half_gap - 0.4),     # Top clamping bump
        (-prong_len, half_gap)                  # Top prong tip inner
    ]
    
    # 2D Polygon
    from shapely.geometry import Polygon
    poly = Polygon(pts_yz)
    
    # Extrude along X by clip_w (centered from -clip_w/2 to +clip_w/2)
    clip_body = trimesh.creation.extrude_polygon(poly, height=clip_w)
    # Centered on X:
    clip_body.vertices[:, [0, 1, 2]] = clip_body.vertices[:, [2, 0, 1]] # map (Z_extrude, Y, Z) to (X, Y, Z)
    clip_body.vertices[:, 0] -= clip_w / 2.0
    
    # Add the Screw Stud on the front face (centered at X=0, Z=0, projecting from Y=front_th)
    # Shank
    shank = trimesh.creation.cylinder(radius=shank_dia / 2.0, height=shank_len)
    # Cylinder default axis is Z. Rotate so axis is +Y
    rot_y = trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0])
    shank.apply_transform(rot_y)
    shank.vertices += [0, front_th + shank_len / 2.0, 0]
    
    # Screw Head
    head = trimesh.creation.cylinder(radius=head_dia / 2.0, height=head_len)
    head.apply_transform(rot_y)
    head.vertices += [0, front_th + shank_len + head_len / 2.0, 0]
    
    # Chamfered lead-in cone on screw head
    cone = trimesh.creation.cone(radius=head_dia / 2.0, height=1.2)
    rot_cone = trimesh.transformations.rotation_matrix(-np.pi / 2, [1, 0, 0])
    cone.apply_transform(rot_cone)
    cone.vertices += [0, front_th + shank_len + head_len + 0.6, 0]
    
    # Fillet / Reinforcement Collar at shank base (radius 3.5mm, height 1.2mm cone)
    collar = trimesh.creation.cone(radius=shank_dia/2.0 + 1.6, height=1.5)
    collar.apply_transform(rot_cone)
    collar.vertices += [0, front_th + 0.75, 0]

    # Combine all parts
    full_clip = trimesh.util.concatenate([clip_body, collar, shank, head, cone])
    
    # Export
    out_stl = "c:/Users/root/Downloads/Fusion360-MCP/IKEA_BONDTOLVAN_18mm_Shelf_Clip.stl"
    full_clip.export(out_stl)
    print("Exported STL:", out_stl)
    print("Bounds:", full_clip.bounds)
    print("Extents:", full_clip.extents)

if __name__ == "__main__":
    create_shelf_clip()
