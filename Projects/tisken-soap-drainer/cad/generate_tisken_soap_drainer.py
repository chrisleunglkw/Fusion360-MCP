"""
Autodesk Fusion 360 - Japanese Minimalist ("Hamon" Zen Ripple) Soap Drainer
For IKEA TISKEN Corner Basket (7.5 - 8.0 mm front beam)
Features:
- 110mm round chamfered outer ring (2.8mm wall, 10.5mm height)
- 100% hollow open bottom with concentric Zen ripple rings (Ø64mm & Ø24mm)
- 6 slender radial spokes (2.2mm wide, 3.4mm tall)
- Extra-slim 18mm chamfered cantilever hook bracket (8.5mm throat gap)
"""

import adsk.core
import adsk.fusion
import math

def run(_context: str):
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    rootComp = design.rootComponent
    
    occ = rootComp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = "IKEA_TISKEN_Japanese_Minimalist_Soap_Drainer"
    
    sketches = comp.sketches
    extrudes = comp.features.extrudeFeatures
    fillets = comp.features.filletFeatures
    
    xyPlane = comp.xYConstructionPlane
    yzPlane = comp.yZConstructionPlane
    
    # Dimensions (Fusion API uses cm: 1 cm = 10 mm)
    dish_outer_rad = 5.50      # 110 mm outer diameter
    wall_th = 0.28             # 2.8 mm outer rim wall
    dish_inner_rad = dish_outer_rad - wall_th # 5.22 cm
    dish_h = 1.05              # 10.5 mm height
    
    lattice_h = 0.34           # 3.4 mm rib height
    rib_w = 0.22               # 2.2 mm rib width
    mid_r_out = 3.20           # Ø64 mm middle ripple ring
    mid_r_in = mid_r_out - rib_w
    cen_r_out = 1.20           # Ø24 mm center ripple ring
    cen_r_in = cen_r_out - rib_w
    
    # Hook parameters (18 mm slim width, 8.5 mm throat)
    hook_gap = 0.85
    hook_h = 2.20
    hook_w = 1.80
    half_hook_w = hook_w / 2.0
    hook_th = 0.30
    hook_lip_drop = 1.50
    neck_offset = 0.60
    
    # 1. Concentric Rings (Outer + Middle + Center)
    s_rings = sketches.add(xyPlane)
    circles = s_rings.sketchCurves.sketchCircles
    circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), dish_outer_rad)
    circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), dish_inner_rad)
    circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), mid_r_out)
    circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), mid_r_in)
    circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), cen_r_out)
    circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), cen_r_in)
    
    # Sort annular profiles by outer radius / area
    profs = sorted(
        [s_rings.profiles.item(i) for i in range(s_rings.profiles.count)],
        key=lambda p: p.areaProperties().area
    )
    # Outer ring, middle ring, inner ring (skip center hole & large void gaps)
    # Using exact area matching:
    outer_area = math.pi * (dish_outer_rad**2 - dish_inner_rad**2)
    mid_area = math.pi * (mid_r_out**2 - mid_r_in**2)
    cen_area = math.pi * (cen_r_out**2 - cen_r_in**2)
    
    for p in profs:
        a = p.areaProperties().area
        if abs(a - outer_area) < 0.5:
            ext = extrudes.createInput(p, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            ext.setDistanceExtent(False, adsk.core.ValueInput.createByReal(dish_h))
            extrudes.add(ext)
        elif abs(a - mid_area) < 0.3 or abs(a - cen_area) < 0.3:
            ext = extrudes.createInput(p, adsk.fusion.FeatureOperations.JoinFeatureOperation)
            ext.setDistanceExtent(False, adsk.core.ValueInput.createByReal(lattice_h))
            extrudes.add(ext)
            
    # 2. 6 Radial Spokes at 60 deg intervals
    s_spokes = sketches.add(xyPlane)
    ls = s_spokes.sketchCurves.sketchLines
    half_rw = rib_w / 2.0
    r_start = cen_r_in
    r_end = dish_inner_rad + 0.12
    for i in range(6):
        ang = math.radians(i * 60.0 + 30.0)
        ca, sa = math.cos(ang), math.sin(ang)
        nx, ny = -sa * half_rw, ca * half_rw
        p0 = adsk.core.Point3D.create(r_start * ca - nx, r_start * sa - ny, 0)
        p1 = adsk.core.Point3D.create(r_end * ca - nx, r_end * sa - ny, 0)
        p2 = adsk.core.Point3D.create(r_end * ca + nx, r_end * sa + ny, 0)
        p3 = adsk.core.Point3D.create(r_start * ca + nx, r_start * sa + ny, 0)
        ls.addByTwoPoints(p0, p1)
        ls.addByTwoPoints(p1, p2)
        ls.addByTwoPoints(p2, p3)
        ls.addByTwoPoints(p3, p0)
        
    for i in range(s_spokes.profiles.count):
        ext_sp = extrudes.createInput(s_spokes.profiles.item(i), adsk.fusion.FeatureOperations.JoinFeatureOperation)
        ext_sp.setDistanceExtent(False, adsk.core.ValueInput.createByReal(lattice_h))
        extrudes.add(ext_sp)
        
    # 3. Slim Cantilever Hook Bracket (18 mm width)
    s_hook = sketches.add(yzPlane)
    lh = s_hook.sketchCurves.sketchLines
    
    y_attach = -dish_outer_rad + 0.18
    y_front_rail = -dish_outer_rad - neck_offset
    y_back_rail = y_front_rail - hook_gap
    y_lip_outer = y_back_rail - hook_th
    
    z_dish_top = dish_h
    z_rail_top = z_dish_top + hook_h
    z_hook_top = z_rail_top + hook_th
    z_lip_end = z_rail_top - hook_lip_drop
    
    hp = [
        (y_attach, z_dish_top - 0.22),
        (y_attach, z_dish_top - 0.05),
        (y_front_rail + hook_th, z_dish_top + 0.65),
        (y_front_rail + hook_th, z_hook_top - 0.12),
        (y_front_rail + hook_th - 0.12, z_hook_top),
        (y_lip_outer + 0.12, z_hook_top),
        (y_lip_outer, z_hook_top - 0.12),
        (y_lip_outer, z_lip_end + 0.25),
        (y_lip_outer + 0.18, z_lip_end),
        (y_back_rail, z_lip_end + 0.25),
        (y_back_rail, z_rail_top),
        (y_front_rail, z_rail_top),
        (y_front_rail, 0.28),
        (y_front_rail - 0.12, 0.14),
        (y_front_rail - 0.12, 0.0),
        (y_attach, 0.0),
        (y_attach, 0.28)
    ]
    
    for i in range(len(hp)):
        p_start = adsk.core.Point3D.create(0, hp[i][0], hp[i][1])
        p_next = adsk.core.Point3D.create(0, hp[(i+1)%len(hp)][0], hp[(i+1)%len(hp)][1])
        lh.addByTwoPoints(p_start, p_next)
        
    prof_hook = s_hook.profiles.item(0)
    ext_hook_in = extrudes.createInput(prof_hook, adsk.fusion.FeatureOperations.JoinFeatureOperation)
    ext_hook_in.setSymmetricExtent(adsk.core.ValueInput.createByReal(half_hook_w), True)
    extrudes.add(ext_hook_in)
    
    print("Japanese Minimalist Soap Drainer created successfully in Fusion 360!")

if __name__ == "__main__":
    run("")
