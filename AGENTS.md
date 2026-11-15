# Fusion360-MCP · CAD & 3D-Printing Agent Guide

This workspace uses a structured CAD-to-print workflow inspired by **PrintLab** (`AFangTeam/PrintLab`), tailored for **Autodesk Fusion 360 MCP**, **Python (`trimesh` / `manifold3d`)**, and **FDM 3D printing**.

## 1. Workspace Structure

- `AGENTS.md` — Core workflow rules and handoff checklist.
- `Templates/Project/` — Templates (`brief.md`, `decisions.md`) for new objects.
- `Projects/<project_id>/` — Dedicated folder per object:
  - `brief.md` — Purpose, measured physical dimensions, protected mating interfaces, clearances, material, and acceptance criteria.
  - `decisions.md` — Revision log (`v001`, `v002`, ...) with user feedback, design trade-offs, and physical test results.
  - `cad/` — Master Python/Fusion 360 parametric scripts (single source of truth in **mm**).
  - `exports/<vNNN>/` — Versioned `.stl`, `.step`, `.3mf`, `manifest.json` (SHA-256 + geometry stats), and multi-view renders.
- `scripts/cad_check.py` — Automated mesh & FDM printability gate (watertightness, connected components, overhang analysis, SHA-256 binding, 4-view render).

## 2. Core Workflow Rules

1. **Preserve Version History**: Never overwrite a working candidate without recording the previous revision or writing the new release to `exports/vNNN/`.
2. **Protect Mating Interfaces**: Record measured dimensions (e.g., rail thickness, shelf thickness, screw diameter) and tolerances explicitly in `brief.md`. Re-verify protected interfaces after every aesthetic or structural edit.
3. **Single Master Source**: Keep parametric dimensions in one place (`cad/`) in millimeters (`mm`). Test clips and full parts must share the exact same interface geometry.
4. **Verify Before Presenting**: Run `python scripts/cad_check.py <stl_path>` after every geometry build to confirm:
   - `watertight == True` (manifold solid)
   - `connected_components == 1` (no floating islands)
   - Printable orientation & overhang ratio
   - Exact bounding box (`X × Y × Z` mm) and estimated PETG/PLA mass (`g`)
   - SHA-256 checksum recorded in the revision manifest
5. **Separate Render Evidence from Physical Acceptance**:
   - Lifestyle / AI renders illustrate appearance only; orthographic/isometric views exported from the actual STL prove geometry.
   - Distinguish **CAD verified** (software check) from **physically accepted** (user test-printed and confirmed fit).
