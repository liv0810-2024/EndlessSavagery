# Ashen Watcher player model

This is a stylized gameplay interpretation of `AshenWatcher_concept.png`. The refined version replaces the initial blockout's spherical hood, round pauldrons, short cape and square boots with an open peaked hood, layered angular armor, longer folded cloak and shaped leg armor.

- `AshenWatcher.blend`: editable Blender 5.2 source, with separate armor, cloth, mask, sword and cloak pieces, a 22-bone rig, and two Actions.
- `AshenWatcher_front.png`: rendered review image.
- `AshenWatcher_gameplay.png`: approximate overhead gameplay-angle review image.
- `AshenWatcher_back.png`: rear review image showing the cloak and sigil.
- `AshenWatcher_Move.gif`: looping visual preview of the moving character.
- `../../Assets/Characters/AshenWatcher/AshenWatcher.fbx`: static model used by the existing scene.
- `../../Assets/Characters/AshenWatcher/AshenWatcher_Animated.fbx`: rigged character with `AshenWatcher_Idle` and `AshenWatcher_Move` actions.
- `../../Assets/Characters/AshenWatcher/Textures/`: tileable color textures for cloth, leather, steel, bronze and lining.
- `../../tools/build_ashen_watcher.py`: reproducible Blender build script.
- `../../tools/rig_ashen_watcher.py`: builds the bone weights and in-place animation clips from the static source.

The character is about 2.09 units tall. The existing scene still uses the static FBX and is not connected to the animations. The animated FBX is a separate asset so movement code and the scene remain available for the project owner to wire up. The animated FBX imports Y-up, while the older static scene asset imports Z-up.

The Blender source keeps pieces separate for editing; the FBX combines them into nine material groups to reduce draw calls. `AshenWatcher_Idle` is a subtle 1.6-second breathing loop. `AshenWatcher_Move` is a 0.6-second in-place locomotion loop at 30 fps, with alternating arms and legs and cape follow-through. Both have matching first and last poses and no horizontal root motion. The FBX carries the actions; when importing into Tuanjie, enable **Loop Time** for both clips in the model's Animation import settings if it is not already on. There is no Animator Controller or gameplay code hookup. Its purple accents are emissive in Blender; Tuanjie may need a material/shader setup for identical bloom.
