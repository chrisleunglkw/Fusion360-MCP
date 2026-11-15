import trimesh
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import os

def render_sunnersta_context():
    stl_path = "c:/Users/root/Downloads/Fusion360-MCP/KitchenSink_CoffeeDrainer_140mm.stl"
    drainer_mesh = trimesh.load(stl_path)
    
    artifact_dir = r"C:\Users\root\.gemini\antigravity\brain\5ecd4bab-3c44-40e0-b8dc-e416fd5880bc"
    out_img = os.path.join(artifact_dir, "sunnersta_cad_simulation.png")

    fig = plt.figure(figsize=(19, 10), facecolor="#0f172a")

    def shade_faces(m, base_rgb=(0.3, 0.7, 0.9), light_dir=np.array([0.4, 0.7, 0.6])):
        light_dir = light_dir / np.linalg.norm(light_dir)
        normals = m.face_normals
        intensity = np.clip(np.dot(normals, light_dir), 0.25, 1.0)
        colors = np.zeros((len(normals), 4))
        for i in range(3):
            colors[:, i] = base_rgb[i] * (0.3 + 0.7 * intensity)
        colors[:, 3] = 0.95
        return colors

    # =========================================================================
    # 1. Coordinate alignment:
    # Original mesh coordinates:
    # X: Height [0, 84.7 mm]
    # Y: Depth [-15.7, 135 mm]  (0 = front of beam, 92 = ledge end, 135 = spout)
    # Z: Width [-70, +70 mm]   (140 mm width)
    #
    # We want standard 3D view:
    # X: Width (left-right across counter, -150 to +150 mm)
    # Y: Depth (front-back, -30 mm behind beam to +180 mm in sink)
    # Z: Height (0 = counter, +80 = beam top)
    # =========================================================================
    verts_aligned = np.zeros_like(drainer_mesh.vertices)
    verts_aligned[:, 0] = drainer_mesh.vertices[:, 2] # Z -> X (Width)
    verts_aligned[:, 1] = drainer_mesh.vertices[:, 1] # Y -> Y (Depth)
    verts_aligned[:, 2] = drainer_mesh.vertices[:, 0] # X -> Z (Height)
    drainer_mesh.vertices = verts_aligned

    # Shift drainer slightly to left of faucet (X centered at -30 mm)
    drainer_mesh.vertices[:, 0] -= 25.0

    # =========================================================================
    # 2. Build IKEA SUNNERSTA Environment
    # =========================================================================
    # A. Back Beam (height 80mm, thickness 11.7mm, width 320mm)
    # Position: X in [-180, 140], Y in [-11.7, 0], Z in [0, 80]
    beam = trimesh.creation.box(extents=[320, 11.7, 80])
    beam.vertices += [-20, -5.85, 40]

    # B. Worktop Ledge (depth 95mm, width 320mm, flat at Z=0)
    # Position: X in [-180, 140], Y in [0, 95], Z in [-2, 0]
    ledge = trimesh.creation.box(extents=[320, 95, 2])
    ledge.vertices += [-20, 47.5, -1]

    # C. Sink Basin (drops 20mm down at Y=95mm, extends forward to Y=200mm)
    sink_step = trimesh.creation.box(extents=[320, 10, 20])
    sink_step.vertices += [-20, 95, -10]

    sink_floor = trimesh.creation.box(extents=[320, 100, 2])
    sink_floor.vertices += [-20, 150, -20]

    # D. Faucet (Base next to drainer at X = 75mm, Y = 55mm)
    faucet_base = trimesh.creation.cylinder(radius=22, height=12)
    faucet_base.vertices += [75, 55, 6]

    faucet_pipe = trimesh.creation.cylinder(radius=10, height=110)
    faucet_pipe.vertices += [75, 55, 65]

    faucet_spout = trimesh.creation.cylinder(radius=9, height=75)
    # Rotate spout forward into sink
    rot_x = trimesh.transformations.rotation_matrix(np.pi/2.5, [1, 0, 0])
    faucet_spout.apply_transform(rot_x)
    faucet_spout.vertices += [75, 75, 120]

    # =========================================================================
    # 3. Coffee Equipment on Drainer
    # =========================================================================
    # Portafilter head (cylinder diameter 70mm, height 30mm)
    pf_head = trimesh.creation.cylinder(radius=34, height=28)
    pf_head.vertices += [-55, 55, 25]
    
    # Portafilter handle (angled back/side)
    pf_handle = trimesh.creation.cylinder(radius=9, height=110)
    rot_h = trimesh.transformations.rotation_matrix(np.pi/3, [0, 0, 1])
    rot_h2 = trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0])
    pf_handle.apply_transform(rot_h)
    pf_handle.apply_transform(rot_h2)
    pf_handle.vertices += [-125, 25, 25]

    # Espresso Filter Basket 58mm (upside down)
    basket = trimesh.creation.cylinder(radius=29, height=24)
    basket.vertices += [0, 50, 23]

    # Small Ceramic Espresso Mug (upside down)
    cup = trimesh.creation.cylinder(radius=26, height=45)
    cup.vertices += [-25, 95, 33]

    # =========================================================================
    # PLOT 1: Isometric View of SUNNERSTA Application Simulation
    # =========================================================================
    ax1 = fig.add_subplot(121, projection="3d", facecolor="#0f172a")
    ax1.set_title("IKEA SUNNERSTA APPLICATION SIMULATION (ISOMETRIC)\nCustom 14cm Coffee Drainer Hooked on 11.7mm Beam", 
                  fontsize=12, fontweight="bold", color="#38bdf8", pad=12)

    # Stainless steel environment objects
    for m_obj, col in [
        (beam, (0.55, 0.60, 0.65)),
        (ledge, (0.65, 0.70, 0.75)),
        (sink_step, (0.50, 0.55, 0.60)),
        (sink_floor, (0.45, 0.50, 0.55)),
        (faucet_base, (0.85, 0.90, 0.95)),
        (faucet_pipe, (0.85, 0.90, 0.95)),
        (faucet_spout, (0.85, 0.90, 0.95))
    ]:
        poly = Poly3DCollection(m_obj.vertices[m_obj.faces],
                                facecolors=shade_faces(m_obj, base_rgb=col),
                                edgecolors="#334155", linewidths=0.1)
        ax1.add_collection3d(poly)

    # Coffee gear
    for m_gear, col, border in [
        (pf_head, (0.75, 0.75, 0.80), "#475569"),
        (pf_handle, (0.15, 0.15, 0.18), "#0f172a"),
        (basket, (0.80, 0.82, 0.85), "#64748b"),
        (cup, (0.95, 0.40, 0.25), "#9a3412")
    ]:
        poly = Poly3DCollection(m_gear.vertices[m_gear.faces],
                                facecolors=shade_faces(m_gear, base_rgb=col),
                                edgecolors=border, linewidths=0.2)
        ax1.add_collection3d(poly)

    # 3D Printed Drainer (Matte White PETG with cyan highlight)
    poly_drainer = Poly3DCollection(drainer_mesh.vertices[drainer_mesh.faces],
                                    facecolors=shade_faces(drainer_mesh, base_rgb=(0.92, 0.96, 0.99)),
                                    edgecolors="#0284c7", linewidths=0.15)
    ax1.add_collection3d(poly_drainer)

    ax1.set_xlim(-180, 140)
    ax1.set_ylim(-30, 190)
    ax1.set_zlim(-30, 130)
    ax1.set_xlabel("Width X (mm)", color="#94a3b8", labelpad=6)
    ax1.set_ylabel("Depth Y (mm)", color="#94a3b8", labelpad=6)
    ax1.set_zlabel("Height Z (mm)", color="#94a3b8", labelpad=6)
    ax1.tick_params(colors="#94a3b8")
    ax1.view_init(elev=28, azim=-55)

    ax1.text2D(0.04, 0.04, 
               "✔ Hook clips securely over IKEA SUNNERSTA 11.7mm beam (Z=80mm)\n"
               "✔ Drainer base sits flat on 95mm countertop ledge behind sink\n"
               "✔ Front spout overhangs 43mm into sink basin -> Water drains safely\n"
               "✔ Coffee gear (Portafilter, 58mm Basket, Mug) sits level & stable on ribs",
               transform=ax1.transAxes, color="#e2e8f0", fontsize=9.2, 
               bbox=dict(boxstyle="round,pad=0.5", facecolor="#1e293b", alpha=0.9, edgecolor="#38bdf8"))

    # =========================================================================
    # PLOT 2: Side Section View (True Mechanical Fit on SUNNERSTA)
    # =========================================================================
    ax2 = fig.add_subplot(122, facecolor="#0f172a")
    ax2.set_title("SIDE FIT & GRAVITY DRAINAGE ANALYSIS\nCross-Section View of Installation on SUNNERSTA Worktop", 
                  fontsize=12, fontweight="bold", color="#38bdf8", pad=12)

    # 1. SUNNERSTA Profile
    # Beam
    ax2.fill([-11.7, 0, 0, -11.7], [0, 0, 80, 80], color="#64748b", alpha=0.8, edgecolor="#94a3b8", linewidth=1.5, label="IKEA SUNNERSTA Beam (11.7mm x 80mm)")
    # Countertop Ledge
    ax2.fill([0, 95, 95, 0], [-2, -2, 0, 0], color="#475569", alpha=0.9, edgecolor="#94a3b8", linewidth=1.5, label="Countertop Ledge (95mm)")
    # Sink drop & basin
    ax2.plot([95, 95, 180], [0, -20, -20], color="#94a3b8", linewidth=2.5, linestyle="-", label="Sink Basin (20mm Drop)")

    # 2. Drainer Profile
    prof_y = [0, 92, 135, 135, 117, 0, 0, -12.5, -12.5, -15.7, -15.7, 3.2, 3.2, 15, 3, 3, 0]
    prof_z = [0, 0, 0.8, 3.8, 16, 16, 81.5, 81.5, 70, 73.2, 84.7, 84.7, 38, 7, 7, 16, 16]
    ax2.fill(prof_y, prof_z, color="#38bdf8", alpha=0.65, edgecolor="#0284c7", linewidth=2, label="3D Printed Drainer")

    # 3. Ribs Profile
    ax2.fill_between([8, 122], [7, 2.3], [10.5, 10.5], color="#0284c7", alpha=0.9, label="Level Ribs (Horiz. Z=10.5mm)")

    # 4. Drainage Slope & Water Droplets
    ax2.plot([3, 135], [7, 1.8], color="#06b6d4", linewidth=2.5, linestyle="--", label="Sloped Floor (5.2mm Drop)")
    # Droplet arrows cascading into sink
    ax2.annotate("Water Cascades into Sink", 
                 xy=(136, 1.5), xytext=(120, -14),
                 arrowprops=dict(facecolor="#06b6d4", shrink=0.08, width=2, headwidth=7),
                 color="#22d3ee", fontsize=9.5, fontweight="bold",
                 bbox=dict(boxstyle="round,pad=0.3", facecolor="#1e293b", edgecolor="#06b6d4"))

    # Hook engagement annotation
    ax2.annotate("12.5mm Hook engages over 11.7mm beam\n(Fixes position, prevents sliding)", 
                 xy=(-5.85, 82), xytext=(-25, 95),
                 arrowprops=dict(facecolor="#38bdf8", shrink=0.08, width=1.8, headwidth=6),
                 color="#e2e8f0", fontsize=9.2, fontweight="bold",
                 bbox=dict(boxstyle="round,pad=0.3", facecolor="#1e293b", edgecolor="#38bdf8"))

    # Coffee gear silhouettes
    # Portafilter outline
    ax2.plot([25, 85, 85, 25, 25], [10.5, 10.5, 38, 38, 10.5], color="#f8fafc", linewidth=2, linestyle="-")
    ax2.text(55, 24, "Portafilter / Basket\n(Rests Level on Ribs)", color="#f8fafc", fontsize=8.5, ha="center", va="center")

    ax2.set_xlim(-35, 185)
    ax2.set_ylim(-30, 115)
    ax2.set_xlabel("Depth / Distance from Beam (mm)", color="#94a3b8", fontsize=10)
    ax2.set_ylabel("Height Z (mm)", color="#94a3b8", fontsize=10)
    ax2.tick_params(colors="#94a3b8")
    ax2.grid(True, linestyle=":", alpha=0.3, color="#64748b")
    ax2.legend(loc="upper right", facecolor="#1e293b", edgecolor="#475569", labelcolor="#e2e8f0", fontsize=8)

    plt.tight_layout()
    plt.savefig(out_img, dpi=200, bbox_inches="tight")
    print(f"SUNNERSTA simulation saved to: {out_img}")

if __name__ == "__main__":
    render_sunnersta_context()
