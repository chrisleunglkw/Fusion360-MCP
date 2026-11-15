# Fusion360-MCP · Structured CAD-to-Print Workbench

A structured AI-assisted CAD and FDM 3D-printing workspace combining **Autodesk Fusion 360 MCP** with a **Python headless solid-modeling pipeline** (`trimesh` / `manifold3d` / `shapely`) and an automated printability verification gate.

---

## Credits & Attribution

- **Workflow & Engineering Methodology**: Inspired by [**AFangTeam/PrintLab**](https://github.com/AFangTeam/PrintLab) — specifically its project-record structure (`brief.md`, `decisions.md`), `vNNN` version preservation, protected mating-interface tracking, single-source parametric CAD discipline, and pre-release geometry/view verification gates.
- **CAD Integration**: Built around **Autodesk Fusion 360 MCP** (`http://127.0.0.1:27182/mcp`) and standalone Fusion 360 Python API scripts (`adsk.core` / `adsk.fusion`).

---

## Workspace Structure

```text
Fusion360-MCP/
├── AGENTS.md                   # AI agent workflow rules & verification checklist
├── README.md                   # Overview, credits, and setup guide
├── mcp_config.json             # Fusion 360 MCP endpoint configuration
├── scripts/
│   └── cad_check.py            # Automated STL watertightness, component, overhang & 4-view gate
├── Templates/
│   └── Project/
│       ├── brief.md            # Template for measurements & protected interfaces
│       └── decisions.md        # Template for vNNN revision log & physical feedback
└── Projects/
    └── tisken-soap-drainer/    # Example project (v004 Japanese "Hamon" minimalist drainer)
        ├── brief.md
        ├── decisions.md
        ├── cad/                # Master Python + Fusion 360 scripts (mm)
        └── exports/v004/       # Versioned STL, SHA-256 manifest.json, 4-view PNG
```

---

## Setup Guide

### 1. Prerequisites
- **Python 3.10+** (tested on Python 3.14 on Windows)
- **Autodesk Fusion 360** *(optional if using the headless Python CAD path, required for live MCP execution or `.step`/`.f3d` export)*
- **FDM Slicer** (Bambu Studio, OrcaSlicer, or PrusaSlicer)

### 2. Install Python Dependencies
```bash
pip install trimesh manifold3d shapely mapbox-earcut matplotlib numpy
```

### 3. Configure Fusion 360 MCP (Optional — for Live Fusion Control)
1. Start the **Fusion 360 MCP Add-In** inside Autodesk Fusion 360 so it listens on `http://127.0.0.1:27182/mcp`.
2. Ensure your agent / IDE MCP config points to the local server (already configured in `mcp_config.json` and `.agents/mcp_config.json`):
   ```json
   {
     "mcpServers": {
       "fusion360": {
         "url": "http://127.0.0.1:27182/mcp"
       }
     }
   }
   ```
> **Note**: If Fusion 360 is closed, the workspace automatically falls back to generating watertight STLs via `trimesh` + `manifold3d` alongside an editable `generate_*.py` Fusion 360 script.

### 4. Verify Installation
Run the automated CAD gate against the included example project:
```bash
python scripts/cad_check.py Projects/tisken-soap-drainer/exports/v004/IKEA_TISKEN_Round_Soap_Drainer_110mm_Minimalist.stl --manifest Projects/tisken-soap-drainer/exports/v004/manifest.json --views Projects/tisken-soap-drainer/exports/v004/views_4panel.png
```
Expected output: `"passed": true`, `"watertight": true`, `"connected_components": 1`.

---

## Day-to-Day Workflow

1. **Start a New Object**: Copy `Templates/Project/` into `Projects/<project_id>/` and record measured mating dimensions and clearances in `brief.md`.
2. **Generate & Iterate (`v001`, `v002`, ...)**: Keep parametric dimensions in millimeters inside `cad/`. Never overwrite previous releases—export each iteration into `exports/vNNN/`.
3. **Run `cad_check.py`**: Confirm manifold watertightness, single connected body, overhang ratio (`> 45°`), bounding box, estimated PETG mass, SHA-256 checksum, and 4-view geometry render.
4. **Print & Log Physical Fit**: Slice flat on `Z = 0`, test print, and record real-world fit feedback in `decisions.md` before marking `brief.md` as **Physically Accepted**.
