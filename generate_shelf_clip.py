"""
Autodesk Fusion 360 - Parametric Shelf Clip for IKEA BONDTOLVAN Clock
Generates an 18mm shelf clip with an integrated 5mm wood screw replacement stud.
"""

import adsk.core
import adsk.fusion
import os

def run(_context: str):
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    rootComp = design.rootComponent
    
    occ = rootComp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = "IKEA_BONDTOLVAN_18mm_Shelf_Clip"
    
    sketches = comp.sketches
    extrudes = comp.features.extrudeFeatures
    fillets = comp.features.filletFeatures
    cplanes = comp.constructionPlanes
    
    yzPlane = comp.yZConstructionPlane
    xyPlane = comp.xYConstructionPlane
    
    # Dimensions (in cm for Fusion API: 1 cm = 10 mm)
    shelf_th = 1.80         # 18 mm shelf
    clip_gap = 1.82         # 18.2 mm gap
    prong_len = 2.80        # 28 mm prong reach
    wall_th = 0.30          # 3.0 mm prong thickness
    front_th = 0.35         # 3.5 mm front plate thickness
    clip_w = 2.20           # 22 mm clip width
    half_w = clip_w / 2.0   # 1.10 cm
    
    # 5mm Wood Screw Stud
    shank_dia = 0.48        # 4.8 mm shank
    shank_len = 0.32        # 3.2 mm neck clearance
    head_dia = 0.85         # 8.5 mm head
    head_len = 0.22         # 2.2 mm head thickness
    
    half_gap = clip_gap / 2.0
    half_outer = half_gap + wall_th
    
    # 1. U-Clip Profile Sketch on YZ Plane
    s_clip = sketches.add(yzPlane)
    lines_c = s_clip.sketchCurves.sketchLines
    pts = [
        adsk.core.Point3D.create(0, -prong_len, half_outer - 0.08),
        adsk.core.Point3D.create(0, -prong_len + 0.12, half_outer),
        adsk.core.Point3D.create(0, front_th, half_outer),
        adsk.core.Point3D.create(0, front_th, -half_outer),
        adsk.core.Point3D.create(0, -prong_len + 0.12, -half_outer),
        adsk.core.Point3D.create(0, -prong_len, -half_outer + 0.08),
        adsk.core.Point3D.create(0, -prong_len, -half_gap - 0.12),
        adsk.core.Point3D.create(0, -prong_len + 0.30, -half_gap + 0.035),
        adsk.core.Point3D.create(0, 0.0, -half_gap),
        adsk.core.Point3D.create(0, 0.0, half_gap),
        adsk.core.Point3D.create(0, -prong_len + 0.30, half_gap - 0.035),
        adsk.core.Point3D.create(0, -prong_len, half_gap + 0.12)
    ]
    for i in range(len(pts)):
        lines_c.addByTwoPoints(pts[i], pts[(i+1)%len(pts)])
        
    prof_c = s_clip.profiles.item(0)
    ext_c_in = extrudes.createInput(prof_c, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ext_c_in.setSymmetricExtent(adsk.core.ValueInput.createByReal(half_w), False)
    ext_c = extrudes.add(ext_c_in)
    body = ext_c.bodies.item(0)
    
    # 2. Screw Stud (Shank & Head) on Front Face
    # Front face is at Y = front_th
    pInput = cplanes.createInput()
    pInput.setByOffset(comp.xZConstructionPlane, adsk.core.ValueInput.createByReal(front_th))
    front_plane = cplanes.add(pInput)
    
    s_stud = sketches.add(front_plane)
    circles = s_stud.sketchCurves.sketchCircles
    circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), shank_dia / 2.0)
    circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), head_dia / 2.0)
    
    # Extrude shank
    prof_shank = s_stud.profiles.item(0) # inner circle
    ext_s_in = extrudes.createInput(prof_shank, adsk.fusion.FeatureOperations.JoinFeatureOperation)
    ext_s_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(shank_len))
    extrudes.add(ext_s_in)
    
    # Extrude head from shank top
    pInput2 = cplanes.createInput()
    pInput2.setByOffset(front_plane, adsk.core.ValueInput.createByReal(shank_len))
    head_plane = cplanes.add(pInput2)
    
    s_head = sketches.add(head_plane)
    s_head.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), head_dia / 2.0)
    prof_head = s_head.profiles.item(0)
    ext_h_in = extrudes.createInput(prof_head, adsk.fusion.FeatureOperations.JoinFeatureOperation)
    ext_h_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(head_len))
    extrudes.add(ext_h_in)
    
    # Export STL & STEP
    exportMgr = design.exportManager
    target_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in locals() else "c:/Users/root/Downloads/Fusion360-MCP"
    stl_path = os.path.join(target_dir, "IKEA_BONDTOLVAN_18mm_Shelf_Clip.stl")
    stlOptions = exportMgr.createSTLExportOptions(body, stl_path)
    stlOptions.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
    exportMgr.execute(stlOptions)
    
    step_path = os.path.join(target_dir, "IKEA_BONDTOLVAN_18mm_Shelf_Clip.step")
    stepOptions = exportMgr.createSTEPExportOptions(step_path, comp)
    exportMgr.execute(stepOptions)
    
    print(f"Generated clip successfully! Width: 22mm, Gap: 18.2mm, Stud: 5mm screw replacement")

if __name__ == "__main__":
    pass
