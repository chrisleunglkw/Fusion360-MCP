import trimesh
import numpy as np
from shapely.geometry import Polygon
import os

def make_chamfered_ring(r_outer, r_inner, height, bevel=1.2, sections=128):
    """Create a smooth lathe/revolved ring with refined Japanese-style beveled edges."""
    # Cross-section profile in (R, Z)
    profile = np.array([
        [r_inner + bevel * 0.5, 0.0],
        [r_outer - bevel * 0.5, 0.0],
        [r_outer, bevel * 0.5],
        [r_outer, height - bevel],
        [r_outer - bevel * 0.6, height],
        [r_inner + bevel * 0.6, height],
        [r_inner, height - bevel],
        [r_inner, bevel * 0.5],
        [r_inner + bevel * 0.5, 0.0]
    ])
    mesh = trimesh.creation.revolve(profile, sections=sections)
    return mesh

def create_japanese_minimalist_soap_drainer():
    # =========================================================================
    # PARAMETRIC DIMENSIONS (mm) - JAPANESE MINIMALIST (HAMON / ZEN RIPPLE)
    # =========================================================================
    dish_dia = 110.0           # 110 mm outer diameter
    dish_rad = dish_dia / 2.0  # 55.0 mm
    wall_th = 2.8              # Refined outer rim thickness
    inner_rad = dish_rad - wall_th # 52.2 mm
    dish_h = 10.5              # Sleek low-profile height
    
    # Zen Ripple Hollow Bottom (Concentric floating rings + 6 radial spokes)
    lattice_h = 3.4            # 3.4 mm tall delicate ribs
    rib_w = 2.2                # 2.2 mm slender rib width
    mid_ring_r_out = 32.0      # Ø64 mm middle ripple ring
    mid_ring_r_in = mid_ring_r_out - rib_w
    cen_ring_r_out = 12.0      # Ø24 mm inner ripple ring (hollow center!)
    cen_ring_r_in = cen_ring_r_out - rib_w
    
    # Hook parameters (for IKEA TISKEN corner basket front beam 7.5 - 8.0 mm)
    hook_gap = 8.5             # 8.5 mm throat clearance
    hook_w = 18.0              # Extra-slim minimalist width (18 mm)
    hook_th = 3.0              # 3.0 mm rigid structure
    hook_h = 22.0              # Vertical rise to top of rail
    hook_lip_drop = 15.0       # Retaining catch behind rail
    neck_offset = 6.0          # Standoff from basket front
    
    print("1. Creating chamfered Japanese-style outer ring...")
    outer_ring = make_chamfered_ring(dish_rad, inner_rad, dish_h, bevel=1.1, sections=128)
    
    print("2. Creating Zen water-ripple concentric hollow lattice...")
    # Middle & center floating rings with subtle top chamfer
    mid_ring = make_chamfered_ring(mid_ring_r_out, mid_ring_r_in, lattice_h, bevel=0.4, sections=96)
    cen_ring = make_chamfered_ring(cen_ring_r_out, cen_ring_r_in, lattice_h, bevel=0.4, sections=64)
    
    # 6 graceful radial spokes connecting center ring -> middle ring -> outer ring
    spokes = []
    spoke_len = (inner_rad + 1.2) - cen_ring_r_in
    spoke_center_r = cen_ring_r_in + spoke_len / 2.0
    for i in range(6):
        angle = np.deg2rad(i * 60.0 + 30.0) # 30 deg offset so no spoke clashes awkwardly
        spoke = trimesh.creation.box(extents=[spoke_len, rib_w, lattice_h])
        spoke.vertices += [spoke_center_r, 0.0, lattice_h / 2.0]
        rot = trimesh.transformations.rotation_matrix(angle, [0, 0, 1])
        spoke.apply_transform(rot)
        spokes.append(spoke)
        
    print("3. Creating refined slim hook bracket with chamfered corners...")
    y_attach = -dish_rad + 1.8             # -53.2 mm
    y_front_rail = -dish_rad - neck_offset # -61.0 mm
    y_back_rail = y_front_rail - hook_gap  # -69.5 mm
    y_lip_outer = y_back_rail - hook_th    # -72.5 mm
    
    z_dish_top = dish_h                    # 10.5 mm
    z_rail_top = z_dish_top + hook_h       # 32.5 mm
    z_hook_top = z_rail_top + hook_th      # 35.5 mm
    z_lip_end = z_rail_top - hook_lip_drop # 17.5 mm
    
    # Smooth beveled hook profile in (Y, Z)
    pts_hook = [
        (y_attach, z_dish_top - 2.2),
        (y_attach, z_dish_top - 0.5),
        (y_front_rail + hook_th, z_dish_top + 6.5),
        (y_front_rail + hook_th, z_hook_top - 1.2),
        (y_front_rail + hook_th - 1.2, z_hook_top),     # Top front bevel
        (y_lip_outer + 1.2, z_hook_top),                # Top back bevel
        (y_lip_outer, z_hook_top - 1.2),
        (y_lip_outer, z_lip_end + 2.5),
        (y_lip_outer + 1.8, z_lip_end),                 # Lead-in chamfer
        (y_back_rail, z_lip_end + 2.5),
        (y_back_rail, z_rail_top),
        (y_front_rail, z_rail_top),
        (y_front_rail, 2.8),
        (y_front_rail - 1.2, 1.4),
        (y_front_rail - 1.2, 0.0),
        (y_attach, 0.0),
        (y_attach, 2.8)
    ]
    
    poly_hook = Polygon(pts_hook)
    hook_mesh = trimesh.creation.extrude_polygon(poly_hook, height=hook_w)
    hook_mesh.vertices[:, [0, 1, 2]] = hook_mesh.vertices[:, [2, 0, 1]]
    hook_mesh.vertices[:, 0] -= hook_w / 2.0
    
    print("4. Combining all components with manifold boolean union...")
    all_parts = [outer_ring, mid_ring, cen_ring] + spokes + [hook_mesh]
    final_model = trimesh.boolean.union(all_parts)
    
    out_dir = "c:/Users/root/Downloads/Fusion360-MCP"
    stl_min = os.path.join(out_dir, "IKEA_TISKEN_Round_Soap_Drainer_110mm_Minimalist.stl")
    stl_pri = os.path.join(out_dir, "IKEA_TISKEN_Round_Soap_Drainer_110mm.stl")
    final_model.export(stl_min)
    final_model.export(stl_pri)
    
    vol_cm3 = final_model.volume / 1000.0
    print("\n=== SUCCESS: Japanese Minimalist Hollow Soap Drainer Generated ===")
    print("Exported STL:", stl_min)
    print("Dimensions [X_width, Y_depth, Z_height]:", [round(float(v), 2) for v in final_model.extents])
    print(f"Solid Volume: {vol_cm3:.1f} cm³")
    print(f"Est. 3D Print Weight (PETG / PLA @ 15% infill): ~{vol_cm3 * 1.24 * 0.45:.1f} grams")
    print(f"Watertight / Solid: {final_model.is_watertight}")
    return final_model

if __name__ == "__main__":
    create_japanese_minimalist_soap_drainer()
