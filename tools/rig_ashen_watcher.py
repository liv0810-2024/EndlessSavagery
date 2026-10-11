"""Rig the approved Ashen Watcher model and export in-place Idle/Move clips.

Run after build_ashen_watcher.py with Blender 5.2. This edits AshenWatcher.blend
and replaces the game FBX. No gameplay script or scene is changed.
"""

import math
from pathlib import Path

import bpy
from mathutils import Matrix, Quaternion, Vector


BASE = Path(__file__).resolve().parents[1]
BLEND = BASE / "ArtSource" / "AshenWatcher" / "AshenWatcher.blend"
FBX = BASE / "Assets" / "Characters" / "AshenWatcher" / "AshenWatcher_Animated.fbx"
bpy.ops.wm.open_mainfile(filepath=str(BLEND))

root = bpy.data.objects.get("AshenWatcher_Model")
if root is None:
    raise RuntimeError("AshenWatcher_Model is missing from the Blender source")
pieces = [o for o in root.children if o.type == "MESH"]
if len(pieces) < 50:
    raise RuntimeError("Expected the editable, separate-piece character source")
if bpy.data.objects.get("AshenWatcher_Rig"):
    raise RuntimeError("Source is already rigged; rebuild the static source first")

# Bright steel on the fronts of the greaves read as white flashes during a
# stride. Use the same dark plate as the other leg armor for moving gameplay.
dark_plate = bpy.data.materials["04 Blackened steel"]
for piece in pieces:
    if "greave spine" in piece.name or "steel toe" in piece.name:
        piece.data.materials.clear()
        piece.data.materials.append(dark_plate)


armature_data = bpy.data.armatures.new("AshenWatcher_Armature")
armature = bpy.data.objects.new("AshenWatcher_Rig", armature_data)
bpy.context.collection.objects.link(armature)
bpy.ops.object.select_all(action="DESELECT")
armature.select_set(True)
bpy.context.view_layer.objects.active = armature
bpy.ops.object.mode_set(mode="EDIT")


def add_bone(name, head, tail, parent=None):
    bone = armature_data.edit_bones.new(name)
    bone.head = head
    bone.tail = tail
    if parent:
        bone.parent = armature_data.edit_bones[parent]
    return bone


add_bone("Root", (0, 0, 0), (0, 0, 1.04))
add_bone("Hips", (0, 0, 1.04), (0, 0, 1.20), "Root")
add_bone("Spine", (0, 0, 1.20), (0, 0, 1.48), "Hips")
add_bone("Chest", (0, 0, 1.48), (0, 0, 1.67), "Spine")
add_bone("Head", (0, 0, 1.67), (0, 0.005, 2.06), "Chest")

for side, sign in (("L", -1), ("R", 1)):
    add_bone("UpperArm." + side, (sign * 0.31, 0, 1.57),
             (sign * 0.44, -0.005, 1.32), "Chest")
    add_bone("Forearm." + side, (sign * 0.44, -0.005, 1.32),
             (sign * 0.55, -0.025, 1.085), "UpperArm." + side)
    add_bone("Hand." + side, (sign * 0.55, -0.025, 1.085),
             (sign * 0.60, -0.04, 0.93), "Forearm." + side)
    add_bone("Thigh." + side, (sign * 0.155, 0, 1.04),
             (sign * 0.155, 0, 0.67), "Hips")
    add_bone("Shin." + side, (sign * 0.155, 0, 0.67),
             (sign * 0.155, 0, 0.24), "Thigh." + side)
    add_bone("Foot." + side, (sign * 0.155, 0, 0.24),
             (sign * 0.155, -0.10, 0.10), "Shin." + side)
    add_bone("CapeSide." + side, (sign * 0.31, 0.08, 1.61),
             (sign * 0.39, 0.25, 0.60), "Chest")
    add_bone("Cape." + side, (sign * 0.22, 0.13, 1.66),
             (sign * 0.24, 0.31, 0.61), "Chest")
add_bone("Cape.Center", (0, 0.13, 1.67), (0, 0.31, 0.55), "Chest")
bpy.ops.object.mode_set(mode="OBJECT")
armature_data.display_type = "STICK"
armature.show_in_front = True


def side_for(name):
    if name.startswith("-1 "):
        return "L"
    if name.startswith("1 "):
        return "R"
    return None


def cape_side(name):
    if name.endswith(" -1") or " -1 " in name:
        return "L"
    if name.endswith(" 1") or " 1 " in name:
        return "R"
    return "Center"


def main_bone(name):
    n = name.lower()
    side = side_for(name)
    if "folded ragged cloak panel" in n or "cloak vertical stitch" in n or "cloak fold highlight" in n or "crimson hem tear" in n:
        return "Cape." + cape_side(name)
    if "back cloak sigil" in n:
        return "Cape.Center"
    if side and ("long side cloak" in n or "side crimson lining" in n or "side cloak seam" in n):
        return "CapeSide." + side
    if "hood" in n or "mask" in n or "eye slit" in n or "shadowed head" in n:
        return "Head"
    if "sword" in n or "belt" in n or "buckle" in n:
        return "Hips"
    if side:
        if "cowl shoulder mantle" in n:
            return "Chest"
        if "glove" in n:
            return "Hand." + side
        if any(word in n for word in ("forearm", "vambrace", "cuff", "gauntlet")):
            return "Forearm." + side
        if any(word in n for word in ("upper sleeve", "elbow", "shoulder")):
            return "UpperArm." + side
        if "boot" in n or "steel toe" in n:
            return "Foot." + side
        if any(word in n for word in ("greave", "knee", "strap rivet")):
            return "Shin." + side
        if any(word in n for word in ("trouser", "thigh")):
            return "Thigh." + side
        if "skirt" in n:
            return "Hips"
    if "skirt" in n:
        return "Hips"
    if "tunic" in n:
        return "Spine"
    return "Chest"


def weights_for(name, z):
    main = main_bone(name)
    n = name.lower()
    if main.startswith("Cape"):
        # Keep the garment sewn to the upper body while its hem follows a cape bone.
        t = max(0.0, min(1.0, (1.62 - z) / 0.65))
        return {"Chest": 1 - t, main: t} if t > 0 else {"Chest": 1.0}
    if "skirt" in n and side_for(name):
        t = max(0.0, min(0.55, (1.03 - z) * 0.8))
        return {"Hips": 1 - t, "Thigh." + side_for(name): t}
    if "trouser" in n and side_for(name):
        t = max(0.0, min(0.26, (0.88 - z) * 1.0))
        return {main: 1 - t, "Shin." + side_for(name): t}
    return {main: 1.0}


for obj in pieces:
    assigned = {}
    for vertex in obj.data.vertices:
        for bone_name, weight in weights_for(obj.name, (obj.matrix_world @ vertex.co).z).items():
            if weight > 0.001:
                assigned.setdefault(bone_name, []).append((vertex.index, weight))
    for bone_name, entries in assigned.items():
        group = obj.vertex_groups.new(name=bone_name)
        for index, weight in entries:
            group.add([index], weight, "REPLACE")
    mod = obj.modifiers.new("AshenWatcher Armature", "ARMATURE")
    mod.object = armature
    mod.use_deform_preserve_volume = True


for pb in armature.pose.bones:
    pb.rotation_mode = "QUATERNION"


def rotate_world_axis(name, axis, angle):
    pb = armature.pose.bones[name]
    local_axis = pb.bone.matrix_local.to_quaternion().inverted() @ Vector(axis)
    pb.rotation_quaternion = Quaternion(local_axis, angle)


def reset_pose():
    for pb in armature.pose.bones:
        pb.rotation_quaternion = Quaternion((1, 0, 0, 0))
        pb.location = Vector((0, 0, 0))


def key_pose(frame):
    for pb in armature.pose.bones:
        pb.keyframe_insert(data_path="rotation_quaternion", frame=frame, group=pb.name)
        if pb.name == "Root":
            pb.keyframe_insert(data_path="location", frame=frame, group=pb.name)


def root_bob(amount):
    pb = armature.pose.bones["Root"]
    local_up = pb.bone.matrix_local.to_quaternion().inverted() @ Vector((0, 0, 1))
    pb.location = local_up * amount


def make_action(name, last_frame, pose_at):
    action = bpy.data.actions.new(name)
    action.use_fake_user = True
    armature.animation_data_create()
    armature.animation_data.action = action
    for frame in range(1, last_frame + 1, 3):
        reset_pose()
        pose_at((frame - 1) / (last_frame - 1) * 2 * math.pi)
        key_pose(frame)
    if (last_frame - 1) % 3 != 0:
        reset_pose()
        pose_at(2 * math.pi)
        key_pose(last_frame)
    scene.frame_set(1)
    return action


scene = bpy.context.scene
scene.render.fps = 30


def idle_pose(phase):
    root_bob(0.008 * math.sin(phase))
    rotate_world_axis("Chest", (1, 0, 0), 0.012 * math.sin(phase))
    rotate_world_axis("Head", (0, 1, 0), 0.009 * math.sin(phase))
    for side, sign in (("L", -1), ("R", 1)):
        rotate_world_axis("UpperArm." + side, (1, 0, 0), sign * 0.012 * math.sin(phase))
        rotate_world_axis("Cape." + side, (1, 0, 0), 0.018 * math.sin(phase + sign * 0.7))
    rotate_world_axis("Cape.Center", (1, 0, 0), 0.015 * math.sin(phase + 0.4))


def move_pose(phase):
    stride = math.sin(phase)
    root_bob(0.012 * (1 - math.cos(2 * phase)))
    rotate_world_axis("Hips", (0, 0, 1), 0.035 * stride)
    rotate_world_axis("Chest", (1, 0, 0), 0.048 + 0.014 * math.sin(2 * phase))
    rotate_world_axis("Head", (1, 0, 0), -0.035)
    for side, sign in (("L", -1), ("R", 1)):
        p = sign * stride
        rotate_world_axis("Thigh." + side, (1, 0, 0), 0.29 * p)
        rotate_world_axis("Shin." + side, (1, 0, 0), -0.08 - 0.20 * max(0, -p))
        rotate_world_axis("Foot." + side, (1, 0, 0), -0.10 * p + 0.09 * max(0, -p))
        rotate_world_axis("UpperArm." + side, (1, 0, 0), -0.24 * p)
        rotate_world_axis("Forearm." + side, (1, 0, 0), 0.09 + 0.04 * max(0, p))
        rotate_world_axis("CapeSide." + side, (1, 0, 0), 0.07 + 0.035 * math.sin(phase + sign))
        rotate_world_axis("Cape." + side, (1, 0, 0), 0.10 + 0.055 * math.sin(phase - 0.7 + sign * 0.5))
    rotate_world_axis("Cape.Center", (1, 0, 0), 0.12 + 0.045 * math.sin(phase - 0.5))


idle = make_action("AshenWatcher_Idle", 49, idle_pose)   # 1.6 seconds at 30 fps
move = make_action("AshenWatcher_Move", 19, move_pose)  # 0.6 seconds at 30 fps
armature.animation_data.action = idle
scene.frame_set(1)

# Render four motion checkpoints for a contact sheet. No world-space movement
# is keyed: the game can drive the Player transform itself.
scene.camera = bpy.data.objects["Review camera front"]
scene.cycles.samples = 18
scene.render.resolution_percentage = 65
armature.animation_data.action = move
for frame in (1, 5, 10, 14):
    scene.frame_set(frame)
    scene.render.filepath = str(BLEND.parent / f"AshenWatcher_Move_{frame:02d}.png")
    bpy.ops.render.render(write_still=True)

armature.animation_data.action = idle
scene.frame_set(1)
scene.render.resolution_percentage = 100
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))

# Export a material-merged copy. The editable blend keeps all original parts.
game_meshes = []
materials = [bpy.data.materials[name] for name in (
    "01 Charcoal cloth", "02 Weathered cloak", "03 Oiled leather",
    "04 Blackened steel", "05 Antique bronze", "06 Pale steel",
    "07 Mask shadow", "08 Worn crimson lining", "09 Arcane violet")]
for material in materials:
    originals = [o for o in pieces if o.material_slots and o.material_slots[0].material == material]
    if not originals:
        continue
    copies = []
    for original in originals:
        copy = original.copy()  # includes vertex group names and armature modifier
        copy.data = original.data.copy()  # includes per-vertex deform weights
        copy.data.transform(original.matrix_world)
        copy.parent = None
        copy.matrix_world = Matrix.Identity(4)
        bpy.context.collection.objects.link(copy)
        copies.append(copy)
    bpy.ops.object.select_all(action="DESELECT")
    for copy in copies:
        copy.select_set(True)
    bpy.context.view_layer.objects.active = copies[0]
    bpy.ops.object.join()
    copies[0].name = "GameMesh_" + material.name.split(" ", 1)[1].replace(" ", "_")
    game_meshes.append(copies[0])

bpy.ops.object.select_all(action="DESELECT")
armature.select_set(True)
for mesh in game_meshes:
    mesh.select_set(True)
bpy.context.view_layer.objects.active = armature
armature.animation_data.action = idle
scene.frame_set(1)
bpy.ops.export_scene.fbx(
    filepath=str(FBX),
    use_selection=True,
    object_types={"ARMATURE", "MESH"},
    apply_scale_options="FBX_SCALE_ALL",
    axis_forward="-Z", axis_up="Y",
    add_leaf_bones=False,
    bake_anim=True,
    bake_anim_use_nla_strips=False,
    bake_anim_use_all_actions=True,
    bake_anim_force_startend_keying=True,
    bake_anim_step=1,
    bake_anim_simplify_factor=0,
    path_mode="AUTO",
)
print("RIGGED_SOURCE", BLEND)
print("ANIMATED_FBX", FBX)
print("CLIPS", idle.name, move.name)
