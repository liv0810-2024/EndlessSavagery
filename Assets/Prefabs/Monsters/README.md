# Monster prefabs

These three prefabs are art-ready wrappers around the generated animated FBX
models. Each root is on the existing `Monster` layer and includes:

- `MonsterBase` with the GDD movement speed and stop distance.
- `CapsuleCollider` sized to the visual.
- `NavMeshAgent` configured with the same speed and stopping distance.
- The animated FBX as a nested model child.

Gameplay targeting, damage, pooling and spawn wiring remain outside these art
prefabs so they can be connected to the project's existing systems.
