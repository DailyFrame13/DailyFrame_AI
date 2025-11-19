import os
from typing import Dict

BACKGROUND_METADATA = {
    # 희진
    "sns업로드_cozy.png": {
        "name": "sns_upload_cozy",
        "mood": ["cozy", "warm", "film_like", "aesthetic", "intimate"],
        "category": ["sns_upload", "cafe_mood", "interior_background"],
        "suitable_objects": ["person", "coffee_cup", "book", "stationery", "small_props"],
        "safe_zones": [
            (200, 850, 900, 1300, "table_area"),
            (150, 300, 450, 650, "left_wall_art"),
            (500, 280, 800, 620, "right_wall_art"),
            (250, 650, 500, 900, "lamp_glow_zone"),
            (100, 900, 400, 1500, "left_chair_area"),
            (600, 900, 1000, 1500, "right_chair_area")
        ],
        "description": "따뜻한 필름 톤의 카페 한 켠 분위기 — 조명 아래 작은 테이블과 커피가 있는 cozy aesthetic 공간"
    },
    "sns업로드_aesthetic.png": {
        "name": "sns_upload_aesthetic",
        "mood": ["aesthetic", "minimal", "soft_light", "calm", "clean"],
        "category": ["sns_upload", "minimal_interior", "workspace_background"],
        "suitable_objects": ["person", "laptop", "book", "pen", "coffee_cup", "stationery"],
        "safe_zones": [
            (100, 850, 900, 1350, "desk_surface"),
            (650, 300, 950, 650, "right_wall_photos"),
            (120, 250, 500, 800, "window_light_area"),
            (400, 850, 650, 1150, "cup_zone"),
            (650, 900, 950, 1250, "notebook_zone")
        ],
        "description": "부드러운 자연광이 들어오는 미니멀한 작업 공간 — 깨끗하고 정돈된 aesthetic 무드의 SNS 업로드용 배경"
    },
    "sns업로드_filmlike.png": {
        "name": "sns_upload_filmlike",
        "mood": ["film_like", "moody", "evening_glow", "aesthetic", "quiet"],
        "category": ["sns_upload", "cafe_mood", "night_scene", "film_color"],
        "suitable_objects": ["person", "coffee_cup", "book", "glasses", "bag", "small_props"],
        "safe_zones": [
            (150, 900, 900, 1400, "table_area"),
            (350, 930, 650, 1200, "cup_zone"),
            (100, 300, 550, 750, "window_view_zone"),
            (600, 350, 900, 700, "wall_frame_zone"),
            (150, 950, 350, 1450, "left_chair_area"),
            (650, 950, 950, 1450, "right_chair_area")
        ],
        "description": "보랏빛 저녁 하늘과 실내의 어두운 카페 톤이 어우러진 필름 라이크 무드 — 고요하고 감성적인 SNS 업로드용 배경"
    },
    "프로필브랜딩_clean.png": {
        "name": "profile_branding_clean",
        "mood": ["clean", "minimal", "bright", "fresh", "calm"],
        "category": ["profile_branding", "studio_background", "minimal_interior"],
        "suitable_objects": ["person", "text_overlay", "logo", "product_small", "plant"],
        "safe_zones": [
            (400, 200, 1100, 900, "right_blank_wall"),
            (150, 900, 950, 1450, "table_surface"),
            (100, 250, 500, 950, "left_plant_zone"),
            (550, 300, 950, 700, "frame_area"),
            (350, 950, 650, 1350, "center_table_zone")
        ],
        "description": "밝고 미니멀한 인테리어 — 깨끗한 여백과 식물이 포인트가 되는 프로필·브랜딩용 클린 무드 배경"
    },
    "프로필브랜딩_minimal.png": {
        "name": "profile_branding_minimal",
        "mood": ["minimal", "clean", "neutral", "bright", "simple"],
        "category": ["profile_branding", "studio_background", "blank_space"],
        "suitable_objects": ["person", "text_overlay", "logo", "product", "small_props"],
        "safe_zones": [
            (100, 150, 1100, 900, "blank_wall_area"),
            (100, 900, 1100, 1400, "table_surface"),
            (350, 250, 900, 650, "center_wall_text_zone"),
            (300, 950, 800, 1350, "center_product_zone")
        ],
        "description": "밝고 여백이 넓은 미니멀 브랜딩용 배경 — 로고, 텍스트, 인물, 제품 배치를 모두 지원하는 심플한 스튜디오 톤"
    },
    "프로필브랜딩_professional.png": {
        "name": "profile_branding_professional",
        "mood": ["professional", "clean", "structured", "minimal", "modern"],
        "category": ["profile_branding", "workspace_background", "business_style"],
        "suitable_objects": ["person", "laptop", "logo", "text_overlay", "documents", "stationery"],
        "safe_zones": [
            (100, 100, 1100, 750, "upper_blank_wall"),
            (100, 780, 1100, 1400, "desk_surface"),
            (350, 200, 950, 650, "center_wall_text_zone"),
            (150, 880, 500, 1250, "left_notebook_area"),
            (600, 880, 1000, 1250, "pen_holder_zone")
        ],
        "description": "모던하고 정돈된 업무용 책상 구성 — 전문적이고 깔끔한 인상을 주는 프로필·브랜딩용 배경"
    },
    "여행기록_scenic.png": {
        "name": "travel_log_scenic",
        "mood": ["scenic", "fresh", "open", "bright", "relaxing"],
        "category": ["travel_log", "outdoor_scenery", "beach_view"],
        "suitable_objects": ["person", "backpack", "hat", "camera", "drink_bottle", "travel_props"],
        "safe_zones": [
            (100, 850, 1100, 1350, "deck_foreground"),
            (100, 650, 1100, 900, "sand_beach"),
            (100, 400, 1100, 650, "shallow_water_zone"),
            (100, 100, 1100, 400, "sky_area"),
            (850, 700, 1100, 950, "rock_side_zone")
        ],
        "description": "맑은 하늘과 에메랄드빛 바다가 펼쳐진 시원한 해변 풍경 — 여행 기록 및 감성적인 전망 컷에 적합한 배경"
    },
    # 태영
    "콘텐츠제작_bold.png": {
        "name": "desk_creator_dual_light",
        "mood": ["bold", "modern", "techy", "dramatic"],
        "category": ["creator_setup", "gaming_room", "streamer_desk", "sns_upload"],
        "suitable_objects": ["headphones", "mouse", "notebook", "coffee_cup", "tablet", "small_figurine"],
        "safe_zones": [
            (150, 600, 450, 900, "left_microphone_area"),
            (500, 550, 900, 900, "right_monitor_area"),
            (250, 750, 850, 1100, "keyboard_front_area"),
            (0, 400, 1080, 650, "wall_gradient_background")
        ],
        "description": "레드-블루 투톤의 감각적인 크리에이터 데스크 셋업. 모니터와 키보드, 마이크 실루엣이 강조된 현대적인 작업 공간 분위기."
    },
    "콘텐츠제작_eyecatching.png": {
        "name": "dark_spotlight_room",
        "mood": ["dramatic", "moody", "minimal", "studio"],
        "category": ["product_shoot", "portrait_studio", "dramatic_scene", "creative_content"],
        "suitable_objects": ["person", "chair", "box", "statue", "product_item", "lamp"],
        "safe_zones": [
            (200, 650, 850, 1100, "spotlight_center_floor"),
            (150, 450, 900, 700, "mid_floor_zone"),
            (0, 300, 1080, 500, "deep_background_wall"),
            (380, 0, 700, 200, "top_light_cone")
        ],
        "description": "어두운 밀폐 공간 위로 스포트라이트만 떨어지는 미니멀 스튜디오. 제품, 인물, 오브젝트의 드라마틱한 연출에 적합한 무드."
    },
    "친구연애_warm.png": {
        "name": "cozy_sunlit_cafe",
        "mood": ["warm", "cozy", "sunlit", "minimal", "calm"],
        "category": ["cafe_aesthetic", "daily_life", "sns_upload", "morning_vibes", "content_creation"],
        "suitable_objects": ["cup", "dessert", "notebook", "book", "plant_small", "phone", "cutlery", "glasses"],
        "safe_zones": [
            (250, 650, 900, 1100, "table_surface"),
            (150, 500, 400, 780, "left_table_edge"),
            (0, 200, 600, 650, "window_area"),
            (600, 250, 1080, 800, "wall_shelf_zone")
        ],
        "description": "따뜻한 햇살이 창가로 들어오는 조용한 코지 카페. 우드 톤의 테이블과 의자가 편안한 분위기를 만드는 공간."
    },
    "친구연애_nostalgic.png": {
        "name": "warm_polaroid_desk",
        "mood": ["warm", "nostalgic", "soft", "afternoon_light", "sentimental"],
        "category": ["journal", "memory_record", "sns_upload", "creative_flatlay", "stationery_setup"],
        "suitable_objects": ["pen", "paper", "notebook", "photos", "postcard", "flower_small", "coffee_cup", "sticker"],
        "safe_zones": [
            (0, 600, 1080, 1450, "bottom_table_area"),
            (100, 300, 950, 650, "mid_table_area"),
            (200, 0, 900, 300, "top_light_stripes"),
            (750, 800, 1080, 1450, "right_pencil_zone")
        ],
        "description": "따뜻한 빛이 내려앉는 우드 테이블 위에 폴라로이드와 연필이 흩어진 감성적인 책상. 기록, 작업, 추억 연출에 적합한 분위기."
    },
    "친구연애_romantic.png": {
        "name": "romantic_candle_dinner",
        "mood": ["romantic", "warm", "intimate", "evening", "cinematic"],
        "category": ["date_night", "fine_dining", "restaurant_scene", "couple_mood", "aesthetic_upload"],
        "suitable_objects": ["wine_bottle", "flower_small", "menu_card", "ring_box", "dessert", "cutlery", "plate"],
        "safe_zones": [
            (250, 650, 830, 1100, "table_center"),
            (150, 500, 450, 830, "left_table_side"),
            (650, 500, 1050, 830, "right_table_side"),
            (300, 0, 800, 500, "candle_background_glow"),
            (0, 300, 1080, 600, "bokeh_background")
        ],
        "description": "은은한 촛불 조명 아래 두 개의 와인잔이 놓인 로맨틱한 디너 테이블. 따뜻하고 친밀한 분위기의 저녁 식사 장면에 적합한 배경."
    },
    "학교업무_neutral.png": {
        "name": "warm_study_desk",
        "mood": ["warm", "focused", "calm", "academic", "morning_light"],
        "category": ["study_space", "library_corner", "note_writing", "daily_routine", "sns_upload"],
        "suitable_objects": ["notebook", "pen", "coffee_cup", "laptop", "glasses", "stationery", "small_book_stack", "tablet"],
        "safe_zones": [
            (250, 700, 900, 1450, "main_desk_area"),
            (50, 450, 450, 850, "left_book_stack_zone"),
            (450, 450, 950, 850, "notebook_center_zone"),
            (200, 0, 800, 400, "window_light_zone"),
            (900, 200, 1080, 900, "bookshelf_side_zone")
        ],
        "description": "잔잔한 햇살이 들어오는 도서관/서재 공부 공간. 나무 책상 위에 책과 노트, 텀블러가 놓인 차분하고 집중하기 좋은 분위기."
    },
    "학교업무_informative.png": {
        "name": "clean_meeting_room",
        "mood": ["clean", "minimal", "professional", "bright", "organized"],
        "category": ["meeting_room", "office_space", "study_room", "presentation_setup", "teamwork_space"],
        "suitable_objects": ["laptop", "notebook", "pen", "coffee_cup", "sticky_notes", "tablet", "nameplate", "documents"],
        "safe_zones": [
            (150, 750, 950, 1450, "table_main_area"),
            (0, 200, 1080, 650, "whiteboard_area"),
            (300, 700, 780, 900, "center_table_focus"),
            (150, 0, 950, 200, "ceiling_light_zone")
        ],
    },
    # 예영
    "여행기록_cinematic.png": {
        "name": "neon_city_street",
        "mood": ["moody", "cinematic", "noir", "neon", "lonely"],
        "category": ["travel_log", "city_walk", "aesthetic_scene", "content_creation"],
        "suitable_objects": ["umbrella", "person", "neon_sign", "street_lights", "bag"],
        "safe_zones": [
            (50, 600, 350, 1100, "left_neon_area"),
            (400, 500, 900, 1100, "center_street_reflection"),
            (600, 200, 950, 600, "right_upper_dark_area"),
            (100, 300, 500, 650, "left_mid_building")
        ],
        "description": "네온사인과 어두운 골목이 대비되는 밤거리, 영화 같은 어반 무드"
    },
    "라이프로그_fresh.png": {
        "name": "sunlit_desk_plants",
        "mood": ["calm", "fresh", "minimal", "cozy", "natural"],
        "category": ["lifestyle", "study_setup", "workspace", "aesthetic_scene"],
        "suitable_objects": ["notebook", "pen", "glass", "plant", "laptop", "coffee_cup"],
        "safe_zones": [
            (100, 650, 450, 1100, "desk_left_area"),
            (500, 600, 900, 1100, "desk_right_area"),
            (50, 150, 350, 450, "left_plant_zone"),
            (600, 150, 950, 450, "right_plant_zone")
        ],
        "description": "따뜻한 햇빛 아래 미니멀한 책상과 식물들이 있는 차분한 데일리 무드"
    },
    "라이프로그_casual.png": {
        "name": "coffee_brunch_table",
        "mood": ["cozy", "warm", "calm", "minimal", "comfort"],
        "category": ["cafe_moment", "lifestyle", "brunch", "sns_upload"],
        "suitable_objects": ["coffee", "latte", "sandwich", "notebook", "phone"],
        "safe_zones": [
            (100, 750, 500, 1100, "front_latte_area"),
            (450, 600, 900, 1100, "sandwich_area"),
            (120, 400, 450, 650, "back_coffee_area"),
            (50, 200, 900, 380, "table_top_space")
        ],
        "description": "따뜻한 카페 분위기에서 라떼·아메리카노·샌드위치가 놓인 아늑한 브런치 무드"
    },
    "라이프로그_cozydaily.png": {
        "name": "sunlit_window_reading",
        "mood": ["calm", "warm", "serene", "soft", "minimal"],
        "category": ["lifestyle", "home_aesthetic", "reading_moment", "sns_upload"],
        "suitable_objects": ["book", "flowers", "cup", "candle", "notebook"],
        "safe_zones": [
            (120, 750, 550, 1100, "table_left_space"),
            (550, 700, 900, 1100, "table_right_space"),
            (200, 300, 450, 650, "curtain_left_area"),
            (550, 250, 900, 600, "curtain_right_area")
        ],
        "description": "부드러운 햇살이 드는 창가, 책과 꽃이 놓인 따뜻하고 고요한 무드"
    },
    "패션메이크업_trendy.png": {
        "name": "pastel_street_bench",
        "mood": ["fresh", "calm", "sunny", "minimal", "pastel"],
        "category": ["travel_log", "street_aesthetic", "daylight_scene", "sns_upload"],
        "suitable_objects": ["person", "bag", "bicycle", "coffee_cup"],
        "safe_zones": [
            (120, 750, 550, 1100, "sidewalk_front_area"),
            (550, 600, 900, 1100, "road_right_area"),
            (150, 450, 500, 700, "bench_zone"),
            (600, 200, 900, 500, "building_right_zone")
        ],
        "description": "파스텔톤 건물이 늘어선 골목과 햇살 아래 벤치가 있는 산뜻한 데일리 스트리트 무드"
    },
    "패션메이크업_chic.png": {
        "name": "gold_beauty_vanity",
        "mood": ["luxury", "elegant", "chic", "warm", "premium"],
        "category": ["beauty_styling", "product_aesthetic", "vanity_setup", "sns_upload"],
        "suitable_objects": ["perfume", "lipstick", "mirror", "jewelry", "skincare"],
        "safe_zones": [
            (80, 650, 450, 1100, "tray_left_area"),
            (450, 650, 900, 1100, "tray_right_area"),
            (100, 300, 350, 600, "mirror_zone"),
            (500, 250, 900, 550, "frame_background_zone")
        ],
        "description": "골드 톤의 거울·향수·립스틱이 조화된 고급스러운 뷰티 스타일링 무드"
    },
    "패션메이크업_stylish.png": {
        "name": "pastel_makeup_glasschair",
        "mood": ["trendy", "stylish", "soft", "minimal", "pastel"],
        "category": ["beauty_styling", "product_aesthetic", "fashion_editorial", "sns_upload"],
        "suitable_objects": ["lipstick", "eyeshadow", "compact", "mirror", "accessories"],
        "safe_zones": [
            (120, 750, 550, 1100, "glass_table_left"),
            (550, 750, 900, 1100, "glass_table_right"),
            (150, 350, 500, 650, "left_gradient_background"),
            (550, 300, 900, 650, "right_gradient_background")
        ],
        "description": "파스텔 조명 아래 투명 의자와 유리 상판 위에 놓인 립스틱·아이팔레트가 강조된 트렌디한 뷰티 무드"
    }
}


def load_background_templates(background_dir: str) -> Dict[str, Dict]:
    """
    BACKGROUND_METADATA + 실제 이미지 파일을 합쳐 BACKGROUND_TEMPLATES를 만든다.
    """
    templates: Dict[str, Dict] = {}

    for filename, meta in BACKGROUND_METADATA.items():
        image_path = os.path.join(background_dir, filename)

        if not os.path.exists(image_path):
            print(f"⚠️ 배경 이미지 파일을 찾을 수 없습니다: {image_path}")
            continue

        template_key = meta.get("name") or os.path.splitext(filename)[0]
        safe_zones = meta.get("safe_zones", [])
        if not safe_zones:
            print(f"⚠️ '{template_key}' 템플릿에 safe_zones가 없습니다. (파일: {filename})")

        templates[template_key] = {
            "image_path": image_path,
            "metadata": meta,
        }

    return templates
    