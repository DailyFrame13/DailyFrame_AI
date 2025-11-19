
import os
import json
from typing import List, Dict, Any
from huggingface_hub import InferenceClient


# =========================================================
# 🔹 1. HuggingFace 모델 설정 (토큰은 외부 환경 변수에서 입력)
# =========================================================
HF_MODEL = "google/gemma-2-2b-it"  # 모델 llava-hf/llava-v1.6-vicuna-7b-hf로 바꾸기 
HF_TOKEN = os.environ.get("HF_TOKEN", None)

if HF_TOKEN is None:
    print("⚠️ WARNING: HF_TOKEN 환경 변수가 설정되지 않았습니다. "
          "select_background_with_llm() 호출 시 오류가 날 수 있습니다.")

client = InferenceClient(model=HF_MODEL, token=HF_TOKEN)

# =========================================================
# 🔹 2. LLM 호출 함수
# =========================================================
def hf_generate(prompt: str) -> str | None:
    try:
        completion = client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.3,
        )

        msg = completion.choices[0].message
        content = msg.get("content", "")

        if isinstance(content, str):
            return content

        # content가 list 형식인 경우 (Gemma의 최신 출력 포맷)
        if isinstance(content, list):
            texts = []
            for part in content:
                if isinstance(part, dict) and part.get("type") == "text":
                    texts.append(part.get("text", ""))
            return "\n".join(texts)

        return str(content)

    except Exception as e:
        print("❌ HF 응답 오류:", e)
        return None


# =========================================================
# 🔹 3. Fallback background selection (LLM 실패 시)
# =========================================================
def fallback_background_selection(
    summary_data: List[Dict],
    BACKGROUND_TEMPLATES: Dict[str, Dict]
) -> Dict:
    """
    BACKGROUND_TEMPLATES를 main에서 전달받는 구조로 변경
    """
    if not BACKGROUND_TEMPLATES:
        raise RuntimeError("BACKGROUND_TEMPLATES가 비어 있습니다.")

    # 첫 번째 템플릿 사용
    selected_bg = list(BACKGROUND_TEMPLATES.keys())[0]
    bg_info = BACKGROUND_TEMPLATES[selected_bg]["metadata"]

    zones = [z[4] for z in bg_info.get("safe_zones", [])]
    zone_cycle = iter(zones) if zones else iter(["center"])

    object_placement = []

    for img in summary_data:
        filename = img.get("filename", "unknown")

        for obj in img.get("objects", []):
            label = obj.get("label")
            if not label:
                continue

            try:
                zone = next(zone_cycle)
            except StopIteration:
                zone_cycle = iter(zones) if zones else iter(["center"])
                zone = next(zone_cycle)

            object_placement.append({
                "object_label": label,
                "source_image": filename,
                "target_zone": zone,
                "priority": 5,
                "scale": 1.0,
            })

    return {
        "selected_background": selected_bg,
        "reasoning": "LLM 호출 실패 → fallback 적용",
        "overall_mood": bg_info.get("mood", ["neutral"])[0],
        "object_placement": object_placement,
    }


# =========================================================
# 🔹 4. LLM 기반 배경 선택 (main에서 BACKGROUND_TEMPLATES 전달)
# =========================================================
def select_background_with_llm(
    summary_data: List[Dict],
    candidate_objects: List[Dict],
    BACKGROUND_TEMPLATES: Dict[str, Dict]
) -> Dict:
    """
    summary_data: result.json["images"]
    candidate_objects: (source_image, object_label) 리스트
    BACKGROUND_TEMPLATES: load_background_templates() 결과
    """
    # -------- scene context summary --------
    all_objects = []
    all_moods = []
    all_activities = []
    all_backgrounds = []

    for img_data in summary_data:
        all_objects.extend(obj["label"] for obj in img_data.get("objects", []))
        all_moods.append(img_data["scene_context"]["style"]["label"])
        all_activities.append(img_data["scene_context"]["activity"]["label"])
        all_backgrounds.append(img_data["scene_context"]["background"]["label"])

    # -------- 배경 옵션 정리 --------
    bg_options = {}
    for key, info in BACKGROUND_TEMPLATES.items():
        meta = info["metadata"]
        bg_options[key] = {
            "mood": meta.get("mood", []),
            "category": meta.get("category", []),
            "suitable_objects": meta.get("suitable_objects", []),
            "zones": [z[4] for z in meta.get("safe_zones", [])],
        }

    # -------- LLM 프롬프트 생성 --------
    prompt = f"""
당신은 이미지 컴포지션 전문가입니다.
아래 3장의 이미지 분석 정보(`summary_data`)와 감지된 객체 후보(`candidate_objects`)를 바탕으로
최적의 배경과 객체 배치 JSON만 반환하세요.

--- 중간 생략(너의 코드 그대로) ---
""".strip()

    # -------- LLM 호출 --------
    try:
        reply = hf_generate(prompt)
        if reply is None:
            raise ValueError("HF returned None")

        json_str = reply.strip()

        # JSON만 추출
        if "{" in json_str:
            json_str = "{" + json_str.split("{", 1)[1]
        if "}" in json_str:
            json_str = json_str.rsplit("}", 1)[0] + "}"

        output = json.loads(json_str)

    except Exception as e:
        print(f"⚠️ LLM 호출 실패 → fallback 사용: {e}")
        output = fallback_background_selection(summary_data, BACKGROUND_TEMPLATES)

    return output


# =========================================================
# 🔹 5. 좌표 변환 함수 (BACKGROUND_TEMPLATES를 인자로 받는다)
# =========================================================
def calculate_pixel_coordinates(
    background_key: str,
    object_placement_plan: List[Dict],
    result_json: Dict,
    BACKGROUND_TEMPLATES: Dict[str, Dict]
) -> List[Dict]:
    """
    LLM 배치 결과(object_placement_plan)를 실제 픽셀 좌표로 변환
    """
    bg_entry = BACKGROUND_TEMPLATES[background_key]
    meta = bg_entry["metadata"]
    bg_zones = meta.get("safe_zones", [])

    if not bg_zones:
        print(f"⚠️ 배경 '{background_key}' 에 safe_zones 없음")
        return []

    zone_dict = {zone[4]: zone[:4] for zone in bg_zones}

    # -------- result.json 기반 객체 인덱싱 --------
    obj_index = {}
    label_index = {}

    for img in result_json.get("images", []):
        filename = img["filename"]
        for obj in img["objects"]:
            label = obj["label"]
            wrapped = {
                **obj,
                "source_filename": filename,
            }
            obj_index[(filename, label)] = wrapped
            label_index.setdefault(label, []).append(wrapped)

    placement_with_coords = []

    # -------- 배치 좌표 계산 --------
    for plan in object_placement_plan:
        zone_name = plan["target_zone"]

        if zone_name not in zone_dict:
            print(f"⚠️ zone '{zone_name}' 없음 → 첫 번째 zone 사용")
            zone_coords = bg_zones[0][:4]
            zone_name = bg_zones[0][4]
        else:
            zone_coords = zone_dict[zone_name]

        x1, y1, x2, y2 = zone_coords
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2

        src_img = plan["source_image"]
        obj_label = plan["object_label"]

        obj_info = obj_index.get((src_img, obj_label))

        if not obj_info and obj_label in label_index:
            print(f"⚠️ fallback: {src_img}에서 '{obj_label}' 못 찾음 → 다른 이미지의 동일 라벨 사용")
            obj_info = label_index[obj_label][0]

        if not obj_info:
            print(f"⚠️ '{obj_label}' 객체 정보 없음 → skip")
            continue

        # 원본 bbox 비율
        bbox = obj_info["bbox"]
        ow = bbox[2] - bbox[0]
        oh = bbox[3] - bbox[1]
        ratio = oh / max(ow, 1)

        # zone 크기
        zw = x2 - x1
        zh = y2 - y1

        fill_ratio = plan.get("scale", 0.9)

        tw = int(zw * fill_ratio)
        th = int(tw * ratio)

        if th > zh * fill_ratio:
            th = int(zh * fill_ratio)
            tw = int(th / ratio)

        final_x = center_x - tw // 2
        final_y = center_y - th // 2

        placement_with_coords.append({
            "object_label": obj_label,
            "source_image": obj_info["source_filename"],
            "rgba_path": obj_info["rgba_path"],
            "target_zone": zone_name,
            "coordinates": {"x": final_x, "y": final_y, "width": tw, "height": th},
            "priority": plan.get("priority", 5),
            "scale": fill_ratio,
        })

    placement_with_coords.sort(key=lambda x: x["priority"])

    return placement_with_coords