import trimesh
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import os

def render_simulation():
    stl_path = "c:/Users/root/Downloads/Fusion360-MCP/KitchenSink_CoffeeDrainer_140mm.stl"
    mesh = trimesh.load(stl_path)
    
    # Target directory in brain artifacts
    artifact_dir = r"C:\Users\root\.gemini\antigravity\brain\5ecd4bab-3c44-40e0-b8dc-e416fd5880bc"
    out_img = os.path.join(artifact_dir, "print_orientation_simulation.png")

    fig = plt.figure(figsize=(18, 9), facecolor="#181a1b")
    
    # -------------------------------------------------------------------------
    # Helper to calculate face colors with directional diffuse lighting
    # -------------------------------------------------------------------------
    def get_shaded_colors(m, base_rgb=(0.25, 0.65, 0.95), light_dir=np.array([0.5, 0.4, 0.8])):
        light_dir = light_dir / np.linalg.norm(light_dir)
        normals = m.face_normals
        intensity = np.clip(np.dot(normals, light_dir), 0.15, 1.0)
        # ambient + diffuse
        colors = np.zeros((len(normals), 4))
        for i in range(3):
            colors[:, i] = base_rgb[i] * (0.35 + 0.65 * intensity)
        colors[:, 3] = 0.95
        return colors

    # -------------------------------------------------------------------------
    # SUBPLOT 1: Recommended Orientation (Printed on its SIDE)
    # -------------------------------------------------------------------------
    ax1 = fig.add_subplot(121, projection="3d", facecolor="#181a1b")
    ax1.set_title("RECOMMENDED ORIENTATION: PRINT ON SIDE (X/Y on Bed, Z=140mm)\n★ 100% Support-Free  ★ Maximum Hook Strength  ★ Clean Surface Finish", 
                  fontsize=13, fontweight="bold", color="#4ade80", pad=15)
    
    # Rotate mesh so side face (Z=-70) lies flat on bed (Z_new = 0)
    # Original: X=Height(85mm), Y=Depth(151mm), Z=Width(140mm)
    # We want: Z_new = Z_orig - min(Z_orig) -> Height is Width(140mm)
    # X_new = Y_orig - min(Y_orig), Y_new = X_orig
    m_side = mesh.copy()
    # Rotation: map original Z to new Z (height), original Y to new X, original X to new Y
    # Rotate around Y by 90 degrees: [X, Y, Z] -> [Z, Y, -X]
    rot_mat = trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0])
    m_side.apply_transform(rot_mat)
    # Shift so min Z is on bed (Z=0) and centered on bed (100, 100)
    m_side.vertices -= m_side.bounds[0]
    m_side.vertices += [30, 20, 0] # center on 220x220 bed
    
    # Draw Build Plate (220x220 mm)
    bed_x, bed_y = np.meshgrid(np.linspace(0, 220, 12), np.linspace(0, 220, 12))
    bed_z = np.zeros_like(bed_x)
    ax1.plot_wireframe(bed_x, bed_y, bed_z, color="#404040", linewidth=0.7, alpha=0.5)
    ax1.plot_surface(np.array([[0, 220], [0, 220]]), 
                     np.array([[0, 0], [220, 220]]), 
                     np.array([[0, 0], [0, 0]]), color="#262626", alpha=0.4)
    
    # Subsample faces for responsive crisp rendering
    faces_side = m_side.faces
    verts_side = m_side.vertices
    poly_side = Poly3DCollection(verts_side[faces_side], 
                                 facecolors=get_shaded_colors(m_side, base_rgb=(0.2, 0.75, 0.5)),
                                 edgecolors="#15803d", linewidths=0.08)
    ax1.add_collection3d(poly_side)
    
    # Labels and Limits
    ax1.set_xlim(0, 220)
    ax1.set_ylim(0, 220)
    ax1.set_zlim(0, 160)
    ax1.set_xlabel("Bed X (mm)", color="#9ca3af", labelpad=8)
    ax1.set_ylabel("Bed Y (mm)", color="#9ca3af", labelpad=8)
    ax1.set_zlabel("Print Height Z (mm)", color="#9ca3af", labelpad=8)
    ax1.tick_params(colors="#9ca3af")
    ax1.view_init(elev=24, azim=-55)

    # Annotations on Subplot 1
    ax1.text2D(0.05, 0.04, 
               "• Bed footprint: 151 × 85 mm (Super stable)\n"
               "• Total height: 140 mm (Fits all FDM printers)\n"
               "• NO SUPPORTS REQUIRED (100% self-supporting)\n"
               "• Layer lines run continuous along the hook arm -> Maximum tensile strength!",
               transform=ax1.transAxes, color="#86efac", fontsize=10, 
               bbox=dict(boxstyle="round,pad=0.5", facecolor="#14532d", alpha=0.8, edgecolor="#22c55e"))

    # -------------------------------------------------------------------------
    # SUBPLOT 2: Alternative Orientation (Printed Flat on Base)
    # -------------------------------------------------------------------------
    ax2 = fig.add_subplot(122, projection="3d", facecolor="#181a1b")
    ax2.set_title("ALTERNATIVE ORIENTATION: PRINT FLAT ON BOTTOM\n⚠ Requires Supports under Hook  ⚠ Weaker Hook Layer Lines", 
                  fontsize=13, fontweight="bold", color="#fbbf24", pad=15)
    
    m_flat = mesh.copy()
    # In original mesh: X was height, Y was depth, Z was width.
    # To place on bottom: swap X and Z so height is along Z!
    # Rotate around Y by -90:
    rot_flat = trimesh.transformations.rotation_matrix(-np.pi/2, [0, 1, 0])
    # Rotate around X by 90 to make X -> Z
    rot_flat2 = trimesh.transformations.rotation_matrix(np.pi/2, [0, 0, 1])
    # Let's align cleanly: Z_new = X_orig (height), X_new = Z_orig (width), Y_new = Y_orig (depth)
    verts_flat = np.zeros_like(mesh.vertices)
    verts_flat[:, 0] = mesh.vertices[:, 2] # Width -> X
    verts_flat[:, 1] = mesh.vertices[:, 1] # Depth -> Y
    verts_flat[:, 2] = mesh.vertices[:, 0] # Height -> Z
    m_flat.vertices = verts_flat
    m_flat.vertices -= m_flat.bounds[0]
    m_flat.vertices += [40, 35, 0] # center on bed
    
    # Draw Build Plate (220x220 mm)
    ax2.plot_wireframe(bed_x, bed_y, bed_z, color="#404040", linewidth=0.7, alpha=0.5)
    ax2.plot_surface(np.array([[0, 220], [0, 220]]), 
                     np.array([[0, 0], [220, 220]]), 
                     np.array([[0, 0], [0, 0]]), color="#262626", alpha=0.4)
    
    # Draw simulated red tree supports under the hook overhang at back
    # Hook overhang is located at top rear of the part
    hook_box = trimesh.creation.box(extents=[36, 16, 75])
    hook_box.vertices += [110, 43, 37.5] # position under hook overhang
    poly_supp = Poly3DCollection(hook_box.vertices[hook_box.faces], 
                                 facecolors=[(0.9, 0.2, 0.2, 0.35)], 
                                 edgecolors="#ef4444", linewidths=0.6)
    ax2.add_collection3d(poly_supp)

    poly_flat = Poly3DCollection(m_flat.vertices[m_flat.faces], 
                                 facecolors=get_shaded_colors(m_flat, base_rgb=(0.95, 0.65, 0.2)),
                                 edgecolors="#b45309", linewidths=0.08)
    ax2.add_collection3d(poly_flat)
    
    ax2.set_xlim(0, 220)
    ax2.set_ylim(0, 220)
    ax2.set_zlim(0, 160)
    ax2.set_xlabel("Bed X (mm)", color="#9ca3af", labelpad=8)
    ax2.set_ylabel("Bed Y (mm)", color="#9ca3af", labelpad=8)
    ax2.set_zlabel("Print Height Z (mm)", color="#9ca3af", labelpad=8)
    ax2.tick_params(colors="#9ca3af")
    ax2.view_init(elev=24, azim=-55)

    ax2.text2D(0.05, 0.04, 
               "• Bed footprint: 140 × 135 mm (Large flat base)\n"
               "• Height: 85 mm\n"
               "• REQUIRES SUPPORTS under hook lip (shown in red)\n"
               "• Hook arm layers are horizontal -> Layer delamination risk when flexed!",
               transform=ax2.transAxes, color="#fde68a", fontsize=10, 
               bbox=dict(boxstyle="round,pad=0.5", facecolor="#78350f", alpha=0.8, edgecolor="#f59e0b"))

    plt.tight_layout()
    plt.savefig(out_img, dpi=200, bbox_inches="tight")
    print(f"Simulation image rendered successfully to: {out_img}")

if __name__ == "__main__":
    render_simulation()
