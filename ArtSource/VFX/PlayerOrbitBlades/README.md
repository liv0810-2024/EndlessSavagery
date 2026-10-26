# Player Orbit Blades

The approved A-direction automatic attack VFX: four violet arc blades with
antique-bronze mounts orbiting the player on a horizontal ring. The FBX contains
the looping 24-frame transform animation and four tapered mesh trails.

- `PlayerOrbitBlades.blend`: editable source.
- `PlayerOrbitBlades.fbx`: animated VFX mesh for Unity import.
- `Assets/VFX/PlayerOrbitBlades/PlayerOrbitBlades.prefab`: complete art prefab with materials and Animator; assign your own Controller on this root.
- `Assets/VFX/PlayerOrbitBlades/PlayerOrbitBlades_Orbit.anim`: independent loop clip.
- `PlayerOrbitBlades.gif`: motion preview.
- `PlayerOrbitBlades_Design.png`: approved concept board showing the A direction.
- Clip timing: 25 frames at 30 fps, one full orbit.

The prefab uses the included OrbitGlow shader, additive blending, and vertex
alpha for fading trails. Its Animator Controller is intentionally unassigned.
Gameplay spawning, damage timing, enabling and disabling belong to the owner.
