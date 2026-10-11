from pathlib import Path
import bpy
from mathutils import Vector

root = Path(__file__).resolve().parents[1]

def report(label, objects):
    points = [obj.matrix_world @ Vector(corner) for obj in objects for corner in obj.bound_box]
    low = [min(p[i] for p in points) for i in range(3)]
    high = [max(p[i] for p in points) for i in range(3)]
    print(label, "meshes", len(objects), "min", low, "max", high)

bpy.ops.wm.open_mainfile(filepath=str(root / "ArtSource/AshenWatcher/AshenWatcher.blend"))
source = [o for o in bpy.data.objects if o.type == "MESH" and o.parent and o.parent.name == "AshenWatcher_Model"]
report("SOURCE", source)
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(root / "Assets/Characters/AshenWatcher/AshenWatcher_Animated.fbx"))
report("FBX", [o for o in bpy.data.objects if o.type == "MESH"])
for action in bpy.data.actions:
    print("FBX_ACTION", action.name, tuple(action.frame_range))
