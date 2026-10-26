"""Ask the open Unity/Tuanjie editor to rebuild the art delivery.

Prefab references must be resolved by AssetDatabase, never by invented file IDs.
Use the editor menu Endless Savagery/Assets/Build Combat Delivery, or run this
helper with the project open and refresh the editor. No runtime code is needed.
"""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
request = root / 'ArtSource' / 'Delivery' / 'build.request'
request.parent.mkdir(parents=True, exist_ok=True)
request.write_text('Rebuild the combat art delivery via CombatAssetDelivery.\n', encoding='utf-8')
print('Request saved. Refresh the open project, or use the editor menu to build.')
