import os, json
from glob import glob
from tqdm import tqdm
from models.yolo_seg import detect_objects
from models.clip_context import compute_scene_context

def run_analysis(PATHS):
    image_paths = sorted(glob(os.path.join(PATHS["uploads"], "*.*")))

    result = {"images": []}

    for path in tqdm(image_paths):
        objects = detect_objects(path, output_dir=PATHS["cutouts"])
        scene = compute_scene_context(path)

        result["images"].append({
            "filename": os.path.basename(path),
            "objects": objects,
            "scene_context": scene,
        })

    out_path = os.path.join(PATHS["base"], "result.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return result, out_path
