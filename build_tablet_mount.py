import trimesh
import numpy as np
from shapely.geometry import Polygon
import os

def build_tablet_clip():
    # =========================================================================
    # PARAMETRIC DIMENSIONS (in mm)
    # =========================================================================
    shelf_th = 18.0         # 18 mm shelf
    clip_gap = 18.2         # 0.2 mm clearance for snug friction fit
    prong_len = 28.0        # reach onto shelf
    wall_th = 3.2           # clamp wall thickness
    clip_w = 24.0           # width of clip (sturdy lateral support)
    
    # Tablet specs (Nvidia Shield Tablet K1)
    # Dimensions: 221 mm (W) x 126 mm (H) x 9.2 mm (T)
    tablet_th = 9.5         # 9.5 mm nominal thickness
    slot_th = 10.4          # 10.4 mm slot width (0.9 mm clearance for easy slide-in/out)
    cradle_lip_h = 10.0     # 10 mm front retaining lip (covers bezel, clears screen)
    cradle_lip_th = 3.0     # front lip thickness
    tilt_deg = 10.0         # 10 degree backward tilt for comfortable viewing
    tilt_rad = np.radians(tilt_deg)
    
    # Shelf clamp profile in (Y, Z):
    # Front of shelf is at Y = 0. Shelf is in -Y direction (-28 to 0).
    # Z = 0 is shelf center line. Shelf is from Z = -9 to +9 mm.
    half_gap = clip_gap / 2.0        # 9.1 mm
    half_outer = half_gap + wall_th  # 12.3 mm
    front_bridge_th = 3.5            # 3.5 mm front plate
    
    # Let's design the unified 2D profile on (Y, Z) plane:
    # 1. Shelf clamp (U-channel from Y = -prong_len to Y = front_bridge_th)
    # 2. Cradle section attached to the bottom-front:
    #    The tablet cradle drops slightly below the shelf (Z <= -half_outer)
    #    or sits right at the bottom front corner, tilted back by 10°.
    
    # Cradle floor:
    # Starts at Y = front_bridge_th, Z = -half_outer (bottom front of shelf clamp)
    # Extends forward with a 10° tilt.
    # Normal to tablet back is (sin(tilt), cos(tilt))
    # Tablet rests against the back rest plane.
    # Floor of cradle is perpendicular to tablet back (angled down by 10° forward)
    # Let's calculate the exact polygon coordinates:
    
    # Clamp upper prong:
    p_clamp_top_tip = (-prong_len, half_outer)
    p_clamp_top_front = (front_bridge_th, half_outer)
    p_clamp_back_wall = (front_bridge_th, -half_gap)
    
    # Inner clamp contour:
    p_inner_top = (0.0, half_gap)
    p_inner_top_bump = (-prong_len + 3.0, half_gap - 0.35)
    p_inner_top_lead = (-prong_len, half_gap + 1.2)
    
    p_inner_bot_lead = (-prong_len, -half_gap - 1.2)
    p_inner_bot_bump = (-prong_len + 3.0, -half_gap + 0.35)
    p_inner_bot = (0.0, -half_gap)
    
    # Clamp bottom prong:
    p_clamp_bot_tip = (-prong_len, -half_outer)
    
    # Cradle geometry:
    # Bottom of clamp is at Z = -half_outer = -12.3 mm.
    # Cradle drops down to Z = -16.0 mm (base thickness 3.5 mm).
    # Cradle floor extends forward from Y = front_bridge_th:
    cradle_base_z = -half_outer - 3.5 # -15.8 mm
    
    # Back rest of tablet is at Y = front_bridge_th, tilted at 10 deg:
    # At cradle floor (Z = cradle_base_z + 3.2 = -12.6 mm): Y = front_bridge_th
    # Tablet sits against this surface.
    # Floor of slot extends forward by slot_th = 10.4 mm along the tilted normal:
    # Floor direction: dx = cos(10°), dz = -sin(10°)
    cos_t = np.cos(tilt_rad)
    sin_t = np.sin(tilt_rad)
    
    y0_floor = front_bridge_th
    z0_floor = -half_outer
    
    # Inner corner of slot:
    # Bottom floor of slot extends forward:
    floor_vec = np.array([cos_t, -sin_t]) * slot_th # length 10.4 mm
    y1_floor = y0_floor + floor_vec[0]
    z1_floor = z0_floor + floor_vec[1]
    
    # Front lip goes UP parallel to tablet back (direction: sin_t, cos_t):
    lip_vec = np.array([-sin_t, cos_t]) * cradle_lip_h # height 10.0 mm
    y2_lip = y1_floor + lip_vec[0]
    z2_lip = z1_floor + lip_vec[1]
    
    # Lip top chamfer / outer face:
    lip_th_vec = np.array([cos_t, -sin_t]) * cradle_lip_th
    y3_lip_out = y2_lip + lip_th_vec[0]
    z3_lip_out = z2_lip + lip_th_vec[1]
    
    # Lip bottom outer corner:
    y4_cradle_bot = y1_floor + lip_th_vec[0] - lip_vec[0] * 0.4
    z4_cradle_bot = z1_floor + lip_th_vec[1] - lip_vec[1] * 0.4
    
    # Underside of cradle connects smoothly back to bottom prong:
    y5_cradle_heel = front_bridge_th
    z5_cradle_heel = cradle_base_z
    
    # Assemble full 2D perimeter:
    poly_pts = [
        # 1. Top prong outer
        (-prong_len, half_outer - 0.8),
        (-prong_len + 1.2, half_outer),
        (front_bridge_th, half_outer),
        # 2. Back rest of tablet (tilted at 10°)
        (front_bridge_th + 0.8, (half_outer + z0_floor) / 2.0),
        (y0_floor, z0_floor),
        # 3. Cradle slot floor
        (y1_floor, z1_floor),
        # 4. Front retaining lip (inside face)
        (y2_lip, z2_lip),
        # 5. Lip top round/chamfer
        (y2_lip + lip_th_vec[0]*0.5, z2_lip + lip_th_vec[1]*0.5 + 0.8),
        (y3_lip_out, z3_lip_out),
        # 6. Cradle outer bottom
        (y4_cradle_bot, z4_cradle_bot),
        (y5_cradle_heel + 2.0, z5_cradle_heel),
        (-prong_len + 1.2, -half_outer),
        (-prong_len, -half_outer + 0.8),
        # 7. Bottom prong inner contour
        (-prong_len, -half_gap - 1.2),
        (p_inner_bot_bump[0], p_inner_bot_bump[1]),
        (0.0, -half_gap),
        # 8. Shelf front face stop
        (0.0, half_gap),
        # 9. Top prong inner contour
        (p_inner_top_bump[0], p_inner_top_bump[1]),
        (-prong_len, half_gap + 1.2)
    ]
    
    poly = Polygon(poly_pts)
    clip_mesh = trimesh.creation.extrude_polygon(poly, height=clip_w)
    
    # Center along X:
    clip_mesh.vertices[:, [0, 1, 2]] = clip_mesh.vertices[:, [2, 0, 1]]
    clip_mesh.vertices[:, 0] -= clip_w / 2.0
    
    out_dir = "c:/Users/root/Downloads/Fusion360-MCP"
    stl_path = os.path.join(out_dir, "NVIDIA_Shield_K1_18mm_Shelf_Mount.stl")
    clip_mesh.export(stl_path)
    print("Exported STL:", stl_path)
    print("Dimensions (Width X, Depth Y, Height Z):", clip_mesh.extents)
    print("Volume per clip:", clip_mesh.volume / 1000.0, "cm3")
    print(f"Weight per clip (~15% infill, 3 walls): ~{clip_mesh.volume / 1000.0 * 1.24 * 0.45:.1f} g")
    return clip_mesh

if __name__ == "__main__":
    build_tablet_clip()
