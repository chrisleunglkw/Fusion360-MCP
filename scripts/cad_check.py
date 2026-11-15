"""
Automated CAD Geometry & FDM Printability Verification Gate
Inspired by PrintLab (AFangTeam/PrintLab) cad-master-design & design-check workflows.
"""
import argparse
import hashlib
import json
import os
import sys
import numpy as np
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def count_connected_components(mesh: trimesh.Trimesh) -> int:
    """Count connected face components without requiring scipy/networkx."""
    try:
        return len(mesh.split(only_watertight=False))
    except ImportError:
        n_faces = len(mesh.faces)
        if n_faces == 0:
            return 0
        adj = [[] for _ in range(n_faces)]
        for a, b in mesh.face_adjacency:
            adj[a].append(b)
            adj[b].append(a)
        visited = bytearray(n_faces)
        count = 0
        for start in range(n_faces):
            if visited[start]:
                continue
            count += 1
            stack = [start]
            visited[start] = 1
            while stack:
                cur = stack.pop()
                for nxt in adj[cur]:
                    if not visited[nxt]:
                        visited[nxt] = 1
                        stack.append(nxt)
        return count


def analyze_mesh(stl_path: str) -> dict:
    mesh = trimesh.load(stl_path, force="mesh")
    extents = [round(float(v), 2) for v in mesh.extents]
    bounds_min = [round(float(v), 2) for v in mesh.bounds[0]]
    bounds_max = [round(float(v), 2) for v in mesh.bounds[1]]

    # Connected components check
    num_components = count_connected_components(mesh)

    # Volume & weight estimate (PETG 1.24 g/cm3, ~45% effective fill at 3 walls + 15% infill)
    vol_cm3 = float(mesh.volume) / 1000.0 if mesh.is_watertight else 0.0
    est_weight_g = vol_cm3 * 1.24 * 0.45

    # Overhang analysis: downward-facing faces > 45 deg off vertical, elevated above build plate
    normals = mesh.face_normals
    areas = mesh.area_faces
    z_centers = mesh.triangles_center[:, 2]
    z_min = float(mesh.bounds[0][2])

    # A face is a steep overhang if normal_z < -cos(45 deg) = -0.7071 AND not touching bed
    steep_mask = (normals[:, 2] < -0.7071) & (z_centers > z_min + 0.4)
    total_area = float(np.sum(areas)) if len(areas) else 1.0
    steep_area = float(np.sum(areas[steep_mask]))
    steep_pct = (steep_area / total_area) * 100.0

    # Bed contact area (faces near z_min pointing straight down)
    bed_mask = (normals[:, 2] < -0.95) & (z_centers <= z_min + 0.4)
    bed_contact_mm2 = float(np.sum(areas[bed_mask]))

    issues = []
    if not mesh.is_watertight:
        issues.append("Mesh is NOT watertight (non-manifold or open edges)")
    if num_components != 1:
        issues.append(f"Expected 1 connected body, found {num_components} disconnected components")
    if vol_cm3 <= 0:
        issues.append("Solid volume is <= 0")
    if bed_contact_mm2 < 10.0:
        issues.append(f"Very small build-plate contact area ({bed_contact_mm2:.1f} mm²)")
    if steep_pct > 5.0:
        issues.append(f"High steep overhang ratio ({steep_pct:.1f}% > 45 deg); supports may be needed")

    return {
        "file": os.path.abspath(stl_path),
        "sha256": sha256_file(stl_path),
        "watertight": bool(mesh.is_watertight),
        "connected_components": num_components,
        "extents_mm": {"x": extents[0], "y": extents[1], "z": extents[2]},
        "bounds_mm": {"min": bounds_min, "max": bounds_max},
        "volume_cm3": round(vol_cm3, 2),
        "est_weight_petg_g": round(est_weight_g, 1),
        "bed_contact_mm2": round(bed_contact_mm2, 1),
        "steep_overhang_pct": round(steep_pct, 2),
        "face_count": int(len(mesh.faces)),
        "passed": len(issues) == 0,
        "issues": issues,
    }, mesh


def render_4view(mesh: trimesh.Trimesh, report: dict, out_png: str):
    fig = plt.figure(figsize=(12, 10), dpi=140)
    fig.patch.set_facecolor("#0f172a")

    # Subsample faces only if huge to keep render snappy
    step = max(1, len(mesh.faces) // 4000)
    tri_verts = mesh.vertices[mesh.faces[::step]]

    cx, cy, cz = mesh.centroid
    max_span = max(mesh.extents) * 0.65

    views = [
        ("Top View (XY)", 90, -90, 1),
        ("Front View (XZ)", 0, -90, 2),
        ("Right Side View (YZ)", 0, 0, 3),
        ("Isometric View", 32, -55, 4),
    ]

    for title, elev, azim, idx in views:
        ax = fig.add_subplot(2, 2, idx, projection="3d")
        ax.set_facecolor("#1e293b")
        col = Poly3DCollection(tri_verts, alpha=0.92, edgecolor="#38bdf8", linewidth=0.18)
        col.set_facecolor("#f8fafc")
        ax.add_collection3d(col)
        ax.set_xlim(cx - max_span, cx + max_span)
        ax.set_ylim(cy - max_span, cy + max_span)
        ax.set_zlim(cz - max_span, cz + max_span)
        ax.view_init(elev=elev, azim=azim)
        ax.set_box_aspect([1, 1, 1])
        ax.set_axis_off()
        ax.set_title(title, color="#f8fafc", fontsize=11, fontweight="bold", pad=6)

    ext = report["extents_mm"]
    status = "PASSED" if report["passed"] else "CHECK WARNINGS"
    subtitle = (
        f"Status: {status} | {ext['x']} x {ext['y']} x {ext['z']} mm | "
        f"Vol: {report['volume_cm3']} cm³ (~{report['est_weight_petg_g']} g) | "
        f"Watertight: {report['watertight']} | Bodies: {report['connected_components']} | "
        f"Overhangs >45°: {report['steep_overhang_pct']}%"
    )
    plt.suptitle(
        f"CAD Verification Sheet: {os.path.basename(report['file'])}\n{subtitle}",
        color="#f8fafc",
        fontsize=11,
        fontweight="bold",
        y=0.98,
    )
    plt.tight_layout(rect=[0, 0, 1, 0.94])
    plt.savefig(out_png, dpi=140, facecolor=fig.get_facecolor())
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="Verify STL geometry & FDM printability.")
    parser.add_argument("stl", help="Path to STL file")
    parser.add_argument("--manifest", help="Optional output JSON manifest path")
    parser.add_argument("--views", help="Optional output 4-view PNG path")
    args = parser.parse_args()

    if not os.path.isfile(args.stl):
        print(f"ERROR: File not found: {args.stl}", file=sys.stderr)
        sys.exit(1)

    report, mesh = analyze_mesh(args.stl)
    print(json.dumps(report, indent=2))

    if args.manifest:
        os.makedirs(os.path.dirname(os.path.abspath(args.manifest)), exist_ok=True)
        with open(args.manifest, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

    if args.views:
        os.makedirs(os.path.dirname(os.path.abspath(args.views)), exist_ok=True)
        render_4view(mesh, report, args.views)
        print(f"Saved 4-view verification render: {args.views}")

    if not report["passed"]:
        sys.exit(2)


if __name__ == "__main__":
    main()
