"""
Autodesk Fusion 360 - Parametric 18mm Shelf Mount for NVIDIA Shield Tablet K1
Generates a minimal-material dual-clip bracket system holding the tablet horizontally.
"""

import adsk.core
import adsk.fusion
import math
import os

def run(_context: str):
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    rootComp = design.rootComponent
    
    occ = rootComp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = "NVIDIA_Shield_K1_18mm_Shelf_Mount"
    
    sketches = comp.sketches
    extrudes = comp.features.extrudeFeatures
    fillets = comp.features.filletFeatures
    yzPlane = comp.yZConstructionPlane
    
    # Dimensions (in cm for Fusion API: 1 cm = 10 mm)
    shelf_th = 1.80          # 18 mm shelf
    clip_gap = 1.82          # 18.2 mm gap
    prong_len = 2.80         # 28 mm prong reach
    wall_th = 0.32           # 3.2 mm clamp wall
    front_bridge_th = 0.35   # 3.5 mm front plate
    clip_w = 2.40            # 24 mm clip width
    half_w = clip_w / 2.0
    
    # Tablet slot
    slot_th = 1.04           # 10.4 mm slot width (clears 9.2 - 9.5 mm tablet)
    cradle_lip_h = 1.00      # 10.0 mm lip height
    cradle_lip_th = 0.30     # 3.0 mm lip thickness
    tilt_deg = 10.0          # 10 degree ergonomic viewing tilt
    tilt_rad = math.radians(tilt_deg)
    
    half_gap = clip_gap / 2.0
    half_outer = half_gap + wall_th
    cradle_base_z = -half_outer - 0.35
    
    cos_t = math.cos(tilt_rad)
    sin_t = math.sin(tilt_rad)
    
    y0 = front_bridge_th
    z0 = -half_outer
    
    y1 = y0 + cos_t * slot_th
    z1 = z0 - sin_t * slot_th
    
    y2 = y1 - sin_t * cradle_lip_h
    z2 = z1 + cos_t * cradle_lip_h
    
    y3 = y2 + cos_t * cradle_lip_th
    z3 = z2 - sin_t * cradle_lip_th
    
    y4 = y1 + cos_t * cradle_lip_th - sin_t * (cradle_lip_h * 0.4)
    z4 = z1 - sin_t * cradle_lip_th + cos_t * (cradle_lip_h * 0.4)
    
    y5 = front_bridge_th + 0.20
    z5 = cradle_base_z
    
    pts = [
        adsk.core.Point3D.create(0, -prong_len, half_outer - 0.08),
        adsk.core.Point3D.create(0, -prong_len + 0.12, half_outer),
        adsk.core.Point3D.create(0, front_bridge_th, half_outer),
        adsk.core.Point3D.create(0, front_bridge_th + 0.08, (half_outer + z0) / 2.0),
        adsk.core.Point3D.create(0, y0, z0),
        adsk.core.Point3D.create(0, y1, z1),
        adsk.core.Point3D.create(0, y2, z2),
        adsk.core.Point3D.create(0, y2 + cos_t*cradle_lip_th*0.5, z2 - sin_t*cradle_lip_th*0.5 + 0.08),
        adsk.core.Point3D.create(0, y3, z3),
        adsk.core.Point3D.create(0, y4, z4),
        adsk.core.Point3D.create(0, y5, z5),
        adsk.core.Point3D.create(0, -prong_len + 0.12, -half_outer),
        adsk.core.Point3D.create(0, -prong_len, -half_outer + 0.08),
        adsk.core.Point3D.create(0, -prong_len, -half_gap - 0.12),
        adsk.core.Point3D.create(0, -prong_len + 0.30, -half_gap + 0.035),
        adsk.core.Point3D.create(0, 0.0, -half_gap),
        adsk.core.Point3D.create(0, 0.0, half_gap),
        adsk.core.Point3D.create(0, -prong_len + 0.30, half_gap - 0.035),
        adsk.core.Point3D.create(0, -prong_len, half_gap + 0.12)
    ]
    
    s = sketches.add(yzPlane)
    lines = s.sketchCurves.sketchLines
    for i in range(len(pts)):
        lines.addByTwoPoints(pts[i], pts[(i+1)%len(pts)])
        
    prof = s.profiles.item(0)
    ext_in = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ext_in.setSymmetricExtent(adsk.core.ValueInput.createByReal(half_w), False)
    ext = extrudes.add(ext_in)
    body = ext.bodies.item(0)
    
    # Export STL
    exportMgr = design.exportManager
    target_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in locals() else "c:/Users/root/Downloads/Fusion360-MCP"
    stl_path = os.path.join(target_dir, "NVIDIA_Shield_K1_18mm_Shelf_Mount.stl")
    stlOptions = exportMgr.createSTLExportOptions(body, stl_path)
    stlOptions.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
    exportMgr.execute(stlOptions)
    
    step_path = os.path.join(target_dir, "NVIDIA_Shield_K1_18mm_Shelf_Mount.step")
    stepOptions = exportMgr.createSTEPExportOptions(step_path, comp)
    exportMgr.execute(stepOptions)
    
    print(f"Generated NVIDIA Shield K1 mount clip successfully! Width: {clip_w*10:.1f} mm, Volume: {body.volume:.1f} cm3")

if __name__ == "__main__":
    pass
