import trimesh
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import os

def render_japanese_minimalist_schematic():
    out_dir = "c:/Users/root/Downloads/Fusion360-MCP"
    stl_path = os.path.join(out_dir, "IKEA_TISKEN_Round_Soap_Drainer_110mm_Minimalist.stl")
    
    mesh = trimesh.load(stl_path)
    
    fig = plt.figure(figsize=(16, 9), dpi=150)
    fig.patch.set_facecolor('#111827') # Zen charcoal slate
    
    # 1. 3D Isometric View
    ax_iso = fig.add_subplot(1, 2, 1, projection='3d')
    ax_iso.set_facecolor('#111827')
    
    sample_faces = mesh.faces[::2]
    tri_verts = mesh.vertices[sample_faces]
    
    collection = Poly3DCollection(tri_verts, alpha=0.94, edgecolor='#94a3b8', linewidth=0.22)
    collection.set_facecolor('#f8fafc')
    ax_iso.add_collection3d(collection)
    
    # Ghost TISKEN beam
    ax_iso.plot([-45, 45], [-65.5, -65.5], [30.5, 30.5], color='#a855f7', lw=3.0, linestyle='--', label='IKEA TISKEN Rail (8.0mm)')
    ax_iso.plot([-45, 45], [-65.5, -65.5], [12.5, 12.5], color='#a855f7', lw=2.0, linestyle=':')
    
    # Water droplets falling straight through the concentric zen ripple gaps
    for dx, dy in [(-18, 12), (18, 12), (0, -20), (0, 22)]:
        ax_iso.plot([dx, dx], [dy, dy], [1, -22], color='#38bdf8', lw=1.5, linestyle=':')
        ax_iso.scatter([dx], [dy], [-18], color='#06b6d4', s=45, marker='o')
    ax_iso.scatter([0], [0], [-22], color='#06b6d4', s=45, marker='o', label='Direct Hollow Drip -> Bath')
    
    ax_iso.set_xlim(-60, 60)
    ax_iso.set_ylim(-75, 60)
    ax_iso.set_zlim(-25, 42)
    ax_iso.view_init(elev=35, azim=-55)
    ax_iso.set_axis_off()
    ax_iso.set_title("Japanese Minimalist 3D Isometric\n(\"Hamon\" Zen Ripple Lattice + Chamfered Rim)", color='#f8fafc', fontsize=13, fontweight='bold', pad=10)
    ax_iso.legend(loc='upper right', facecolor='#1f2937', edgecolor='#4b5563', labelcolor='#f8fafc', fontsize=9)
    
    # 2. Side Cross-Section (Y vs Z)
    ax_side = fig.add_subplot(2, 2, 2)
    ax_side.set_facecolor('#1f2937')
    
    rect_beam = plt.Rectangle((-69.5, 12.5), 8.0, 20.0, facecolor='#a855f7', alpha=0.35, edgecolor='#c084fc', lw=2.0, label='TISKEN Front Rail (8.0mm)')
    ax_side.add_patch(rect_beam)
    
    # Outer ring chamfered walls in section
    wall_back = plt.Rectangle((-55, 0), 2.8, 10.5, facecolor='#e2e8f0', edgecolor='#38bdf8', lw=2.0)
    wall_front = plt.Rectangle((52.2, 0), 2.8, 10.5, facecolor='#e2e8f0', edgecolor='#38bdf8', lw=2.0, label='Chamfered Outer Ring (Ø110mm)')
    ax_side.add_patch(wall_back)
    ax_side.add_patch(wall_front)
    
    # Concentric ripple cross-sections
    for rx in [-32, -12, 9.8, 29.8]:
        r_patch = plt.Rectangle((rx, 0), 2.2, 3.4, facecolor='#cbd5e1', edgecolor='#38bdf8', lw=1.2)
        ax_side.add_patch(r_patch)
    
    # Slim beveled hook bracket profile
    hook_y = [-53.2, -53.2, -58, -58, -59.2, -71.3, -72.5, -72.5, -70.7, -69.5, -69.5, -61, -61, -62.2, -62.2, -53.2, -53.2]
    hook_z = [8.3, 10.0, 17.0, 34.3, 35.5, 35.5, 34.3, 20.0, 17.5, 20.0, 32.5, 32.5, 2.8, 1.4, 0, 0, 2.8]
    ax_side.plot(hook_y, hook_z, color='#38bdf8', lw=2.5, label='Slim 18mm Beveled Hook (8.5mm gap)')
    
    for dy in [-21, 0, 21]:
        ax_side.annotate('', xy=(dy, -18), xytext=(dy, 1), arrowprops=dict(arrowstyle="->", color='#38bdf8', lw=2))
    ax_side.text(0, -22, 'HOLLOW ZEN LATTICE DRIPS STRAIGHT INTO BATH', color='#38bdf8', fontsize=9, fontweight='bold', ha='center')
    
    ax_side.set_xlim(-85, 70)
    ax_side.set_ylim(-26, 43)
    ax_side.set_aspect('equal')
    ax_side.set_xlabel('Y Position (mm) [Basket <--- ---> Bath]', color='#cbd5e1', fontsize=10)
    ax_side.set_ylabel('Z Height (mm)', color='#cbd5e1', fontsize=10)
    ax_side.tick_params(colors='#94a3b8')
    ax_side.grid(True, linestyle=':', color='#374151')
    ax_side.set_title("Side Section: Low-Profile 10.5mm Rim & Slim Hook", color='#f8fafc', fontsize=11, fontweight='bold')
    ax_side.legend(loc='upper right', facecolor='#111827', edgecolor='#4b5563', labelcolor='#f8fafc', fontsize=8)
    
    # 3. Top-Down Plan View (X vs Y)
    ax_top = fig.add_subplot(2, 2, 4)
    ax_top.set_facecolor('#1f2937')
    
    # Outer ring
    ax_top.add_patch(plt.Circle((0, 0), 55, facecolor='#f8fafc', edgecolor='#38bdf8', lw=1.8))
    ax_top.add_patch(plt.Circle((0, 0), 52.2, facecolor='#111827', edgecolor='#38bdf8', lw=1.2))
    
    # 6 Radial spokes
    for i in range(6):
        ang = np.deg2rad(i * 60.0 + 30.0)
        ca, sa = np.cos(ang), np.sin(ang)
        x0, y0 = 9.8 * ca, 9.8 * sa
        x1, y1 = 53.0 * ca, 53.0 * sa
        ax_top.plot([x0, x1], [y0, y1], color='#f8fafc', lw=3.2, solid_capstyle='butt')
        
    # Middle & Center concentric ripple rings
    ax_top.add_patch(plt.Circle((0, 0), 32.0, facecolor='none', edgecolor='#f8fafc', lw=3.5))
    ax_top.add_patch(plt.Circle((0, 0), 12.0, facecolor='none', edgecolor='#f8fafc', lw=3.5, label='Hamon Concentric Ripple Lattice (~82% Open)'))
    
    # Slim 18mm hook bracket at rear
    hook_top_rect = plt.Rectangle((-9, -72.5), 18, 19.3, facecolor='#38bdf8', alpha=0.55, edgecolor='#38bdf8', lw=2, label='Extra-Slim 18mm Hook Bracket')
    ax_top.add_patch(hook_top_rect)
    
    ax_top.set_xlim(-65, 65)
    ax_top.set_ylim(-80, 65)
    ax_top.set_aspect('equal')
    ax_top.set_xlabel('X Position (mm)', color='#cbd5e1', fontsize=10)
    ax_top.set_ylabel('Y Position (mm)', color='#cbd5e1', fontsize=10)
    ax_top.tick_params(colors='#94a3b8')
    ax_top.grid(True, linestyle=':', color='#374151')
    ax_top.set_title("Top Plan View: Japanese Zen Ripple Lattice (~9.8 g Filament)", color='#f8fafc', fontsize=11, fontweight='bold')
    ax_top.legend(loc='lower left', facecolor='#111827', edgecolor='#4b5563', labelcolor='#f8fafc', fontsize=8)
    
    plt.suptitle("IKEA TISKEN Japanese Minimalist Soap Drainer - \"Hamon\" Edition", color='#f8fafc', fontsize=15, fontweight='bold', y=0.98)
    plt.tight_layout()
    
    sim_path = "C:/Users/root/.gemini/antigravity/brain/5ecd4bab-3c44-40e0-b8dc-e416fd5880bc/tisken_soap_drainer_simulation.png"
    plt.savefig(sim_path, dpi=180, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print("Saved schematic:", sim_path)

if __name__ == "__main__":
    render_japanese_minimalist_schematic()
