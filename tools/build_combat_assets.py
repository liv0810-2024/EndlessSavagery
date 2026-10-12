"""Build the remaining combat assets for EndlessSavagery.

This script is intentionally self contained so the art pass can be rebuilt with
the Blender version already used by the Ashen Watcher player asset.

Run from the project root:
    blender -b --python tools/build_combat_assets.py
"""

from pathlib import Path
import math
import shutil

import bpy
from mathutils import Euler, Quaternion, Vector


ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "ArtSource"
GAME = ROOT / "Assets"
BLENDER = Path(r"D:\ApplicationFile\Blander\blender.exe")
FPS = 30


def mat(name, color, metallic=0.0, rough=0.65, emission=None):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = rough
    if emission:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1)
        bsdf.inputs["Emission Strength"].default_value = 4.0
    return m


CHARCOAL = mat("Monster Charcoal", (0.035, 0.042, 0.055), 0.45, 0.48)
PLATE = mat("Monster Blackened Steel", (0.09, 0.10, 0.12), 0.72, 0.38)
BRONZE = mat("Monster Antique Bronze", (0.36, 0.19, 0.08), 0.7, 0.36)
VIOLET = mat("Monster Arcane Violet", (0.22, 0.055, 0.58), 0.15, 0.25, (0.38, 0.08, 0.95))
SLIME = mat("Wilderness Slime", (0.12, 0.42, 0.27), 0.05, 0.3)
SLIME_LIGHT = mat("Wilderness Slime Light", (0.28, 0.86, 0.48), 0.0, 0.28, (0.10, 0.5, 0.15))
WOLF = mat("Shadow Wolf Fur", (0.055, 0.047, 0.09), 0.15, 0.5)
WOLF_LIGHT = mat("Shadow Wolf Mark", (0.22, 0.05, 0.30), 0.25, 0.35, (0.38, 0.03, 0.5))
EYE = mat("Monster Eye", (0.8, 0.05, 0.04), 0.0, 0.2, (1.0, 0.02, 0.01))
STONE = mat("Stone Guardian", (0.22, 0.24, 0.27), 0.5, 0.82)
STONE_DARK = mat("Stone Guardian Dark", (0.09, 0.10, 0.12), 0.65, 0.65)


def refresh_materials():
    """Reload material handles after opening another .blend file."""
    global CHARCOAL, PLATE, BRONZE, VIOLET, SLIME, SLIME_LIGHT
    global WOLF, WOLF_LIGHT, EYE, STONE, STONE_DARK
    CHARCOAL = mat("Monster Charcoal", (0.035, 0.042, 0.055), 0.45, 0.48)
    PLATE = mat("Monster Blackened Steel", (0.09, 0.10, 0.12), 0.72, 0.38)
    BRONZE = mat("Monster Antique Bronze", (0.36, 0.19, 0.08), 0.7, 0.36)
    VIOLET = mat("Monster Arcane Violet", (0.22, 0.055, 0.58), 0.15, 0.25, (0.38, 0.08, 0.95))
    SLIME = mat("Wilderness Slime", (0.12, 0.42, 0.27), 0.05, 0.3)
    SLIME_LIGHT = mat("Wilderness Slime Light", (0.28, 0.86, 0.48), 0.0, 0.28, (0.10, 0.5, 0.15))
    WOLF = mat("Shadow Wolf Fur", (0.055, 0.047, 0.09), 0.15, 0.5)
    WOLF_LIGHT = mat("Shadow Wolf Mark", (0.22, 0.05, 0.30), 0.25, 0.35, (0.38, 0.03, 0.5))
    EYE = mat("Monster Eye", (0.8, 0.05, 0.04), 0.0, 0.2, (1.0, 0.02, 0.01))
    STONE = mat("Stone Guardian", (0.22, 0.24, 0.27), 0.5, 0.82)
    STONE_DARK = mat("Stone Guardian Dark", (0.09, 0.10, 0.12), 0.65, 0.65)


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.armatures, bpy.data.cameras, bpy.data.lights):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)


def smooth(obj):
    if obj.type == "MESH":
        for p in obj.data.polygons:
            p.use_smooth = True
    return obj


def primitive(kind, name, loc, scale, material, rotation=None):
    if kind == "ico":
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1, location=loc)
    elif kind == "uv":
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, location=loc)
    elif kind == "cube":
        bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    elif kind == "cone":
        bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=1, radius2=0.72, depth=1, location=loc)
    elif kind == "cylinder":
        bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=1, depth=1, location=loc)
    else:
        raise ValueError(kind)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    if rotation:
        o.rotation_euler = rotation
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    return smooth(o)


def mesh_poly(name, vertices, faces, material, loc=(0, 0, 0)):
    me = bpy.data.meshes.new(name + "Mesh")
    me.from_pydata(vertices, [], faces)
    me.update()
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    o.location = loc
    o.data.materials.append(material)
    return o


def add_bone(arm, name, head, tail, parent=None):
    b = arm.data.edit_bones.new(name)
    b.head = head
    b.tail = tail
    if parent:
        b.parent = arm.data.edit_bones[parent]
    return b


def make_armature(name, bones):
    data = bpy.data.armatures.new(name + "_Armature")
    arm = bpy.data.objects.new(name + "_Rig", data)
    bpy.context.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    arm.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    for args in bones:
        add_bone(arm, *args)
    bpy.ops.object.mode_set(mode="OBJECT")
    arm.show_in_front = True
    return arm


def bind(obj, arm, bone):
    world = obj.matrix_world.copy()
    obj.parent = arm
    obj.parent_type = "BONE"
    obj.parent_bone = bone
    obj.matrix_world = world
    return obj


def key_pose(arm, frame, include_scale=True):
    for pb in arm.pose.bones:
        pb.keyframe_insert(data_path="rotation_euler", frame=frame, group=pb.name)
        pb.keyframe_insert(data_path="location", frame=frame, group=pb.name)
        if include_scale:
            pb.keyframe_insert(data_path="scale", frame=frame, group=pb.name)


def reset_pose(arm):
    for pb in arm.pose.bones:
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = Euler((0, 0, 0), "XYZ")
        pb.location = Vector((0, 0, 0))
        pb.scale = Vector((1, 1, 1))


def action_for(arm, name, last, pose_fn):
    action = bpy.data.actions.new(name)
    action.use_fake_user = True
    arm.animation_data_create()
    arm.animation_data.action = action
    for frame in range(1, last + 1, 3):
        reset_pose(arm)
        pose_fn((frame - 1) / (last - 1) * 2 * math.pi)
        key_pose(arm, frame)
    reset_pose(arm)
    pose_fn(2 * math.pi)
    key_pose(arm, last)
    return action


def setup_camera(title="Review"):
    bpy.ops.object.camera_add(location=(4.0, -5.5, 3.5))
    cam = bpy.context.object
    cam.name = title + " camera"
    direction = Vector((0, 0, 0.75)) - cam.location
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = 52
    bpy.context.scene.camera = cam
    bpy.ops.object.light_add(type="AREA", location=(2.5, -3.0, 5.0))
    key = bpy.context.object
    key.data.energy = 720
    key.data.shape = "DISK"
    key.data.size = 4.5
    key.rotation_euler = (0.4, 0, 0.35)
    bpy.ops.object.light_add(type="AREA", location=(-3.5, 1.0, 2.8))
    fill = bpy.context.object
    fill.data.energy = 420
    fill.data.color = (0.35, 0.25, 0.8)
    fill.data.size = 3.0
    fill.rotation_euler = (0.8, 0, -1.0)
    world = bpy.context.scene.world
    world.color = (0.018, 0.021, 0.032)
    return cam


def render_asset(folder, stem, frames=(1, 5, 10, 14), arm=None):
    folder.mkdir(parents=True, exist_ok=True)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 512
    scene.render.resolution_y = 512
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.fps = FPS
    if arm:
        arm.animation_data.action = bpy.data.actions.get(stem + "_Walk") or arm.animation_data.action
    for frame in frames:
        scene.frame_set(frame)
        scene.render.filepath = str(folder / f"{stem}_{frame:02d}.png")
        bpy.ops.render.render(write_still=True)
    scene.frame_set(1)


def export_selected(filepath, arm, meshes):
    bpy.ops.object.select_all(action="DESELECT")
    arm.select_set(True)
    for o in meshes:
        o.select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.export_scene.fbx(
        filepath=str(filepath), use_selection=True,
        object_types={"ARMATURE", "MESH", "EMPTY"},
        apply_scale_options="FBX_SCALE_ALL", axis_forward="-Z", axis_up="Y",
        add_leaf_bones=False, bake_anim=True,
        bake_anim_use_nla_strips=False, bake_anim_use_all_actions=True,
        bake_anim_force_startend_keying=True, bake_anim_step=1,
        bake_anim_simplify_factor=0, path_mode="AUTO")


def build_slime():
    name = "WildernessSlime"
    clear_scene()
    folder = ART / "Monsters" / name
    out = GAME / "Characters" / "Monsters" / name
    folder.mkdir(parents=True, exist_ok=True); out.mkdir(parents=True, exist_ok=True)
    bones = [("Root", (0, 0, 0), (0, 0, 0.45), None), ("Body", (0, 0, 0.28), (0, 0, 0.75), "Root"),
             ("Core", (0, 0, 0.45), (0, 0, 0.75), "Body"), ("Eye.L", (-0.16, -0.18, 0.47), (-0.16, -0.18, 0.62), "Body"),
             ("Eye.R", (0.16, -0.18, 0.47), (0.16, -0.18, 0.62), "Body")]
    arm = make_armature(name, bones)
    meshes = []
    meshes.append(bind(primitive("ico", "Slime_Body", (0, 0, 0.42), (0.62, 0.52, 0.42), SLIME), arm, "Body"))
    meshes.append(bind(primitive("uv", "Slime_Core", (0, -0.08, 0.47), (0.18, 0.13, 0.18), SLIME_LIGHT), arm, "Core"))
    for s, x in (("L", -0.16), ("R", 0.16)):
        meshes.append(bind(primitive("uv", f"Slime_Eye_{s}", (x, -0.47, 0.53), (0.07, 0.045, 0.09), EYE), arm, "Eye." + s))
    for i, x in enumerate((-0.38, 0.38)):
        meshes.append(bind(primitive("ico", f"Slime_SideBlob_{i}", (x, 0.01, 0.26), (0.22, 0.24, 0.18), SLIME), arm, "Root"))
    def pose(phase):
        arm.pose.bones["Root"].rotation_euler[2] = 0.04 * math.sin(phase)
        body = arm.pose.bones["Body"]
        body.scale = (1.0 + 0.06 * math.sin(phase), 1.0 + 0.06 * math.sin(phase), 1.0 - 0.08 * math.sin(phase))
        arm.pose.bones["Core"].rotation_euler[1] = 0.12 * math.sin(phase)
        for n, sign in (("Eye.L", -1), ("Eye.R", 1)):
            arm.pose.bones[n].rotation_euler[2] = sign * 0.06 * math.sin(phase)
    walk = action_for(arm, name + "_Walk", 19, pose)
    arm.animation_data.action = walk
    setup_camera(name)
    render_asset(folder, name + "_Walk", arm=arm)
    bpy.ops.wm.save_as_mainfile(filepath=str(folder / (name + ".blend")))
    export_selected(out / (name + "_Animated.fbx"), arm, meshes)
    return folder, out


def build_wolf():
    name = "ShadowWolf"
    clear_scene()
    folder = ART / "Monsters" / name
    out = GAME / "Characters" / "Monsters" / name
    folder.mkdir(parents=True, exist_ok=True); out.mkdir(parents=True, exist_ok=True)
    bones = [("Root", (0, 0, 0), (0, 0, 0.45), None), ("Spine", (0, 0, 0.55), (0, 0, 0.95), "Root"),
             ("Head", (0, -0.55, 0.88), (0, -0.75, 1.18), "Spine"), ("Tail", (0, 0.65, 0.75), (0, 0.0, 1.25), "Spine")]
    for side, x in (("L", -1), ("R", 1)):
        for leg, y in (("Front", -0.32), ("Rear", 0.34)):
            bones.append((f"{leg}Leg.{side}", (x * 0.24, y, 0.58), (x * 0.26, y - 0.02, 0.12), "Root"))
    arm = make_armature(name, bones)
    meshes = []
    meshes.append(bind(primitive("ico", "Wolf_Body", (0, 0.05, 0.78), (0.58, 0.92, 0.42), WOLF), arm, "Spine"))
    meshes.append(bind(primitive("ico", "Wolf_Chest", (0, -0.47, 0.78), (0.48, 0.50, 0.42), WOLF), arm, "Spine"))
    meshes.append(bind(primitive("ico", "Wolf_Head", (0, -0.72, 1.04), (0.38, 0.40, 0.34), WOLF), arm, "Head"))
    meshes.append(bind(primitive("cone", "Wolf_Snout", (0, -1.04, 0.96), (0.23, 0.34, 0.20), WOLF_LIGHT, rotation=(math.pi/2, 0, 0)), arm, "Head"))
    for side, x in (("L", -1), ("R", 1)):
        meshes.append(bind(primitive("cone", f"Wolf_Ear_{side}", (x * 0.23, -0.72, 1.37), (0.13, 0.13, 0.32), WOLF, rotation=(0, 0, x * 0.18)), arm, "Head"))
        meshes.append(bind(primitive("uv", f"Wolf_Eye_{side}", (x * 0.18, -1.02, 1.10), (0.055, 0.035, 0.06), EYE), arm, "Head"))
        for leg, y in (("Front", -0.35), ("Rear", 0.35)):
            meshes.append(bind(primitive("cone", f"Wolf_{leg}Leg_{side}", (x * 0.27, y, 0.34), (0.16, 0.16, 0.38), WOLF), arm, f"{leg}Leg.{side}"))
            meshes.append(bind(primitive("ico", f"Wolf_{leg}Paw_{side}", (x * 0.27, y - 0.08, 0.10), (0.20, 0.25, 0.10), WOLF_LIGHT), arm, f"{leg}Leg.{side}"))
    meshes.append(bind(primitive("cone", "Wolf_Tail", (0, 0.82, 1.05), (0.16, 0.16, 0.65), WOLF_LIGHT, rotation=(-0.6, 0, 0)), arm, "Tail"))
    def pose(phase):
        arm.pose.bones["Spine"].rotation_euler[2] = 0.035 * math.sin(phase)
        arm.pose.bones["Head"].rotation_euler[0] = 0.045 * math.sin(phase + 0.5)
        arm.pose.bones["Tail"].rotation_euler[0] = 0.18 + 0.10 * math.sin(phase + 0.7)
        for leg, phase_sign in (("Front", 1), ("Rear", -1)):
            for side, sign in (("L", -1), ("R", 1)):
                arm.pose.bones[f"{leg}Leg.{side}"].rotation_euler[0] = 0.34 * math.sin(phase + phase_sign * sign * math.pi)
    walk = action_for(arm, name + "_Walk", 19, pose)
    arm.animation_data.action = walk
    setup_camera(name)
    render_asset(folder, name + "_Walk", arm=arm)
    bpy.ops.wm.save_as_mainfile(filepath=str(folder / (name + ".blend")))
    export_selected(out / (name + "_Animated.fbx"), arm, meshes)
    return folder, out


def build_guardian():
    name = "StoneGuardian"
    clear_scene()
    folder = ART / "Monsters" / name
    out = GAME / "Characters" / "Monsters" / name
    folder.mkdir(parents=True, exist_ok=True); out.mkdir(parents=True, exist_ok=True)
    bones = [("Root", (0, 0, 0), (0, 0, 0.9), None), ("Hips", (0, 0, 0.88), (0, 0, 1.3), "Root"),
             ("Chest", (0, 0, 1.28), (0, 0, 1.95), "Hips"), ("Head", (0, -0.02, 1.95), (0, 0, 2.32), "Chest")]
    for side, x in (("L", -1), ("R", 1)):
        bones += [(f"Arm.{side}", (x * 0.55, 0, 1.72), (x * 0.82, -0.02, 1.10), "Chest"),
                  (f"Leg.{side}", (x * 0.25, 0, 0.90), (x * 0.29, 0, 0.18), "Hips")]
    arm = make_armature(name, bones)
    meshes = []
    meshes.append(bind(primitive("cube", "Guardian_Torso", (0, 0, 1.50), (0.72, 0.52, 0.80), STONE, rotation=(0.0, 0.0, 0.0)), arm, "Chest"))
    meshes.append(bind(primitive("cube", "Guardian_ChestPlate", (0, -0.46, 1.52), (0.52, 0.10, 0.56), STONE_DARK), arm, "Chest"))
    meshes.append(bind(primitive("ico", "Guardian_Head", (0, -0.02, 2.05), (0.45, 0.40, 0.36), STONE), arm, "Head"))
    meshes.append(bind(primitive("cube", "Guardian_Face", (0, -0.39, 2.04), (0.28, 0.08, 0.12), STONE_DARK), arm, "Head"))
    meshes.append(bind(primitive("cube", "Guardian_GlowCore", (0, -0.54, 1.53), (0.15, 0.04, 0.22), VIOLET), arm, "Chest"))
    for side, x in (("L", -1), ("R", 1)):
        meshes.append(bind(primitive("cube", f"Guardian_Shoulder_{side}", (x * 0.62, 0, 1.86), (0.30, 0.55, 0.35), STONE_DARK), arm, "Chest"))
        meshes.append(bind(primitive("cube", f"Guardian_Arm_{side}", (x * 0.84, 0, 1.35), (0.27, 0.33, 0.67), STONE), arm, f"Arm.{side}"))
        meshes.append(bind(primitive("ico", f"Guardian_Fist_{side}", (x * 0.86, -0.07, 0.88), (0.30, 0.32, 0.28), STONE_DARK), arm, f"Arm.{side}"))
        meshes.append(bind(primitive("cube", f"Guardian_Leg_{side}", (x * 0.28, 0, 0.48), (0.36, 0.45, 0.75), STONE_DARK), arm, f"Leg.{side}"))
        meshes.append(bind(primitive("cube", f"Guardian_Foot_{side}", (x * 0.28, -0.15, 0.12), (0.46, 0.60, 0.25), STONE), arm, f"Leg.{side}"))
    for z in (1.15, 1.42, 1.72):
        meshes.append(bind(primitive("cube", f"Guardian_Crack_{z}", (0, -0.57, z), (0.025, 0.02, 0.16), VIOLET), arm, "Chest"))
    def pose(phase):
        arm.pose.bones["Hips"].rotation_euler[2] = 0.02 * math.sin(phase)
        arm.pose.bones["Chest"].rotation_euler[0] = 0.035 * math.sin(phase + 0.4)
        arm.pose.bones["Head"].rotation_euler[2] = -0.025 * math.sin(phase)
        for side, sign in (("L", -1), ("R", 1)):
            arm.pose.bones[f"Leg.{side}"].rotation_euler[0] = 0.22 * math.sin(phase + sign * math.pi)
            arm.pose.bones[f"Arm.{side}"].rotation_euler[0] = 0.14 * math.sin(phase + sign * math.pi) + 0.08
    walk = action_for(arm, name + "_Walk", 25, pose)
    arm.animation_data.action = walk
    setup_camera(name)
    render_asset(folder, name + "_Walk", frames=(1, 7, 13, 19), arm=arm)
    bpy.ops.wm.save_as_mainfile(filepath=str(folder / (name + ".blend")))
    export_selected(out / (name + "_Animated.fbx"), arm, meshes)
    return folder, out


def add_dash_to_player():
    src = ART / "AshenWatcher" / "AshenWatcher.blend"
    folder = ART / "AshenWatcher"
    out = GAME / "Characters" / "AshenWatcher"
    bpy.ops.wm.open_mainfile(filepath=str(src))
    arm = bpy.data.objects.get("AshenWatcher_Rig")
    if not arm:
        raise RuntimeError("AshenWatcher_Rig missing")
    for pb in arm.pose.bones:
        pb.rotation_mode = "QUATERNION"
    action = bpy.data.actions.new("AshenWatcher_Dash")
    action.use_fake_user = True
    arm.animation_data_create(); arm.animation_data.action = action
    def set_pose(frame, crouch, lean, arms):
        for pb in arm.pose.bones:
            pb.rotation_quaternion = Quaternion((1, 0, 0, 0)); pb.location = Vector((0, 0, 0))
        def q(name, axis, angle):
            if arm.pose.bones.get(name):
                arm.pose.bones[name].rotation_quaternion = Quaternion(axis, angle)
        q("Hips", (1, 0, 0), crouch * 0.22)
        q("Spine", (1, 0, 0), lean)
        q("Chest", (1, 0, 0), lean * 0.45)
        q("Head", (1, 0, 0), -lean * 0.35)
        for side, sign in (("L", -1), ("R", 1)):
            q("Thigh." + side, (1, 0, 0), sign * crouch * 0.32)
            q("Shin." + side, (1, 0, 0), -crouch * 0.22)
            q("UpperArm." + side, (1, 0, 0), sign * arms)
            q("Forearm." + side, (1, 0, 0), -sign * arms * 0.6)
            q("Cape." + side, (1, 0, 0), 0.12 + crouch * 0.08)
        q("Cape.Center", (1, 0, 0), 0.14 + crouch * 0.06)
        for pb in arm.pose.bones:
            pb.keyframe_insert(data_path="rotation_quaternion", frame=frame, group=pb.name)
            if pb.name == "Root": pb.keyframe_insert(data_path="location", frame=frame, group=pb.name)
    for frame, crouch, lean, arms in ((1, 0.0, 0.0, 0.0), (4, 0.9, 0.18, 0.22), (8, 1.0, 0.42, 0.34), (12, 0.55, 0.24, 0.20), (19, 0.0, 0.0, 0.0)):
        set_pose(frame, crouch, lean, arms)
    scene = bpy.context.scene; scene.render.fps = FPS; scene.frame_set(1)
    cam = bpy.data.objects.get("Review camera front") or setup_camera("AshenWatcher Dash")
    scene.camera = cam
    for frame in (1, 4, 8, 12, 19):
        scene.frame_set(frame); scene.render.resolution_x = 512; scene.render.resolution_y = 512
        scene.render.image_settings.file_format = "PNG"
        scene.render.filepath = str(folder / f"AshenWatcher_Dash_{frame:02d}.png")
        bpy.ops.render.render(write_still=True)
    dash_blend = folder / "AshenWatcher_Dash.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(dash_blend))
    meshes = [o for o in bpy.data.objects if o.type == "MESH" and o.parent == arm]
    export_selected(out / "AshenWatcher_Dash.fbx", arm, meshes)


def build_orbit_blades():
    name = "PlayerOrbitBlades"
    clear_scene()
    folder = ART / "VFX" / name
    out = GAME / "VFX" / name
    folder.mkdir(parents=True, exist_ok=True); out.mkdir(parents=True, exist_ok=True)
    root = bpy.data.objects.new(name, None); bpy.context.collection.objects.link(root)
    blades = []
    for i in range(4):
        a = i * math.pi / 2
        r = 1.25
        x, y = math.cos(a) * r, math.sin(a) * r
        outline = [(-0.52, 0, -0.04), (-0.18, 0, -0.15), (0.45, 0, 0), (-0.18, 0, 0.15), (-0.52, 0, 0.04)]
        verts = []
        for z in (0.03, 0.12):
            verts.extend([(x + px * math.cos(a) - py * math.sin(a), y + px * math.sin(a) + py * math.cos(a), z) for px, _, py in outline])
        faces = [(0,1,2,3,4), (5,9,8,7,6), (0,5,6,1), (1,6,7,2), (2,7,8,3), (3,8,9,4), (4,9,5,0)]
        blade = mesh_poly(f"OrbitBlade_{i+1}", verts, faces, VIOLET)
        blade.parent = root; blade.rotation_euler[2] = a
        blades.append(blade)
        mount = primitive("cone", f"OrbitMount_{i+1}", (x * 0.94, y * 0.94, 0.09), (0.15, 0.15, 0.07), BRONZE)
        mount.parent = root; mount.rotation_euler[2] = a; blades.append(mount)
    bpy.ops.mesh.primitive_torus_add(major_radius=1.25, minor_radius=0.012, major_segments=64, minor_segments=6, location=(0, 0, 0.055))
    ring = bpy.context.object; ring.name = "OrbitEnergyTrace"; ring.data.materials.append(VIOLET); ring.parent = root; blades.append(ring)
    root.rotation_mode = "XYZ"
    root.keyframe_insert(data_path="rotation_euler", frame=1, index=2)
    root.rotation_euler[2] = 2 * math.pi
    root.keyframe_insert(data_path="rotation_euler", frame=25, index=2)
    scene = bpy.context.scene; scene.render.engine = "BLENDER_EEVEE"; scene.render.resolution_x = 640; scene.render.resolution_y = 640; scene.render.image_settings.file_format = "PNG"
    setup_camera(name)
    for frame in (1, 7, 13, 19, 25):
        scene.frame_set(frame); scene.render.filepath = str(folder / f"{name}_{frame:02d}.png"); bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(folder / (name + ".blend")))
    bpy.ops.object.select_all(action="DESELECT"); root.select_set(True)
    for o in blades: o.select_set(True)
    bpy.context.view_layer.objects.active = root
    bpy.ops.export_scene.fbx(filepath=str(out / (name + ".fbx")), use_selection=True, object_types={"EMPTY", "MESH"}, apply_scale_options="FBX_SCALE_ALL", axis_forward="-Z", axis_up="Y", bake_anim=True, bake_anim_use_all_actions=True, bake_anim_force_startend_keying=True, bake_anim_step=1, bake_anim_simplify_factor=0, path_mode="AUTO")


def main():
    add_dash_to_player()
    refresh_materials()
    build_slime()
    build_wolf()
    build_guardian()
    build_orbit_blades()
    print("COMBAT ASSETS COMPLETE")


if __name__ == "__main__":
    main()
