import trimesh
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import os

def render_refined_clip_simulation():
    stl_path = "c:/Users/root/Downloads/Fusion360-MCP/IKEA_BONDTOLVAN_18mm_Shelf_Clip.stl"
    clip_mesh = trimesh.load(stl_path)
    
    artifact_dir = r"C:\Users\root\.gemini\antigravity\brain\5ecd4bab-3c44-40e0-b8dc-e416fd5880bc"
    out_img = os.path.join(artifact_dir, "bondtolvan_shelf_clip_simulation.png")

    fig = plt.figure(figsize=(19, 9.5), facecolor="#0f172a")

    def shade_faces(m, base_rgb=(0.25, 0.75, 0.95), light_dir=np.array([0.5, 0.6, 0.7])):
        light_dir = light_dir / np.linalg.norm(light_dir)
        normals = m.face_normals
        intensity = np.clip(np.dot(normals, light_dir), 0.25, 1.0)
        colors = np.zeros((len(normals), 4))
        for i in range(3):
            colors[:, i] = base_rgb[i] * (0.35 + 0.65 * intensity)
        colors[:, 3] = 0.98
        return colors

    # =========================================================================
    # VIEW 1: Isometric 3D Model with Detailed Stud Callouts
    # =========================================================================
    ax1 = fig.add_subplot(121, projection="3d", facecolor="#0f172a")
    ax1.set_title("18mm SHELF CLIP WITH 5mm WOOD SCREW STUD\nCustom Mount for IKEA BONDTOLVAN Digital Clock", 
                  fontsize=12, fontweight="bold", color="#38bdf8", pad=12)

    poly1 = Poly3DCollection(clip_mesh.vertices[clip_mesh.faces],
                             facecolors=shade_faces(clip_mesh, base_rgb=(0.22, 0.72, 0.92)),
                             edgecolors="#0284c7", linewidths=0.2)
    ax1.add_collection3d(poly1)

    ax1.set_xlim(-22, 22)
    ax1.set_ylim(-35, 18)
    ax1.set_zlim(-16, 16)
    ax1.set_xlabel("Width X (22 mm)", color="#94a3b8", labelpad=6)
    ax1.set_ylabel("Depth Y (39 mm)", color="#94a3b8", labelpad=6)
    ax1.set_zlabel("Height Z (24.2 mm)", color="#94a3b8", labelpad=6)
    ax1.tick_params(colors="#94a3b8")
    ax1.view_init(elev=22, azim=-45)

    ax1.text2D(0.04, 0.04, 
               "• Clip Throat: 18.2 mm (Snug fit on 18 mm shelf)\n"
               "• 5mm Screw Stud: Ø8.5mm Head, Ø4.8mm Shank, 3.2mm Neck Gap\n"
               "• Retention Clamping: +0.35mm positive grip bumps\n"
               "• Easy Install: 45° lead-in chamfers slide on with one hand\n"
               "• Print Orientation: Print flat on side -> 100% Support-Free!",
               transform=ax1.transAxes, color="#e2e8f0", fontsize=9.2, 
               bbox=dict(boxstyle="round,pad=0.5", facecolor="#1e293b", alpha=0.9, edgecolor="#38bdf8"))

    # =========================================================================
    # VIEW 2: Side Section Diagram Showing Shelf & Keyhole Fit
    # =========================================================================
    ax2 = fig.add_subplot(122, facecolor="#0f172a")
    ax2.set_title("MECHANICAL FIT & MOUNTING SCHEMATIC\nSide Cross-Section: 18mm Shelf Clamping & Keyhole Lock", 
                  fontsize=12, fontweight="bold", color="#38bdf8", pad=12)

    # 1. 18mm Shelf (Wood)
    ax2.fill([-45, 0, 0, -45], [-9, -9, 9, 9], color="#b45309", alpha=0.7, edgecolor="#f59e0b", linewidth=1.5, label="18mm Shelf (Wood/Laminate)")
    
    # 2. Clip Cross-Section Profile
    pts_y = [-28, -26.8, 3.5, 3.5, -26.8, -28, -28, -25, 0, 0, -25, -28, -28]
    pts_z = [11.3, 12.1, 12.1, -12.1, -12.1, -11.3, -10.3, -8.75, -9.1, 9.1, 8.75, 10.3, 11.3]
    ax2.fill(pts_y, pts_z, color="#0284c7", alpha=0.75, edgecolor="#38bdf8", linewidth=2, label="3D Printed Clip (22mm wide)")

    # 3. Screw Stud on Front Face (Y from 3.5 to 3.5+3.2+2.2 = 8.9)
    # Shank: Y in [3.5, 6.7], Z in [-2.4, 2.4]
    ax2.fill([3.5, 6.7, 6.7, 3.5], [-2.4, -2.4, 2.4, 2.4], color="#38bdf8", alpha=0.9, edgecolor="#0284c7", linewidth=1.5, label="Ø4.8mm Screw Shank")
    # Head: Y in [6.7, 8.9], Z in [-4.25, 4.25]
    ax2.fill([6.7, 8.9, 8.9, 6.7], [-4.25, -4.25, 4.25, 4.25], color="#0ea5e9", alpha=0.95, edgecolor="#38bdf8", linewidth=1.5, label="Ø8.5mm Screw Head")

    # 4. BONDTOLVAN Clock Backplate & Keyhole outline
    # Backplate: Y = 4.2 to 6.2, hanging down from Z = +2.4
    ax2.fill([4.0, 6.2, 6.2, 4.0], [-35, -35, 2.0, 2.0], color="#94a3b8", alpha=0.55, edgecolor="#cbd5e1", linewidth=1.5, label="BONDTOLVAN Clock Backplate")
    # Clock Main Body (hangs down in front)
    ax2.fill([6.2, 35, 35, 6.2], [-35, -35, 15, 15], color="#334155", alpha=0.85, edgecolor="#64748b", linewidth=1.5, label="BONDTOLVAN Clock Body (80mm tall)")

    # Annotations & Dimension Arrows
    ax2.annotate("18mm Shelf Thickness\n(Firm Spring Clamp)", 
                 xy=(-15, 0), xytext=(-38, 22),
                 arrowprops=dict(facecolor="#f59e0b", shrink=0.08, width=1.5, headwidth=6),
                 color="#fde047", fontsize=9.2, fontweight="bold",
                 bbox=dict(boxstyle="round,pad=0.3", facecolor="#1e293b", edgecolor="#f59e0b"))

    ax2.annotate("Ø8.5mm Screw Head\n(Locks in Keyhole Slot)", 
                 xy=(7.8, 4.25), xytext=(12, 24),
                 arrowprops=dict(facecolor="#38bdf8", shrink=0.08, width=1.5, headwidth=6),
                 color="#e2e8f0", fontsize=9.2, fontweight="bold",
                 bbox=dict(boxstyle="round,pad=0.3", facecolor="#1e293b", edgecolor="#38bdf8"))

    ax2.annotate("Dual Clips Spaced 134 mm Apart\n(Matching Clock Keyhole Centers)", 
                 xy=(5.0, -15), xytext=(15, -28),
                 arrowprops=dict(facecolor="#38bdf8", shrink=0.08, width=1.5, headwidth=6),
                 color="#38bdf8", fontsize=9.2, fontweight="bold",
                 bbox=dict(boxstyle="round,pad=0.3", facecolor="#1e293b", edgecolor="#38bdf8"))

    ax2.set_xlim(-50, 40)
    ax2.set_ylim(-40, 32)
    ax2.set_xlabel("Depth Y (mm)", color="#94a3b8", fontsize=10)
    ax2.set_ylabel("Height Z (mm)", color="#94a3b8", fontsize=10)
    ax2.tick_params(colors="#94a3b8")
    ax2.grid(True, linestyle=":", alpha=0.25, color="#64748b")
    ax2.legend(loc="upper left", facecolor="#1e293b", edgecolor="#475569", labelcolor="#e2e8f0", fontsize=8)

    plt.tight_layout()
    plt.savefig(out_img, dpi=200, bbox_inches="tight")
    print(f"Refined simulation saved to: {out_img}")

if __name__ == "__main__":
    render_refined_clip_simulation()
