"""
Autodesk Fusion 360 - Parametric Kitchen Sink Coffee Drainer Generator
Generates a custom FDM-optimized drying tray with:
- Back hook clipping over a 11.7 mm worktop beam (80 mm tall)
- 140 mm width (around 14 cm)
- Downward sloped floor (5.2 mm drop) directing water into the sink
- 11 raised level drying ribs for coffee baskets, portafilters, mugs, spoons
- Open front spout with drip chamfer
- Full fillets on rim and rib edges
"""

import adsk.core
import adsk.fusion
import os

def run(_context: str):
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    rootComp = design.rootComponent
    
    # Reset/clean existing test occurrences
    while rootComp.occurrences.count > 0:
        rootComp.occurrences.item(0).deleteMe()
        
    occ = rootComp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = "KitchenSink_CoffeeDrainer"
    
    sketches = comp.sketches
    extrudes = comp.features.extrudeFeatures
    cplanes = comp.constructionPlanes
    fillets = comp.features.filletFeatures
    
    yzPlane = comp.yZConstructionPlane
    
    # =========================================================================
    # PARAMETRIC DIMENSIONS (in cm for Fusion API: 1 cm = 10 mm)
    # =========================================================================
    width_total = 14.0         # 140 mm width (around 14 cm)
    half_w = width_total / 2.0 # 7.0 cm (symmetric half-width across Z)
    wall_th = 0.28             # 2.8 mm side wall thickness
    inner_half_w = half_w - wall_th # 6.72 cm pocket half-width
    
    counter_depth = 9.2        # 92 mm flat resting zone on counter
    depth_total = 13.5         # 135 mm total depth (extends 43 mm over sink)
    
    # Vertical heights (along X axis in Fusion YZ extrusion frame)
    back_wall_h = 1.60         # 16.0 mm rim height
    floor_back_x = 0.70        # 7.0 mm floor height at back
    floor_front_x = 0.18       # 1.8 mm floor height at front spout (5.2 mm drop)
    
    # Beam & Hook dimensions
    beam_th = 1.17             # 11.7 mm beam thickness
    hook_clearance = 0.08      # 0.8 mm clearance (snug & easy slip-on)
    hook_inner_gap = beam_th + hook_clearance # 1.25 cm (12.5 mm)
    beam_h = 8.0               # 80 mm beam height
    hook_top_x = beam_h + 0.15 # 8.15 cm (81.5 mm, 1.5 mm top clearance)
    hook_th = 0.32             # 3.2 mm hook thickness
    hook_lip_drop = 1.15       # 11.5 mm downward retaining lip behind beam
    hook_w = 3.6               # 36 mm hook bracket width
    hook_half_w = hook_w / 2.0 # 1.8 cm
    
    # Ribs (Drying Grille)
    rib_top_x = 1.05           # 10.5 mm height (level drying surface)
    half_rib_th = 0.10         # 2.0 mm wide ribs
    rib_spacing = 1.10         # 11.0 mm pitch between ribs
    
    # =========================================================================
    # STEP 1: Outer Solid Block (Extrude Symmetric along Z)
    # =========================================================================
    s_outer = sketches.add(yzPlane)
    p_outer = [
        adsk.core.Point3D.create(0, 0.0, 0.0),
        adsk.core.Point3D.create(0, counter_depth, 0.0),
        adsk.core.Point3D.create(0, depth_total, 0.08),       # relief taper for sink drop
        adsk.core.Point3D.create(0, depth_total, 0.38),       # front spout side tip
        adsk.core.Point3D.create(0, depth_total - 1.8, back_wall_h), # graceful rim taper
        adsk.core.Point3D.create(0, 0.0, back_wall_h)         # back wall top
    ]
    lines_out = s_outer.sketchCurves.sketchLines
    for i in range(len(p_outer)):
        lines_out.addByTwoPoints(p_outer[i], p_outer[(i+1)%len(p_outer)])
        
    prof_out = s_outer.profiles.item(0)
    ext_in1 = extrudes.createInput(prof_out, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ext_in1.setSymmetricExtent(adsk.core.ValueInput.createByReal(half_w), False)
    ext1 = extrudes.add(ext_in1)
    body = ext1.bodies.item(0)
    body.name = "DrainerBase"

    # =========================================================================
    # STEP 2: Interior Pocket Cut (Sloped Floor & Side Rims)
    # =========================================================================
    s_cut = sketches.add(yzPlane)
    p_cut = [
        adsk.core.Point3D.create(0, 0.30, floor_back_x),
        adsk.core.Point3D.create(0, 0.30, 2.5),
        adsk.core.Point3D.create(0, 14.5, 2.5),
        adsk.core.Point3D.create(0, 14.5, floor_front_x),
        adsk.core.Point3D.create(0, depth_total, floor_front_x)
    ]
    lines_cut = s_cut.sketchCurves.sketchLines
    for i in range(len(p_cut)):
        lines_cut.addByTwoPoints(p_cut[i], p_cut[(i+1)%len(p_cut)])
        
    prof_cut = s_cut.profiles.item(0)
    ext_in2 = extrudes.createInput(prof_cut, adsk.fusion.FeatureOperations.CutFeatureOperation)
    ext_in2.setSymmetricExtent(adsk.core.ValueInput.createByReal(inner_half_w), False)
    ext2 = extrudes.add(ext_in2)

    # =========================================================================
    # STEP 3: Hook Bracket with Integrated Stiffening Gusset
    # =========================================================================
    s_hook = sketches.add(yzPlane)
    p_hook = [
        adsk.core.Point3D.create(0, 0.0, back_wall_h),
        adsk.core.Point3D.create(0, 0.0, hook_top_x),
        adsk.core.Point3D.create(0, -hook_inner_gap, hook_top_x),
        adsk.core.Point3D.create(0, -hook_inner_gap, hook_top_x - hook_lip_drop),
        adsk.core.Point3D.create(0, -hook_inner_gap - hook_th, hook_top_x - hook_lip_drop + 0.32), # 45 deg lead-in
        adsk.core.Point3D.create(0, -hook_inner_gap - hook_th, hook_top_x + hook_th),
        adsk.core.Point3D.create(0, hook_th, hook_top_x + hook_th),
        adsk.core.Point3D.create(0, hook_th, 3.80),           # straight arm down
        adsk.core.Point3D.create(0, 1.50, floor_back_x),      # 45 deg triangular gusset to floor
        adsk.core.Point3D.create(0, 0.30, floor_back_x),
        adsk.core.Point3D.create(0, 0.30, back_wall_h)
    ]
    lines_hook = s_hook.sketchCurves.sketchLines
    for i in range(len(p_hook)):
        lines_hook.addByTwoPoints(p_hook[i], p_hook[(i+1)%len(p_hook)])
        
    prof_hook = s_hook.profiles.item(0)
    ext_in3 = extrudes.createInput(prof_hook, adsk.fusion.FeatureOperations.JoinFeatureOperation)
    ext_in3.setSymmetricExtent(adsk.core.ValueInput.createByReal(hook_half_w), False)
    ext3 = extrudes.add(ext_in3)

    # =========================================================================
    # STEP 4: 11 Raised Drying Ribs Extruded Directly to Sloped Floor
    # =========================================================================
    body = comp.bRepBodies.item(0)
    candidates = [f for f in body.faces if f.evaluator.getNormalAtPoint(f.pointOnFace)[1].x > 0.8]
    floor_face = max(candidates, key=lambda f: f.area)

    pInput = cplanes.createInput()
    pInput.setByOffset(yzPlane, adsk.core.ValueInput.createByReal(rib_top_x))
    rib_plane = cplanes.add(pInput)

    s_ribs = comp.sketches.add(rib_plane)
    lines_r = s_ribs.sketchCurves.sketchLines

    rib_offsets_z = [0.0]
    for n in range(1, 6):
        rib_offsets_z.extend([n * rib_spacing, -n * rib_spacing])

    for oz in rib_offsets_z:
        y_start = 1.70 if abs(oz) < 1.9 else 0.80
        lx1 = -oz - half_rib_th
        lx2 = -oz + half_rib_th
        ly1 = y_start
        ly2 = 12.2

        p0 = adsk.core.Point3D.create(lx1, ly1, 0)
        p1 = adsk.core.Point3D.create(lx2, ly1, 0)
        p2 = adsk.core.Point3D.create(lx2, ly2, 0)
        p3 = adsk.core.Point3D.create(lx1, ly2, 0)
        lines_r.addByTwoPoints(p0, p1)
        lines_r.addByTwoPoints(p1, p2)
        lines_r.addByTwoPoints(p2, p3)
        lines_r.addByTwoPoints(p3, p0)

    prof_col = adsk.core.ObjectCollection.create()
    for i in range(s_ribs.profiles.count):
        prof_col.add(s_ribs.profiles.item(i))

    ext_rib_in = extrudes.createInput(prof_col, adsk.fusion.FeatureOperations.JoinFeatureOperation)
    ext_rib_in.setOneSideToExtent(floor_face, False)
    extrudes.add(ext_rib_in)

    # =========================================================================
    # STEP 5: Fillets on Rims & Rib Top Edges
    # =========================================================================
    body = comp.bRepBodies.item(0)

    # 1. Top rim fillet (1.0 mm)
    rim_edges = adsk.core.ObjectCollection.create()
    for e in body.edges:
        p1 = e.startVertex.geometry
        p2 = e.endVertex.geometry
        if abs(p1.x - back_wall_h) < 0.05 and abs(p2.x - back_wall_h) < 0.05:
            if abs(abs(p1.z) - half_w) < 0.05 or abs(abs(p2.z) - half_w) < 0.05 or (abs(p1.y) < 0.05 and abs(p2.y) < 0.05):
                rim_edges.add(e)
    if rim_edges.count > 0:
        try:
            fIn = fillets.createInput()
            fIn.addConstantRadiusEdgeSet(rim_edges, adsk.core.ValueInput.createByReal(0.10), True)
            fillets.add(fIn)
        except Exception:
            pass

    # 2. Rib top edge fillets (0.4 mm)
    rib_top_edges = adsk.core.ObjectCollection.create()
    for e in body.edges:
        p1 = e.startVertex.geometry
        p2 = e.endVertex.geometry
        if abs(p1.x - rib_top_x) < 0.02 and abs(p2.x - rib_top_x) < 0.02:
            if abs(p1.y - p2.y) > 2.0:
                rib_top_edges.add(e)
    if rib_top_edges.count > 0:
        try:
            fIn = fillets.createInput()
            fIn.addConstantRadiusEdgeSet(rib_top_edges, adsk.core.ValueInput.createByReal(0.04), True)
            fillets.add(fIn)
        except Exception:
            pass

    # =========================================================================
    # STEP 6: Material / Appearance
    # =========================================================================
    try:
        matLib = app.materialLibraries.itemByName("Fusion Appearance Library")
        app_target = None
        for a in matLib.appearances:
            if "Plastic" in a.name and "White" in a.name:
                app_target = a
                break
        if app_target:
            doc_app = design.appearances.addByCopy(app_target, "Drainer_White_Plastic")
            body.appearance = doc_app
    except Exception:
        pass

    # =========================================================================
    # STEP 7: Export Files (STL, STEP, F3D)
    # =========================================================================
    exportMgr = design.exportManager
    target_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in locals() else "c:/Users/root/Downloads/Fusion360-MCP"
    
    stl_path = os.path.join(target_dir, "KitchenSink_CoffeeDrainer_140mm.stl")
    stlOptions = exportMgr.createSTLExportOptions(body, stl_path)
    stlOptions.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
    exportMgr.execute(stlOptions)
    
    step_path = os.path.join(target_dir, "KitchenSink_CoffeeDrainer_140mm.step")
    stepOptions = exportMgr.createSTEPExportOptions(step_path, comp)
    exportMgr.execute(stepOptions)
    
    f3d_path = os.path.join(target_dir, "KitchenSink_CoffeeDrainer_140mm.f3d")
    f3dOptions = exportMgr.createFusionArchiveExportOptions(f3d_path)
    exportMgr.execute(f3dOptions)
    
    bbox = body.boundingBox
    w_mm = (bbox.maxPoint.z - bbox.minPoint.z) * 10
    d_mm = (bbox.maxPoint.y - bbox.minPoint.y) * 10
    h_mm = (bbox.maxPoint.x - bbox.minPoint.x) * 10
    vol_cm3 = body.volume
    
    print(f"Drainer successfully built and exported:")
    print(f"Width: {w_mm:.1f} mm, Depth: {d_mm:.1f} mm, Height: {h_mm:.1f} mm, Volume: {vol_cm3:.1f} cm3")

if __name__ == "__main__":
    pass
