# Monster prefabs

These three prefabs are saved and reload-validated by the Tuanjie editor.
Each root is on the existing `Monster` layer and includes:

- An Animator with root motion disabled and its Controller left unassigned.
- `CapsuleCollider` sized to the visual.
- The full animated model hierarchy and separately editable materials.

Assign your Animator Controller on the prefab root, then use the matching
`Assets/Characters/Monsters/<Name>/<Name>_Walk.anim` clip. Gameplay behaviours
and NavMeshAgent setup are owned by the programmer. See
`ArtSource/Delivery/美术资源交付说明.md` for the complete asset index.
