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
    full_frames = sorted((folder / "PreviewFrames").glob("*.png"))
    if not full_frames:
        raise RuntimeError("Render the full cycle before creating previews: " + str(folder))
    images = [Image.open(file).convert("RGB") for file in full_frames]
    # GIF delay uses 10 ms units. 30/30/40 ms totals exactly 30 frames per second.
    durations = [30 if i % 3 != 2 else 40 for i in range(len(images))]
    if stem == "AshenWatcher_Dash":
        durations[-1] += 500
    images[0].save(folder / f"{stem}.gif", save_all=True, append_images=images[1:], duration=durations, loop=0, optimize=True)
    for image in images:
        image.close()
