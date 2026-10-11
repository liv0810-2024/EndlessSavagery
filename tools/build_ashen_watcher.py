"""Build the Ashen Watcher player model and export it for Tuanjie/Unity.

Run with Blender 5.2: blender -b -t 4 --python tools/build_ashen_watcher.py
The script creates an editable .blend, a game FBX, and two review renders.
"""

import math
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "ArtSource" / "AshenWatcher"
EXPORT = ROOT / "Assets" / "Characters" / "AshenWatcher"
SOURCE.mkdir(parents=True, exist_ok=True)
EXPORT.mkdir(parents=True, exist_ok=True)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)


def mat(name, color, metallic=0.0, roughness=0.7, emission=None):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if emission:
        bsdf.inputs["Emission Color"].default_value = (*color, 1)
        bsdf.inputs["Emission Strength"].default_value = emission
    elif name != "07 Mask shadow":
        # Fine surface relief is kept in the .blend; diffuse colors survive FBX export.
        noise = m.node_tree.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 95 if metallic else 125
        noise.inputs["Detail"].default_value = 3
        bump = m.node_tree.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.12 if metallic else 0.22
        bump.inputs["Distance"].default_value = 0.006
        m.node_tree.links.new(noise.outputs["Fac"], bump.inputs["Height"])
        m.node_tree.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return m


cloth = mat("01 Charcoal cloth", (0.042, 0.047, 0.061))
cloak = mat("02 Weathered cloak", (0.052, 0.054, 0.066))
leather = mat("03 Oiled leather", (0.085, 0.059, 0.052))
plate = mat("04 Blackened steel", (0.105, 0.115, 0.13), 0.72, 0.47)
edge = mat("05 Antique bronze", (0.33, 0.21, 0.11), 0.72, 0.39)
silver = mat("06 Pale steel", (0.47, 0.50, 0.55), 0.75, 0.29)
dark = mat("07 Mask shadow", (0.015, 0.019, 0.027))
red = mat("08 Worn crimson lining", (0.17, 0.027, 0.035))
glow = mat("09 Arcane violet", (0.26, 0.10, 0.75), 0.1, 0.25, 2.5)


def add_color_texture(material, stem, base, kind):
    """Make a small reusable tile; unlike shader-only noise it follows the FBX."""
    tex_dir = EXPORT / "Textures"
    tex_dir.mkdir(parents=True, exist_ok=True)
    size = 256
    image = bpy.data.images.new(stem, width=size, height=size, alpha=True)
    pixels = [0.0] * (size * size * 4)
    for y in range(size):
        v = y / size
        for x in range(size):
            u = x / size
            broad = math.sin(2 * math.pi * (u * 3 + 0.18 * math.sin(v * 2 * math.pi)))
            broad *= math.cos(2 * math.pi * v * 4)
            fine = math.sin(2 * math.pi * (u * 39 + v * 21)) * math.cos(2 * math.pi * (v * 53 - u * 12))
            grain = 0.07 * broad + 0.035 * fine
            if kind == "cloth":
                weave = 0.026 * math.sin(2 * math.pi * u * 48) * math.sin(2 * math.pi * v * 48)
                variation = 0.9 + grain + weave
            elif kind == "metal":
                hairline = 0.04 * math.sin(2 * math.pi * (v * 57 + u * 7))
                variation = 0.91 + grain + hairline
            elif kind == "leather":
                variation = 0.9 + grain * 1.6
            else:
                variation = 0.94 + grain
            offset = (y * size + x) * 4
            for channel in range(3):
                pixels[offset + channel] = max(0.0, min(1.0, base[channel] * variation))
            pixels[offset + 3] = 1.0
    image.pixels.foreach_set(pixels)
    image.filepath_raw = str(tex_dir / (stem + ".png"))
    image.file_format = "PNG"
    image.save()
    node = material.node_tree.nodes.new("ShaderNodeTexImage")
    node.image = image
    node.interpolation = "Linear"
    material.node_tree.links.new(node.outputs["Color"],
                             material.node_tree.nodes["Principled BSDF"].inputs["Base Color"])


for material, stem, base, kind in [
    (cloth, "charcoal_fabric", (0.055, 0.060, 0.073), "cloth"),
    (cloak, "weathered_cloak", (0.062, 0.064, 0.074), "cloth"),
    (leather, "aged_leather", (0.095, 0.064, 0.055), "leather"),
    (plate, "blackened_steel", (0.123, 0.132, 0.147), "metal"),
    (edge, "aged_bronze", (0.34, 0.22, 0.118), "metal"),
    (silver, "pale_steel", (0.46, 0.49, 0.53), "metal"),
    (red, "crimson_lining", (0.19, 0.034, 0.04), "cloth"),
]:
    add_color_texture(material, stem, base, kind)

body_parts = []


def keep(obj, material):
    obj.data.materials.append(material)
    body_parts.append(obj)
    return obj


def bevel(obj, amount=0.012, segments=1):
    mod = obj.modifiers.new("Soft edges", "BEVEL")
    mod.width = amount
    mod.segments = segments
    mod.affect = "EDGES"
    mod2 = obj.modifiers.new("Weighted face normals", "WEIGHTED_NORMAL")
    mod2.keep_sharp = True
    return obj


def cube(name, loc, scale, material, bevel_size=0.0, rotation=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if rotation:
        o.rotation_euler = rotation
    if bevel_size:
        bevel(o, bevel_size)
    return keep(o, material)


def ellipsoid(name, loc, scale, material, segments=16, rings=8):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return keep(o, material)


def cone(name, loc, radius1, radius2, depth, material, vertices=10):
    bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=radius1, radius2=radius2, depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    return keep(o, material)


def bone(name, a, b, radius, material, verts=10, radius_end=None):
    a, b = Vector(a), Vector(b)
    direction = b - a
    bpy.ops.mesh.primitive_cone_add(
        vertices=verts,
        radius1=radius,
        radius2=radius if radius_end is None else radius_end,
        depth=direction.length,
        location=(a + b) / 2,
    )
    o = bpy.context.object
    o.name = name
    o.rotation_euler = direction.to_track_quat("Z", "Y").to_euler()
    return keep(o, material)


def poly(name, vertices, faces, material, solidify=0):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(o)
    if solidify:
        m = o.modifiers.new("Garment thickness", "SOLIDIFY")
        m.thickness = solidify
    return keep(o, material)


def ring_loft(name, rings, material, cap=True):
    """Mesh a sequence of equally sampled 3D rings, useful for shaped armor."""
    n = len(rings[0])
    verts = [v for ring in rings for v in ring]
    faces = []
    for j in range(len(rings) - 1):
        for i in range(n):
            ni = (i + 1) % n
            faces.append((j * n + i, j * n + ni, (j + 1) * n + ni, (j + 1) * n + i))
    if cap:
        faces.append(tuple(reversed(range(n))))
        faces.append(tuple((len(rings) - 1) * n + i for i in range(n)))
    o = poly(name, verts, faces, material)
    bevel(o, 0.006, 2)
    return o


def ellipse_ring(cx, cy, z, rx, ry, count=16):
    return [(cx + rx * math.cos(i * 2 * math.pi / count),
             cy + ry * math.sin(i * 2 * math.pi / count), z) for i in range(count)]


def shield(name, points, material, thickness=0.018, bevel_width=0.008):
    o = poly(name, points, [tuple(range(len(points)))], material, thickness)
    if bevel_width:
        bevel(o, bevel_width, 2)
    return o


def curve(name, points, material, bevel_depth):
    data = bpy.data.curves.new(name, "CURVE")
    data.dimensions = "3D"
    data.resolution_u = 1
    data.bevel_depth = bevel_depth
    data.resolution_u = 2
    data.bevel_resolution = 1
    spline = data.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for p, xyz in zip(spline.points, points):
        p.co = (*xyz, 1)
    o = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(o)
    return keep(o, material)


# The origin is on the ground. Blender -Y is front. Total height is 2.06 m.
for s in (-1, 1):
    x = s * 0.155
    # Tapered boots, shaped shin armor and cloth trousers.
    ellipsoid(f"{s} boot sole", (x, -0.071, 0.055), (0.112, 0.200, 0.052), dark, 20, 10)
    ring_loft(f"{s} boot upper", [
        ellipse_ring(x, -0.067, 0.075, 0.105, 0.188),
        ellipse_ring(x, -0.044, 0.155, 0.106, 0.155),
        ellipse_ring(x, 0, 0.254, 0.087, 0.105),
    ], leather)
    shield(f"{s} steel toe", [(x - 0.085, -0.195, 0.095), (x, -0.255, 0.12),
                              (x + 0.085, -0.195, 0.095), (x + 0.072, -0.145, 0.177),
                              (x - 0.072, -0.145, 0.177)], plate, 0.012)
    curve(f"{s} boot toe bronze", [(x - 0.082, -0.20, 0.103), (x, -0.256, 0.127),
                                   (x + 0.082, -0.20, 0.103)], edge, 0.006)
    ring_loft(f"{s} shaped greave", [
        ellipse_ring(x, 0.005, 0.23, 0.084, 0.095),
        ellipse_ring(x, 0.005, 0.43, 0.098, 0.105),
        ellipse_ring(x, 0.005, 0.59, 0.12, 0.118),
        ellipse_ring(x, 0.006, 0.64, 0.105, 0.108),
    ], plate)
    shield(f"{s} greave spine", [(x - 0.065, -0.10, 0.28), (x, -0.134, 0.245),
                                 (x + 0.065, -0.10, 0.28), (x + 0.078, -0.120, 0.55),
                                 (x, -0.143, 0.61), (x - 0.078, -0.120, 0.55)], silver, 0.007)
    for z in (0.315, 0.475):
        curve(f"{s} greave strap {z}", [(x - 0.10, -0.02, z), (x - 0.09, -0.115, z - 0.012),
                                      (x + 0.09, -0.115, z - 0.012), (x + 0.10, -0.02, z)], leather, 0.016)
        cube(f"{s} strap rivet {z}", (x + 0.09, -0.115, z - 0.012), (0.018, 0.012, 0.018), edge, 0.003)
    shield(f"{s} pointed knee", [(x - 0.095, -0.108, 0.68), (x, -0.165, 0.725),
                                 (x + 0.095, -0.108, 0.68), (x + 0.087, -0.14, 0.62),
                                 (x, -0.168, 0.586), (x - 0.087, -0.14, 0.62)], plate, 0.025)
    curve(f"{s} knee bronze V", [(x - 0.082, -0.145, 0.67), (x, -0.188, 0.615),
                                 (x + 0.082, -0.145, 0.67)], edge, 0.008)
    ring_loft(f"{s} trouser leg", [
        ellipse_ring(x, 0.01, 0.70, 0.117, 0.111),
        ellipse_ring(x, 0.006, 0.90, 0.131, 0.135),
        ellipse_ring(s * 0.142, 0.004, 1.11, 0.151, 0.147),
    ], cloth)
    shield(f"{s} thigh leather flap", [(x - 0.088, -0.129, 1.07), (x + 0.093, -0.129, 1.07),
                                       (x + 0.102, -0.144, 0.86), (x, -0.162, 0.79),
                                       (x - 0.092, -0.144, 0.86)], leather, 0.012)
    curve(f"{s} thigh seam", [(x - 0.08, -0.146, 1.05), (x - 0.08, -0.156, 0.87),
                              (x, -0.176, 0.8)], edge, 0.004)

    # Long narrow sleeves and shaped forearm bracers preserve the A-pose.
    shoulder = (s * 0.31, 0, 1.57)
    elbow = (s * 0.44, -0.005, 1.32)
    wrist = (s * 0.55, -0.025, 1.085)
    bone(f"{s} upper sleeve", shoulder, elbow, 0.092, cloth, 14, 0.074)
    bone(f"{s} elbow leather", (s * 0.425, -0.005, 1.35), (s * 0.46, -0.008, 1.275), 0.078, leather, 14)
    bone(f"{s} forearm sleeve", elbow, wrist, 0.072, cloth, 14, 0.057)
    bone(f"{s} tapered vambrace", (s * 0.475, -0.009, 1.25), (s * 0.54, -0.024, 1.105), 0.077, plate, 12, 0.056)
    curve(f"{s} vambrace gold line", [(s * 0.49, -0.08, 1.22), (s * 0.50, -0.09, 1.19),
                                      (s * 0.54, -0.076, 1.13)], edge, 0.006)
    for z in (1.115, 1.235):
        bone(f"{s} cuff {z}", (s * (0.545 if z < 1.2 else 0.48), -0.01, z - 0.01),
             (s * (0.555 if z < 1.2 else 0.49), -0.01, z + 0.01), 0.078, leather, 12)
    ellipsoid(f"{s} glove palm", (s * 0.585, -0.035, 1.018), (0.058, 0.055, 0.092), leather, 16, 8)
    for i in range(4):
        fy = -0.07 + i * 0.025
        bone(f"{s} glove finger {i}", (s * (0.59 + (i - 1.5) * 0.007), fy, 0.963),
             (s * (0.61 + (i - 1.5) * 0.008), fy, 0.907 + abs(i - 1.5) * 0.007),
             0.012, leather, 8, 0.009)

# Tailored torso and layered cuirass: narrow waist, relatively broad shoulders.
ring_loft("Tapered charcoal tunic", [
    ellipse_ring(0, 0.015, 1.04, 0.245, 0.17),
    ellipse_ring(0, 0.014, 1.20, 0.215, 0.155),
    ellipse_ring(0, 0.005, 1.43, 0.27, 0.185),
    ellipse_ring(0, 0, 1.60, 0.315, 0.19),
    ellipse_ring(0, 0, 1.67, 0.23, 0.16),
], cloth)
ellipsoid("Short neck and cowl", (0, 0.01, 1.675), (0.145, 0.145, 0.085), cloak, 20, 10)
for s in (-1, 1):
    shield(f"{s} fitted upper cuirass", [(0, -0.205, 1.61), (s * 0.24, -0.19, 1.62),
                                        (s * 0.283, -0.195, 1.47), (s * 0.16, -0.235, 1.38),
                                        (s * 0.025, -0.237, 1.42)], plate, 0.022)
    shield(f"{s} lower cuirass lame", [(s * 0.025, -0.215, 1.42), (s * 0.16, -0.216, 1.38),
                                       (s * 0.22, -0.186, 1.28), (s * 0.15, -0.20, 1.22),
                                       (0, -0.209, 1.24)], plate, 0.018)
    curve(f"{s} chest bronze rim", [(0, -0.231, 1.612), (s * 0.23, -0.21, 1.62),
                                    (s * 0.274, -0.211, 1.47)], edge, 0.007)
    curve(f"{s} belly plate seam", [(s * 0.02, -0.232, 1.405), (s * 0.16, -0.235, 1.37),
                                    (s * 0.22, -0.205, 1.28)], edge, 0.004)
    for z in (1.285, 1.38, 1.53):
        cube(f"{s} chest rivet {z}", (s * 0.215, -0.218, z), (0.015, 0.008, 0.015), edge, 0.002)

# Restrained branching fissures follow the armor seams rather than forming a badge.
curve("Violet chest main fissure", [(-0.045, -0.247, 1.585), (0.01, -0.248, 1.535),
                                    (-0.018, -0.252, 1.49), (0.042, -0.254, 1.44),
                                    (0.018, -0.246, 1.405)], glow, 0.004)
curve("Violet chest fork", [(0.011, -0.25, 1.535), (0.072, -0.241, 1.55),
                            (0.095, -0.24, 1.52)], glow, 0.003)
curve("Violet chest lower fork", [(0.04, -0.255, 1.444), (0.10, -0.235, 1.462)], glow, 0.002)

# Diagonal leather bandolier, three narrow belts and a layered split skirt.
curve("Leather diagonal cross strap", [(-0.21, -0.218, 1.65), (-0.12, -0.25, 1.51),
                                       (0.025, -0.258, 1.39), (0.18, -0.232, 1.20)], leather, 0.028)
for z, width in [(1.16, 0.052), (1.09, 0.039), (1.02, 0.035)]:
    ring_loft(f"Waist belt {z}", [ellipse_ring(0, 0.008, z - width / 2, 0.252, 0.179),
                                 ellipse_ring(0, 0.008, z + width / 2, 0.252, 0.179)], leather)
    cube(f"Belt buckle {z}", (0.065 if z != 1.16 else -0.06, -0.181, z),
         (0.068, 0.018, width * 1.1), edge, 0.007)
for s in (-1, 1):
    shield(f"{s} inner red skirt", [(s * 0.025, -0.165, 1.04), (s * 0.275, -0.145, 1.02),
                                   (s * 0.31, -0.13, 0.68), (s * 0.205, -0.17, 0.57),
                                   (s * 0.14, -0.19, 0.67), (s * 0.06, -0.175, 0.55)], red, 0.008)
    shield(f"{s} leather skirt overlay", [(s * 0.035, -0.184, 1.05), (s * 0.245, -0.175, 1.05),
                                           (s * 0.275, -0.17, 0.77), (s * 0.17, -0.19, 0.66),
                                           (s * 0.095, -0.202, 0.75)], leather, 0.016)
    curve(f"{s} skirt gilded edge", [(s * 0.245, -0.19, 1.035), (s * 0.275, -0.188, 0.77),
                                     (s * 0.17, -0.208, 0.66)], edge, 0.007)
    for z in (1.00, 0.90):
        cube(f"{s} skirt stud {z}", (s * 0.225, -0.199, z), (0.014, 0.008, 0.014), edge, 0.002)

# Overlapping angular pauldrons replace the round shoulder masses.
for s in (-1, 1):
    width = 0.195 if s == 1 else 0.15
    shield(f"{s} shoulder first scale", [(s * 0.22, -0.08, 1.67), (s * 0.36, -0.15, 1.69),
                                         (s * (0.36 + width), -0.09, 1.59),
                                         (s * 0.43, -0.145, 1.52), (s * 0.29, -0.147, 1.56)],
           plate if s == 1 else leather, 0.035)
    shield(f"{s} shoulder lower scale", [(s * 0.30, -0.155, 1.55), (s * 0.46, -0.154, 1.51),
                                         (s * 0.475, -0.125, 1.44), (s * 0.35, -0.172, 1.46)],
           plate, 0.022)
    curve(f"{s} shoulder rim", [(s * 0.22, -0.099, 1.675), (s * 0.36, -0.173, 1.695),
                                (s * (0.36 + width), -0.111, 1.595)], edge, 0.009)
    curve(f"{s} lower shoulder rim", [(s * 0.30, -0.178, 1.55), (s * 0.46, -0.18, 1.51)], edge, 0.006)
    for px, pz in ((0.32, 1.65), (0.43, 1.55)):
        cube(f"{s} shoulder rivet {px}", (s * px, -0.174, pz), (0.016, 0.012, 0.016), edge, 0.003)

# A genuinely open, peaked cloth hood. The face is inset in darkness.
ellipsoid("Layered neck cowl", (0, 0.013, 1.68), (0.22, 0.195, 0.10), cloak, 24, 12)
ellipsoid("Shadowed head inside hood", (0, -0.025, 1.85), (0.135, 0.135, 0.19), dark, 24, 12)
hood_rings = []
for z, rx, ry, cy, opening in [(1.70, 0.219, 0.183, 0.044, 0.55),
                                (1.79, 0.220, 0.206, 0.038, 0.70),
                                (1.91, 0.222, 0.209, 0.023, 0.65),
                                (2.015, 0.164, 0.174, 0.048, 0.19),
                                (2.065, 0.070, 0.088, 0.080, 0.0),
                                (2.095, 0.013, 0.022, 0.092, 0.0)]:
    ring = []
    for i in range(25):
        a = -math.pi / 2 + opening + i * (2 * math.pi - 2 * opening) / 24
        ring.append((rx * math.cos(a), cy + ry * math.sin(a) + 0.008 * math.sin(i * 0.9 + z * 7), z))
    hood_rings.append(ring)
hood_verts = [v for row in hood_rings for v in row]
hood_faces = [(j * 25 + i, j * 25 + i + 1, (j + 1) * 25 + i + 1, (j + 1) * 25 + i)
              for j in range(len(hood_rings) - 1) for i in range(24)]
hood_obj = poly("Open draped hood", hood_verts, hood_faces, cloak, 0.025)
for face in hood_obj.data.polygons:
    face.use_smooth = True
shield("Pointed overhanging hood brow", [(-0.18, -0.145, 1.975), (0, -0.255, 2.051),
                                         (0.18, -0.145, 1.975), (0.128, -0.205, 1.921),
                                         (0, -0.285, 1.995), (-0.128, -0.205, 1.921)], cloak, 0.018)
curve("Hood stitched brow", [(-0.128, -0.218, 1.932), (0, -0.29, 2.004),
                              (0.128, -0.218, 1.932)], edge, 0.006)
for s in (-1, 1):
    shield(f"{s} hanging hood cheek", [(s * 0.145, -0.183, 1.934), (s * 0.215, -0.112, 1.929),
                                       (s * 0.235, -0.105, 1.727), (s * 0.145, -0.19, 1.667),
                                       (s * 0.126, -0.23, 1.768)], cloak, 0.02)
    curve(f"{s} hood opening bronze", [(s * 0.13, -0.225, 1.927),
                                       (s * 0.155, -0.232, 1.817),
                                       (s * 0.145, -0.217, 1.716)], edge, 0.005)
    curve(f"{s} hood stitched fold", [(s * 0.17, 0.001, 2.005),
                                      (s * 0.225, 0.052, 1.855),
                                      (s * 0.20, 0.145, 1.732)], leather, 0.004)

# Narrow beaked metal mask and tiny angled eye slits.
shield("Narrow forged face mask", [(-0.097, -0.145, 1.924), (0.097, -0.145, 1.924),
                                   (0.123, -0.161, 1.798), (0.067, -0.174, 1.724),
                                   (0, -0.210, 1.697), (-0.067, -0.174, 1.724),
                                   (-0.123, -0.161, 1.798)], plate, 0.012)
shield("Long angular nose ridge", [(-0.018, -0.175, 1.918), (0.018, -0.175, 1.918),
                                   (0.026, -0.202, 1.790), (0, -0.23, 1.728),
                                   (-0.026, -0.202, 1.790)], edge, 0.007)
for s in (-1, 1):
    curve(f"{s} mask cheek bronze", [(s * 0.105, -0.186, 1.886),
                                     (s * 0.112, -0.189, 1.803),
                                     (s * 0.057, -0.197, 1.738)], edge, 0.004)
    curve(f"{s} violet eye slit", [(s * 0.035, -0.195, 1.861),
                                   (s * 0.090, -0.190, 1.847)], glow, 0.006)

# Three long folded cloak panels make a readable dark triangular back silhouette.
for panel in (-1, 0, 1):
    cx = panel * 0.22
    bottom = 0.50 if panel == 0 else (0.62 if panel == -1 else 0.55)
    rows = []
    for row, (z, width, y) in enumerate([(1.67, 0.16, 0.116), (1.48, 0.195, 0.184),
                                        (1.17, 0.235, 0.235), (0.85, 0.265, 0.283),
                                        (bottom + 0.08, 0.285, 0.31)]):
        rows.append([(cx + width * (i - 3) / 3,
                      y + 0.027 * math.cos(i * math.pi / 3 + panel),
                      z + (0.014 * math.cos(i * 2.2) if row > 0 else 0)) for i in range(7)])
    # Individual uneven hem points keep the panel from ending in a straight line.
    rows.append([(cx + 0.29 * (i - 3) / 3,
                  0.325 + 0.028 * math.cos(i * math.pi / 3 + panel),
                  bottom + [0.065, -0.10, 0.035, -0.06, 0.07, -0.035, 0.095][i]) for i in range(7)])
    verts = [p for row in rows for p in row]
    faces = [(j * 7 + i, j * 7 + i + 1, (j + 1) * 7 + i + 1, (j + 1) * 7 + i)
             for j in range(len(rows) - 1) for i in range(6)]
    poly(f"Folded ragged cloak panel {panel}", verts, faces, cloak, 0.015)
    curve(f"Cloak vertical stitch {panel}", [rows[k][2] for k in (0, 1, 2, 3, 4)],
          leather, 0.004)
    for i in (1, 5):
        curve(f"Cloak fold highlight {panel} {i}", [rows[k][i] for k in (1, 2, 3, 4)],
              cloth, 0.005)
    # Crimson lining peeks through tears below the charcoal hem.
    for j in (1, 4):
        x = cx + 0.29 * (j - 3) / 3
        shield(f"Crimson hem tear {panel} {j}", [(x - 0.035, 0.326, bottom + 0.10),
                                                   (x + 0.045, 0.326, bottom + 0.10),
                                                   (x + 0.015, 0.342, bottom - 0.14)], red, 0.004, 0)

# Front shoulder mantle and long side tails frame the chest without covering it.
for s in (-1, 1):
    shield(f"{s} cowl shoulder mantle", [(s * 0.12, 0.04, 1.74), (s * 0.31, 0.02, 1.68),
                                        (s * 0.46, 0.02, 1.59), (s * 0.37, -0.08, 1.48),
                                        (s * 0.28, -0.13, 1.55), (s * 0.12, -0.12, 1.65)],
           cloak, 0.017)
    shield(f"{s} long side cloak", [(s * 0.34, 0.02, 1.57), (s * 0.44, 0.08, 1.54),
                                   (s * 0.40, 0.20, 1.10), (s * 0.44, 0.25, 0.58),
                                   (s * 0.32, 0.24, 0.44), (s * 0.29, 0.16, 0.58),
                                   (s * 0.27, 0.08, 1.08)], cloak, 0.013)
    shield(f"{s} side crimson lining", [(s * 0.36, 0.232, 0.70), (s * 0.43, 0.263, 0.66),
                                       (s * 0.33, 0.258, 0.37)], red, 0.006, 0)
    curve(f"{s} side cloak seam", [(s * 0.31, 0.12, 1.49), (s * 0.35, 0.217, 1.05),
                                   (s * 0.36, 0.255, 0.61)], leather, 0.006)
curve("Back cloak sigil outer", [(-0.095, 0.225, 1.46), (0, 0.25, 1.51),
                                  (0.095, 0.225, 1.46), (0, 0.258, 1.37),
                                  (-0.095, 0.225, 1.46)], edge, 0.006)
curve("Back cloak sigil spine", [(0, 0.255, 1.52), (0, 0.262, 1.20),
                                  (0, 0.304, 0.91)], edge, 0.005)

# Sword is sheathed against the hip so the idle silhouette remains compact.
bone("Sword sheath", (-0.29, -0.08, 0.62), (-0.39, -0.08, 1.15), 0.041, dark, 8, 0.045)
bone("Sword steel", (-0.30, -0.092, 0.67), (-0.38, -0.092, 1.10), 0.017, silver, 4, 0.018)
bone("Sword grip", (-0.39, -0.08, 1.12), (-0.43, -0.08, 1.36), 0.035, leather, 8)
bone("Sword pommel", (-0.43, -0.08, 1.35), (-0.44, -0.08, 1.40), 0.047, edge, 8)
bone("Sword crossguard", (-0.50, -0.08, 1.13), (-0.27, -0.08, 1.16), 0.025, edge, 6)
curve("Sword magical edge", [(-0.31, -0.132, 0.78), (-0.36, -0.132, 1.04)], glow, 0.005)

# Single root transform makes the exported model straightforward to parent to Player.
root = bpy.data.objects.new("AshenWatcher_Model", None)
bpy.context.collection.objects.link(root)
for obj in body_parts:
    obj.parent = root

# Bevels and curves are baked before FBX export for reliable Unity import.
bpy.ops.object.select_all(action="DESELECT")
for obj in body_parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = body_parts[0]
for obj in list(body_parts):
    bpy.context.view_layer.objects.active = obj
    if obj.type == "CURVE":
        bpy.ops.object.convert(target="MESH")
    elif obj.type == "MESH":
        for mod in list(obj.modifiers):
            bpy.ops.object.modifier_apply(modifier=mod.name)

# Every part gets UVs so the material color textures are visible in Blender and Tuanjie.
for obj in body_parts:
    if obj.type != "MESH" or len(obj.data.polygons) == 0:
        continue
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(island_margin=0.025)
    bpy.ops.object.mode_set(mode="OBJECT")

# Store a useful artist view in the .blend and render two review angles.
world = bpy.context.scene.world
world.color = (0.22, 0.23, 0.26)
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.22, 0.23, 0.26, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.6

def camera(name, location, target, ortho):
    bpy.ops.object.camera_add(location=location)
    o = bpy.context.object
    o.name = name
    o.rotation_euler = (Vector(target) - o.location).to_track_quat("-Z", "Y").to_euler()
    o.data.type = "ORTHO"
    o.data.ortho_scale = ortho
    return o


def area(name, loc, energy, size):
    bpy.ops.object.light_add(type="AREA", location=loc)
    o = bpy.context.object
    o.name = name
    o.data.energy = energy
    o.data.shape = "DISK"
    o.data.size = size
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat("-Z", "Y").to_euler()


front = camera("Review camera front", (3.4, -5.5, 3.0), (0, 0, 1.05), 2.8)
high = camera("Review camera gameplay angle", (3.8, -4.5, 7), (0, 0, 1.02), 3.2)
back = camera("Review camera back", (3.4, 5.5, 3.0), (0, 0, 1.05), 2.8)
area("Key softbox", (-3, -4, 6), 380, 5)
area("Violet rim", (3, 2, 4), 300, 4)

scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.samples = 48
scene.render.resolution_x = 1024
scene.render.resolution_y = 1024
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
scene.view_settings.view_transform = "AgX"

scene.camera = front
scene.render.filepath = str(SOURCE / "AshenWatcher_front.png")
bpy.ops.render.render(write_still=True)
scene.camera = high
scene.render.filepath = str(SOURCE / "AshenWatcher_gameplay.png")
bpy.ops.render.render(write_still=True)
scene.camera = back
scene.render.filepath = str(SOURCE / "AshenWatcher_back.png")
bpy.ops.render.render(write_still=True)

scene.camera = front
blend_file = SOURCE / "AshenWatcher.blend"
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(blend_file))

# The artist source stays separated; the FBX combines static geometry by material
# to avoid one renderer and draw call for every rivet or stitch in the game.
export_parts = []
for material in (cloth, cloak, leather, plate, edge, silver, dark, red, glow):
    originals = [obj for obj in bpy.data.objects if obj.parent == root and obj.type == "MESH"
                 and len(obj.material_slots) and obj.material_slots[0].material == material]
    if not originals:
        continue
    # Bake each piece into world coordinates first. Joining parented objects with
    # different local transforms otherwise shifts the FBX geometry.
    group = []
    for original in originals:
        mesh = original.data.copy()
        mesh.transform(original.matrix_world)
        copy = bpy.data.objects.new(original.name + "_export", mesh)
        bpy.context.collection.objects.link(copy)
        group.append(copy)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in group:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = group[0]
    bpy.ops.object.join()
    group[0].name = "GameMesh_" + material.name.split(" ", 1)[1].replace(" ", "_")
    group[0].parent = root
    export_parts.append(group[0])

for original in list(body_parts):
    bpy.data.objects.remove(original, do_unlink=True)

bpy.ops.object.select_all(action="DESELECT")
root.select_set(True)
for obj in export_parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = root
bpy.ops.export_scene.fbx(
    filepath=str(EXPORT / "AshenWatcher.fbx"),
    use_selection=True,
    object_types={"EMPTY", "MESH"},
    apply_scale_options="FBX_SCALE_ALL",
    axis_forward="-Z",
    axis_up="Y",
    add_leaf_bones=False,
    bake_anim=False,
    path_mode="AUTO",
)
print(f"MODEL COMPLETE: {blend_file}")
print(f"FBX COMPLETE: {EXPORT / 'AshenWatcher.fbx'}")
