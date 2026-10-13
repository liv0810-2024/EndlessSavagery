"""Write lightweight Unity/Tuanjie monster prefabs around the generated FBX models."""

from pathlib import Path
import uuid

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Assets" / "Prefabs" / "Monsters"
OUT.mkdir(parents=True, exist_ok=True)

MONSTERS = {
    "WildernessSlime": {
        "guid": "Bnsbti6qBikdzK80ooegmPVRZqFiPyKVU8fANFOL/0UXcCImrSJxeko=",
        "speed": 2.2, "stop": 1.2, "radius": 0.55, "height": 0.85,
    },
    "ShadowWolf": {
        "guid": "CnxM53ivBy/x3L9QjwgCDx9OAuJnEI2RboT5d5R2QjeZduXQcQ0KTBY=",
        "speed": 3.5, "stop": 1.25, "radius": 0.48, "height": 1.25,
    },
    "StoneGuardian": {
        "guid": "XX0etnyoVnzDjv5CGL0YG3sIVazs5rgQiy/CqCT9Oxd8jETyPkeo308=",
        "speed": 1.8, "stop": 1.4, "radius": 0.72, "height": 2.35,
    },
}

SCRIPT_GUID = "WysatC6tUXqW9AfanEZfimQqoLvwJiOHq+EKF0ErN3eLi4b8O0SOhjU="


def prefab(name, cfg):
    root_go = 1000000000000001
    root_tr = 4000000000000001
    nested = 100100000
    child_go = 1000000000000000
    child_tr = 4000000000000000
    monster = 1140000000000001
    collider = 1360000000000001
    agent = 1950000000000001
    return f'''%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!1 &{root_go}
GameObject:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  serializedVersion: 6
  m_Component:
  - component: {{fileID: {root_tr}}}
  - component: {{fileID: {monster}}}
  - component: {{fileID: {collider}}}
  - component: {{fileID: {agent}}}
  m_Layer: 8
  m_Name: {name}
  m_TagString: Untagged
  m_Icon: {{fileID: 0}}
  m_NavMeshLayer: 0
  m_StaticEditorFlags: 0
  m_IsActive: 1
--- !u!4 &{root_tr}
Transform:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_GameObject: {{fileID: {root_go}}}
  serializedVersion: 2
  m_LocalRotation: {{x: 0, y: 0, z: 0, w: 1}}
  m_LocalPosition: {{x: 0, y: 0, z: 0}}
  m_LocalScale: {{x: 1, y: 1, z: 1}}
  m_ConstrainProportionsScale: 0
  m_Children:
  - {{fileID: {child_tr}}}
  m_Father: {{fileID: 0}}
  m_LocalEulerAnglesHint: {{x: 0, y: 0, z: 0}}
--- !u!114 &{monster}
MonoBehaviour:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_GameObject: {{fileID: {root_go}}}
  m_Enabled: 1
  m_EditorHideFlags: 0
  serializedVersion: 8
  m_EditorClassIdentifier: 
  m_Script: {{fileID: 11500000, guid: {SCRIPT_GUID}, type: 3}}
  moveSpeed: {cfg['speed']}
  stopDistance: {cfg['stop']}
  target: {{fileID: 0}}
  visualAnimator: {{fileID: 0}}
--- !u!136 &{collider}
CapsuleCollider:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_GameObject: {{fileID: {root_go}}}
  m_Material: {{fileID: 0}}
  m_IsTrigger: 0
  m_Enabled: 1
  m_Radius: {cfg['radius']}
  m_Height: {cfg['height']}
  m_Direction: 1
  m_Center: {{x: 0, y: {cfg['height']/2:.3f}, z: 0}}
--- !u!195 &{agent}
NavMeshAgent:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_GameObject: {{fileID: {root_go}}}
  m_Enabled: 1
  m_AgentTypeID: 0
  m_Radius: {cfg['radius']}
  m_Speed: {cfg['speed']}
  m_Acceleration: 20
  m_AngularSpeed: 720
  m_StoppingDistance: {cfg['stop']}
  m_AutoBraking: 1
  m_AutoRepath: 1
  m_Height: {cfg['height']}
  m_BaseOffset: 0
  m_ObstacleAvoidanceType: 4
  m_Quality: 0
  m_PathFindingIterationsPerFrame: 100
--- !u!1001 &{nested}
PrefabInstance:
  m_ObjectHideFlags: 0
  serializedVersion: 2
  m_Modification:
    serializedVersion: 3
    m_TransformParent: {{fileID: {root_tr}}}
    m_Modifications: []
    m_RemovedComponents: []
    m_AddedComponents: []
  m_SourcePrefab: {{fileID: 100100000, guid: {cfg['guid']}, type: 3}}
--- !u!1 &{child_go} stripped
GameObject:
  m_CorrespondingSourceObject: {{fileID: 1000000000000000, guid: {cfg['guid']}, type: 3}}
  m_PrefabInstance: {{fileID: {nested}}}
  m_PrefabAsset: {{fileID: 0}}
--- !u!4 &{child_tr} stripped
Transform:
  m_CorrespondingSourceObject: {{fileID: 4000000000000000, guid: {cfg['guid']}, type: 3}}
  m_PrefabInstance: {{fileID: {nested}}}
  m_PrefabAsset: {{fileID: 0}}
  m_GameObject: {{fileID: {child_go}}}
  m_LocalRotation: {{x: 0, y: 0, z: 0, w: 1}}
  m_LocalPosition: {{x: 0, y: 0, z: 0}}
  m_LocalScale: {{x: 1, y: 1, z: 1}}
  m_Father: {{fileID: {root_tr}}}
'''


for name, cfg in MONSTERS.items():
    p = OUT / f"{name}.prefab"
    p.write_text(prefab(name, cfg), encoding="utf-8")
    meta = p.with_suffix(p.suffix + ".meta")
    if not meta.exists():
        meta.write_text(f"fileFormatVersion: 2\nguid: {uuid.uuid4().hex}\nPrefabImporter:\n  externalObjects: {{}}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n", encoding="utf-8")

folder_meta = OUT.with_suffix(".meta")
if not folder_meta.exists():
    folder_meta.write_text(f"fileFormatVersion: 2\nguid: {uuid.uuid4().hex}\nfolderAsset: 1\ntimeCreated: 0\nDefaultImporter:\n  externalObjects: {{}}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n", encoding="utf-8")

print("MONSTER PREFABS COMPLETE", OUT)
