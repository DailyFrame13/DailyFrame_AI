# ================================================
# 🧠 HuggingFace Gemma 기반 배경 선정 함수 (신규 API)
# ================================================
import json, os
import difflib
from typing import List, Dict, Optional
from huggingface_hub import InferenceClient
from dotenv import load_dotenv 
from openai import OpenAI 

load_dotenv()

HF_MODEL = "meta-llama/Meta-Llama-3-8B-Instruct"

# ✅ HF Router용 OpenAI 클라이언트
hf_client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.environ["HF_TOKEN"],
)


def hf_generate(prompt: str) -> str | None:
    try:
        completion = hf_client.chat.completions.create(
            model=HF_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.3,
        )

        content = completion.choices[0].message.content
        return content or ""

    except Exception as e:
        print("❌ HF 응답 오류:", e)
        return None


# ----------------------------------------------------
# ⭐ fuzzy zone matcher
# ----------------------------------------------------
def fuzzy_match_zone(requested_zone: str, available_zones: List[str]) -> str:
    # 🔥 방어 로직 추가
    if not available_zones:
        print(f"⚠️ fuzzy_match_zone: available_zones 비어있음 → '{requested_zone}' 그대로 반환")
        return requested_zone

    if requested_zone in available_zones:
        return requested_zone

    matches = difflib.get_close_matches(requested_zone, available_zones, n=1, cutoff=0.0)
    if matches:
        print(f"🔄 fuzzy zone match: '{requested_zone}' → '{matches[0]}'")
        return matches[0]

    print(f"⚠️ zone '{requested_zone}' matched none → fallback '{available_zones[0]}'")
    return available_zones[0]



# ----------------------------------------------------
# ⭐ fuzzy object-label matcher (새로 추가됨)
# ----------------------------------------------------
def fuzzy_match_label(llm_label: str, available_labels: List[str]) -> str:
    """
    YOLO가 감지한 label 목록에서 LLM이 제공한 label을 가장 비슷하게 맞춰준다.
    """
    # 🔥 방어 로직 추가
    if not available_labels:
        print(f"⚠️ fuzzy_match_label: available_labels 비어있음 → '{llm_label}' 그대로 반환")
        return llm_label

    if llm_label in available_labels:
        return llm_label

    matches = difflib.get_close_matches(llm_label, available_labels, n=1, cutoff=0.0)
    if matches:
        print(f"🔍 label fuzzy match: '{llm_label}' → '{matches[0]}'")
        return matches[0]

    print(f"⚠️ object label '{llm_label}' matched none → fallback '{available_labels[0]}'")
    return available_labels[0]


def fallback_background_selection(
    summary_data: List[Dict],
    candidate_objects: List[Dict],
    BACKGROUND_TEMPLATES: Dict,
) -> Dict:
    """
    HF가 죽었을 때 사용할 간단한 배경/배치 전략:
    - suitable_objects와 겹치는 객체가 많은 배경을 선택
    - zone 이름과 object_label이 비슷하면 거기에 배치
    - 나머지는 첫 번째 zone에 몰아넣기
    """

    if not BACKGROUND_TEMPLATES:
        raise ValueError("BACKGROUND_TEMPLATES is empty")

    # 1) 후보 객체 label 모으기
    object_labels = [obj["object_label"] for obj in candidate_objects]

    # 2) suitable_objects overlap 최대인 배경 선택
    best_bg_key = None
    best_score = -1

    for key, info in BACKGROUND_TEMPLATES.items():
        meta = info["metadata"]
        suitable = meta.get("suitable_objects", [])
        score = len(set(object_labels) & set(suitable))
        if score > best_score:
            best_score = score
            best_bg_key = key

    # 안전장치: 그래도 못 찾으면 첫 번째
    if best_bg_key is None:
        best_bg_key = next(iter(BACKGROUND_TEMPLATES.keys()))

    bg_meta = BACKGROUND_TEMPLATES[best_bg_key]["metadata"]
    zones = bg_meta.get("safe_zones", [])
    if not zones:
        # zone이 진짜 하나도 없으면 그냥 첫 번째 키만 반환
        return {
            "selected_background": best_bg_key,
            "reasoning": "fallback: no zones defined, background only",
            "overall_mood": "fallback",
            "object_placement": [],
        }

    zone_names = [z[4] for z in zones]

    placements = []
    for idx, obj in enumerate(candidate_objects):
        label = obj["object_label"]
        src = obj["source_image"]

        # label 이랑 비슷한 이름의 zone 있으면 우선 사용
        chosen_zone = None
        for zn in zone_names:
            if label in zn or zn in label:
                chosen_zone = zn
                break
        if chosen_zone is None:
            # 없으면 round-robin 으로 배치
            chosen_zone = zone_names[idx % len(zone_names)]

        placements.append({
            "object_label": label,
            "source_image": src,
            "target_zone": chosen_zone,
            "priority": 5,
            "scale": 0.8,
        })

    return {
        "selected_background": best_bg_key,
        "reasoning": "fallback: HF 호출 실패, suitable_objects & zone 이름 기반으로 자동 선택",
        "overall_mood": "fallback",
        "object_placement": placements,
    }



# ----------------------------------------------------
# ⭐ select_background_with_llm (fuzzy zone + label matching)
# ----------------------------------------------------
def select_background_with_llm(
    summary_data: List[Dict],
    candidate_objects: List[Dict],
    BACKGROUND_TEMPLATES: Dict
) -> Dict:

    # -----------------------------
    # ① summary_data 분석
    # -----------------------------
    all_objects, all_moods, all_activities, all_backgrounds = [], [], [], []

    for img_data in summary_data:
        all_objects.extend(obj["label"] for obj in img_data.get("objects", []))

        ctx = img_data.get("scene_context", {})
        style = ctx.get("style", {})
        activity = ctx.get("activity", {})
        background = ctx.get("background", {})

        if style.get("label"):
            all_moods.append(style["label"])
        if activity.get("label"):
            all_activities.append(activity["label"])
        if background.get("label"):
            all_backgrounds.append(background["label"])

    # -----------------------------
    # ② background template options
    # -----------------------------
    bg_options = {}
    for key, info in BACKGROUND_TEMPLATES.items():
        meta = info["metadata"]
        bg_options[key] = {
            "mood": meta["mood"],
            "category": meta["category"],
            "suitable_objects": meta["suitable_objects"],
            "zones": [z[4] for z in meta["safe_zones"]],
        }

    # -----------------------------
    # ③ prompt (그대로 유지)
    # -----------------------------
    prompt = f"""
당신은 이미지 컴포지션 전문가입니다.
아래 summary_data(3장의 사진 분석)와 candidate_objects(감지된 객체 리스트)를 기반으로
최적의 배경 하나를 선택을 선택하고, 최적의 객체 배치 JSON만 반환하세요.

------------------------------------------------------------
📌 사용 가능한 배경 템플릿 (zones 목록 포함)
------------------------------------------------------------
{json.dumps(bg_options, ensure_ascii=False, indent=2)}

[selected_background 규칙]
selected_background는 반드시 아래 목록에 있는 키 중 하나만 선택해야 합니다.
새로운 이름을 만들면 안 됩니다.

가능한 background key 목록:
{list(BACKGROUND_TEMPLATES.keys())}
zone 하나에 객체 하나만을 배치합니다.
------------------------------------------------------------
📌 배치 가능한 객체 목록
------------------------------------------------------------
{json.dumps(candidate_objects, ensure_ascii=False, indent=3)}
📌 중요 규칙:suitable_objects는 고려하지 않습니다.
키보드, 노트북, 컵, 스마트폰, 책과 같은 책상용 객체는 반드시 desk 관련 zone에 배치해야 합니다.
창문 또는 벽 zone에는 책상용 객체를 배치하면 안 됩니다.
zone과 객체의 이름이 비슷하면 동일하게 배치합니다.(ex. cup과 cup_zone)
------------------------------------------------------------

📌 출력(JSON만)
------------------------------------------------------------
반드시 **유효한 JSON만** 출력하세요.

- 한국어 설명 문장, 마크다운, ``` 코드블럭, 주석, 자연어는 절대 출력하지 마세요.
- JSON 객체 하나만 출력합니다.
- 마지막 요소 뒤에 쉼표(,)를 절대 붙이지 마세요.
- 모든 키와 문자열은 큰따옴표(")를 사용하세요.
- true/false/null 은 문자열이 아니라 JSON 리터럴로 사용하세요.

출력 형식 예시는 아래와 같으며, 실제 값만 바꿔서 그대로 출력합니다.

{{
  "selected_background": "<BACKGROUND_TEMPLATES key 중 하나>",
  "reasoning": "선택 이유",
  "overall_mood": "<무드>",
  "object_placement": [
    {{
      "object_label": "<candidate_objects 안의 object_label>",
      "source_image": "<candidate_objects 안의 source_image>",
      "target_zone": "<safe_zones 중 하나>",
      "priority": 5,
      "scale": 0.8
    }}
  ]
}}
""".strip()

    # -----------------------------
    # ④ LLM 호출
    # -----------------------------
    try:
        reply = hf_generate(prompt)
        if reply is None:
            raise ValueError("HF returned None")

        json_str = reply.strip()

        if "{" in json_str:
            json_str = "{" + json_str.split("{", 1)[1]
        if "}" in json_str:
            json_str = json_str.rsplit("}", 1)[0] + "}"

        llm_decision = json.loads(json_str)

    except Exception as e:
        print(f"⚠️ HF 호출 실패 → fallback 사용: {e}")
        return fallback_background_selection(summary_data, candidate_objects, BACKGROUND_TEMPLATES)


    # ------------------------------------------------------------
    # ⭐ ⑤ zone fuzzy matching
    # ------------------------------------------------------------
    bg_key = llm_decision.get("selected_background")

    if bg_key not in BACKGROUND_TEMPLATES:
        print(f"⚠️ LLM이 unknown background '{bg_key}' 반환 → fallback 사용")
        return fallback_background_selection(summary_data, candidate_objects, BACKGROUND_TEMPLATES)


    available_zones = [z[4] for z in BACKGROUND_TEMPLATES[bg_key]["metadata"]["safe_zones"]]

    # ------------------------------------------------------------
    # ⭐ ⑥ object_label fuzzy matching
    # ------------------------------------------------------------
    available_labels = [obj["object_label"] for obj in candidate_objects]

    for obj in llm_decision.get("object_placement", []):
        # 1) object_label 보정
        if "object_label" in obj:
            obj["object_label"] = fuzzy_match_label(obj["object_label"], available_labels)

        # 2) target_zone 보정
        if "target_zone" in obj:
            obj["target_zone"] = fuzzy_match_zone(obj["target_zone"], available_zones)

    return llm_decision


# =========================================================
# 🔹 5. 좌표 변환 함수 (BACKGROUND_TEMPLATES를 인자로 받는다)
# =========================================================
def calculate_pixel_coordinates(
    background_key: str,
    object_placement_plan: List[Dict],
    result_json: Dict,
    BACKGROUND_TEMPLATES: Dict,
) -> List[Dict]:

    # 객체별 고정 크기(px)
    OBJECT_SIZE_PRESET = {
        "cup": 380,
        "mug": 380,
        "coffee_cup": 380,
        "laptop": 500,
        "notebook_pc": 480,
        "smartphone": 260,
        "phone": 260,
        "cellphone": 260,
        "book": 320,
        "notebook": 320,
        "pen": 180,
        "pencil": 180,
        "bottle": 400,
        "sandwich": 200,
        "keyboard": 400,
        "mouse": 180,
        "person": 700,
        "fork": 250,
        "wine glass": 400,
        "_default": 200,
    }

    # --------------------------------------------------------
    # 1) 배경/zone 로드
    # --------------------------------------------------------
    bg_entry = BACKGROUND_TEMPLATES[background_key]
    meta = bg_entry["metadata"]
    bg_zones = meta.get("safe_zones", [])

    if not bg_zones:
        print(f"⚠️ 배경 '{background_key}' 에 safe_zones 없음.")
        return []

    # zone 이름 → 좌표 매핑
    zone_dict = {zone[4]: zone[:4] for zone in bg_zones}

    # fallback zone은 첫 번째 zone
    fallback_zone_name = bg_zones[0][4]
    fallback_zone_coords = bg_zones[0][:4]

    # --------------------------------------------------------
    # 2) result.json 객체 인덱스 구성
    # --------------------------------------------------------
    obj_index = {}
    label_index = {}

    for img in result_json.get("images", []):
        filename = img.get("filename")
        for obj in img.get("objects", []):
            label = obj.get("label")
            wrapped = {**obj, "source_filename": filename}
            obj_index[(filename, label)] = wrapped
            label_index.setdefault(label, []).append(wrapped)

    placement_with_coords = []

    # --------------------------------------------------------
    # 3) 배치 시작
    # --------------------------------------------------------
    for plan in object_placement_plan:

        zone_name = plan.get("target_zone", "")

        # ⭐ zone 이름이 정확히 없으면 fallback zone
        if zone_name not in zone_dict:
            print(f"⚠️ zone '{zone_name}' 없음 → fallback '{fallback_zone_name}' 사용")
            zone_coords = fallback_zone_coords
            zone_name = fallback_zone_name
        else:
            zone_coords = zone_dict[zone_name]

        x1, y1, x2, y2 = zone_coords

        # zone 중심
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2

        # 객체 찾기
        source_image = plan.get("source_image")
        object_label = plan.get("object_label")

        obj_info = obj_index.get((source_image, object_label))
        if not obj_info:
            candidates = label_index.get(object_label, [])
            obj_info = candidates[0] if candidates else None

        if not obj_info:
            print(f"⚠️ 객체 `{object_label}` 찾지 못함")
            continue

        # --------------------------------------------------------
        # ⭐ 핵심: 객체 label별 고정 크기 preset
        # --------------------------------------------------------
        preset_size = OBJECT_SIZE_PRESET.get(object_label, OBJECT_SIZE_PRESET["_default"])
        new_w = preset_size
        new_h = preset_size

        # 중심 배치
        final_x = center_x - new_w // 2
        final_y = center_y - new_h // 2

        placement_with_coords.append({
            "object_label": object_label,
            "source_image": obj_info["source_filename"],
            "rgba_path": obj_info["rgba_path"],
            "target_zone": zone_name,
            "coordinates": {
                "x": final_x,
                "y": final_y,
                "width": new_w,
                "height": new_h
            },
            "priority": plan.get("priority", 5),
        })

    placement_with_coords.sort(key=lambda x: x["priority"])
    return placement_with_coords