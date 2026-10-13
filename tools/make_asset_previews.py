from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SETS = [
    (ROOT / "ArtSource" / "AshenWatcher", "AshenWatcher_Dash", [1, 4, 8, 12, 19]),
    (ROOT / "ArtSource" / "Monsters" / "WildernessSlime", "WildernessSlime_Walk", [1, 5, 10, 14]),
    (ROOT / "ArtSource" / "Monsters" / "ShadowWolf", "ShadowWolf_Walk", [1, 5, 10, 14]),
    (ROOT / "ArtSource" / "Monsters" / "StoneGuardian", "StoneGuardian_Walk", [1, 7, 13, 19]),
    (ROOT / "ArtSource" / "VFX" / "PlayerOrbitBlades", "PlayerOrbitBlades", [1, 7, 13, 19, 25]),
]

for folder, stem, frames in SETS:
    images = [Image.open(folder / f"{stem}_{frame:02d}.png").convert("RGB") for frame in frames]
    images[0].save(folder / f"{stem}.gif", save_all=True, append_images=images[1:], duration=100, loop=0, optimize=True)
    for image in images:
        image.close()
