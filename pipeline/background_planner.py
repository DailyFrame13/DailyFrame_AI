import os, json
from background.selection import (
    select_background_with_llm,
    calculate_pixel_coordinates
)
from background.metadata import load_background_templates

def run_background_selection(result_path, PATHS):
    with open(result_path, "r", encoding="utf-8") as f:
        result_json = json.load(f)

    bg_templates = load_background_templates(PATHS["backgrounds"])

    # candidate_objects 만들기 (YOLO 결과 기반)
    candidate_objects = []
    for img in result_json["images"]:
        filename = img["filename"]
        for obj in img["objects"]:
            candidate_objects.append({
                "source_image": filename,
                "object_label": obj["label"],
                "rgba_path": obj["rgba_path"]
            })

    plan = select_background_with_llm(
        summary_data=result_json["images"],
        candidate_objects=candidate_objects
    )

    coords = calculate_pixel_coordinates(
        background_key=plan["selected_background"],
        object_placement_plan=plan["object_placement"],
        result_json=result_json
    )

    final = {
        "plan": plan,
        "coordinates": coords,
    }

    out_path = os.path.join(PATHS["base"], "composition_plan.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(final, f, ensure_ascii=False, indent=2)

    return final, out_path