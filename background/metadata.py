import os
from typing import Dict


BACKGROUND_METADATA = {
    # 희진
    "sns업로드_cozy.png": {
        "name": "sns_upload__cozy",
        "mood": ["cozy", "warm", "film_like", "aesthetic", "intimate"],
        "category": ["sns_upload", "cafe_mood", "interior_background"],
        "suitable_objects": ["person", "coffee_cup", "book", "stationery", "small_props"],
        "safe_zones": [
            # (150, 1000, 360, 1200, "sns_upload__cozy__table_left"),
            # (570, 1040, 720, 1150, "sns_upload__cozy__cup"),
            (200, 900, 360, 1000, "sns_upload__cozy__table_left"),

        ],
        "description": "따뜻한 필름 톤의 카페 한 켠 분위기 — 조명 아래 작은 테이블과 커피가 있는 cozy aesthetic 공간"
    },
    "sns업로드_aesthetic.png": {
        "name": "sns_upload__aesthetic",
        "mood": ["aesthetic", "minimal", "soft_light", "calm", "clean"],
        "category": ["sns_upload", "minimal_interior", "workspace_background"],
        "suitable_objects": ["person", "laptop", "book", "pen", "coffee_cup", "stationery"],
        "safe_zones": [
            (100, 1100, 300, 1350, "sns_upload__aesthetic__desk_side"),
            (310, 1100, 590, 1350, "sns_upload__aesthetic__desk_middle"),
            #(400, 0, 950, 500, "sns_upload_aesthetic__wall"),
            #(0, 0, 270, 1000, "sns_upload_aesthetic__window"),
            (600, 1080, 760, 1230, "sns_upload__aesthetic__cup_zone"),
            (600, 1250, 920, 1380, "sns_upload__aesthetic__notebook_zone"),
            #(695, 550, 785, 680, "sns_upload_aesthetic__frame_right"),
            #(570, 730, 655, 850, "sns_upload_aesthetic__frame_left")
        ],
        "description": "부드러운 자연광이 들어오는 미니멀한 작업 공간 — 깨끗하고 정돈된 aesthetic 무드의 SNS 업로드용 배경"
    },
    "sns업로드_filmlike.png": {
        "name": "sns_upload__filmlike",
        "mood": ["film_like", "moody", "evening_glow", "aesthetic", "quiet"],
        "category": ["sns_upload", "cafe_mood", "night_scene", "film_color"],
        "suitable_objects": ["person", "coffee_cup", "book", "glasses", "bag", "small_props"],
        "safe_zones": [
            (100, 1100, 330, 1300, "sns_upload__filmlike__table_left"),
            (570, 1100, 750, 1300, "sns_upload__filmlike__table_right"),
            (350, 1080, 550, 1200, "sns_upload__filmlike__cup"),
            (650, 1300, 950, 1450, "sns_upload__filmlike__chair_right"),
            (0, 1450, 300, 1600, "sns_upload__filmlike__chair_left")
        ],
        "description": "보랏빛 저녁 하늘과 실내의 어두운 카페 톤이 어우러진 필름 라이크 무드 — 고요하고 감성적인 SNS 업로드용 배경"
    },
    "프로필브랜딩_clean.png": {
        "name": "profile_branding__clean",
        "mood": ["clean", "minimal", "bright", "fresh", "calm"],
        "category": ["profile_branding", "studio_background", "minimal_interior"],
        "suitable_objects": ["person", "text_overlay", "logo", "product_small", "plant"],
        "safe_zones": [
            (100, 600, 300, 1450, "profile_branding__clean__plant_big"),
            (400, 840, 570, 1080, "profile_branding__clean__plant_small"),
            (600, 390, 820, 690, "profile_branding__clean__frame"),
            (600, 1000, 900, 1100, "profile_branding__clean__table"),
            (450, 1250, 850, 1500, "profile_branding__clean__under")
        ],
        "description": "밝고 미니멀한 인테리어 — 깨끗한 여백과 식물이 포인트가 되는 프로필·브랜딩용 클린 무드 배경"
    },
    "프로필브랜딩_minimal.png": {
        "name": "profile_branding__minimal",
        "mood": ["minimal", "clean", "neutral", "bright", "simple"],
        "category": ["profile_branding", "studio_background", "blank_space"],
        "suitable_objects": ["person", "text_overlay", "logo", "product", "small_props"],
        "safe_zones": [
            (350, 650, 900, 1000, "profile_branding__minimal__wall")
        ],
        "description": "밝고 여백이 넓은 미니멀 브랜딩용 배경 — 로고, 텍스트, 인물, 제품 배치를 모두 지원하는 심플한 스튜디오 톤"
    },
    "프로필브랜딩_professional.png": {
        "name": "profile_branding__professional",
        "mood": ["professional", "clean", "structured", "minimal", "modern"],
        "category": ["profile_branding", "workspace_background", "business_style"],
        "suitable_objects": ["person", "laptop", "logo", "text_overlay", "documents", "stationery"],
        "safe_zones": [
            (180, 1200, 430, 1300, "profile_branding__professional__book")
        ],
        "description": "모던하고 정돈된 업무용 책상 구성 — 전문적이고 깔끔한 인상을 주는 프로필·브랜딩용 배경"
    },
    "여행기록_scenic.png": {
        "name": "travel_log__scenic",
        "mood": ["scenic", "fresh", "open", "bright", "relaxing"],
        "category": ["travel_log", "outdoor_scenery", "beach_view"],
        "suitable_objects": ["person", "backpack", "hat", "camera", "drink_bottle", "travel_props"],
        "safe_zones": [
            (0, 1300, 350, 1600, "travel_log__scenic__deck_left"),
            (350, 1250, 700, 1600, "travel_log__scenic__deck_middle"),
            (700, 1150, 1300, 1600, "travel_log__scenic__deck_right"),
            (100, 650, 850, 900, "travel_log__scenic__beach"),
            (0, 1100, 670, 1230, "travel_log__scenic__sand")
        ],
        "description": "맑은 하늘과 에메랄드빛 바다가 펼쳐진 시원한 해변 풍경 — 여행 기록 및 감성적인 전망 컷에 적합한 배경"
    },
    # 태영
    "콘텐츠제작_bold.png": {
        "name": "content_creation__bold",
        "mood": ["bold", "modern", "techy", "dramatic"],
        "category": ["creator_setup", "gaming_room", "streamer_desk", "sns_upload"],
        "suitable_objects": ["headphones", "mouse", "notebook", "coffee_cup", "tablet", "small_figurine"],
        "safe_zones": [
            #(150, 600, 450, 900, "left_microphone_area"),
            #(500, 550, 900, 900, "right_monitor_area"),
            (270, 475, 800, 790, "content_creation__bold__monitor"),
            #0, 400, 1080, 650, "wall_gradient_background")
        ],
        "description": "레드-블루 투톤의 감각적인 크리에이터 데스크 셋업. 모니터와 키보드, 마이크 실루엣이 강조된 현대적인 작업 공간 분위기."
    },
    "콘텐츠제작_eyecatching.png": {
        "name": "content_creation__eyecatching",
        "mood": ["dramatic", "moody", "minimal", "studio"],
        "category": ["product_shoot", "portrait_studio", "dramatic_scene", "creative_content"],
        "suitable_objects": ["person", "chair", "box", "statue", "product_item", "lamp"],
        "safe_zones": [
            (200, 800, 850, 1250, "content_creation__eyecatching__spotlight")
        ],
        "description": "어두운 밀폐 공간 위로 스포트라이트만 떨어지는 미니멀 스튜디오. 제품, 인물, 오브젝트의 드라마틱한 연출에 적합한 무드."
    },
    "친구연애_warm.png": {
        "name": "friends_romance__warm",
        "mood": ["warm", "cozy", "sunlit", "minimal", "calm"],
        "category": ["cafe_aesthetic", "daily_life", "sns_upload", "morning_vibes", "content_creation"],
        "suitable_objects": ["cup", "dessert", "notebook", "book", "plant_small", "phone", "cutlery", "glasses"],
        "safe_zones": [
            (250, 950, 550, 1150, "friends_romance__warm__table"),
            (0, 1320, 430, 1600, "friends_romance__warm__chair")
        ],
        "description": "따뜻한 햇살이 창가로 들어오는 조용한 코지 카페. 우드 톤의 테이블과 의자가 편안한 분위기를 만드는 공간."
    },
    "친구연애_nostalgic.png": {
        "name": "friends_romance__nostalgic",
        "mood": ["warm", "nostalgic", "soft", "afternoon_light", "sentimental"],
        "category": ["journal", "memory_record", "sns_upload", "creative_flatlay", "stationery_setup"],
        "suitable_objects": ["pen", "paper", "notebook", "photos", "postcard", "flower_small", "coffee_cup", "sticker"],
        "safe_zones": [
            (330, 100, 580, 400, "friends_romance__nostalgic__picture1"),
            (100, 300, 350, 650, "friends_romance__nostalgic__picture2"),
            (630, 850, 900, 1250, "friends_romance__nostalgic__picture3"),
            (300, 1050, 500, 1400, "friends_romance__nostalgic__picture4")
        ],
        "description": "따뜻한 빛이 내려앉는 우드 테이블 위에 폴라로이드와 연필이 흩어진 감성적인 책상. 기록, 작업, 추억 연출에 적합한 분위기."
    },
    "친구연애_romantic.png": {
        "name": "friends_romance__romantic",
        "mood": ["romantic", "warm", "intimate", "evening", "cinematic"],
        "category": ["date_night", "fine_dining", "restaurant_scene", "couple_mood", "aesthetic_upload"],
        "suitable_objects": ["wine_bottle", "flower_small", "menu_card", "ring_box", "dessert", "cutlery", "plate"],
        "safe_zones": [
            (260, 730, 430, 1050, "friends_romance__romantic__wine_left"),
            (600, 730, 760, 1070, "friends_romance__romantic__wine_right")
        ],
        "description": "은은한 촛불 조명 아래 두 개의 와인잔이 놓인 로맨틱한 디너 테이블. 따뜻하고 친밀한 분위기의 저녁 식사 장면에 적합한 배경."
    },
    "학교업무_neutral.png": {
        "name": "school_work__neutral",
        "mood": ["warm", "focused", "calm", "academic", "morning_light"],
        "category": ["study_space", "library_corner", "note_writing", "daily_routine", "sns_upload"],
        "suitable_objects": ["notebook", "pen", "coffee_cup", "laptop", "glasses", "stationery", "small_book_stack", "tablet"],
        "safe_zones": [
            (50, 900, 370, 1100, "shcool_work__neutral__book"),
            (650, 720, 730, 900, "shcool_work__neutral__bottle")
        ],
        "description": "잔잔한 햇살이 들어오는 도서관/서재 공부 공간. 나무 책상 위에 책과 노트, 텀블러가 놓인 차분하고 집중하기 좋은 분위기."
    },
    "학교업무_informative.png": {
        "name": "school_work__informative",
        "mood": ["clean", "minimal", "professional", "bright", "organized"],
        "category": ["meeting_room", "office_space", "study_room", "presentation_setup", "teamwork_space"],
        "suitable_objects": ["laptop", "notebook", "pen", "coffee_cup", "sticky_notes", "tablet", "nameplate", "documents"],
        "safe_zones": [
            (0, 1300, 1000, 1600, "shcool_work__informative__table"),
            (65, 350, 960, 970, "shcool_work__informative__whiteboard"),
            (460, 1100, 570, 1270, "shcool_work__informative__pen")
        ],
    },
    # 예영
    "여행기록_cinematic.png": {
        "name": "travel_log__cinematic",
        "mood": ["moody", "cinematic", "noir", "neon", "lonely"],
        "category": ["travel_log", "city_walk", "aesthetic_scene", "content_creation"],
        "suitable_objects": ["umbrella", "person", "neon_sign", "street_lights", "bag"],
        "safe_zones": [
            (50, 1100, 500, 1500, "travel_log__cinematic__ground"),
            (530, 520, 920, 1500, "travel_log__cinematic__person"),
            (160, 140, 260, 520, "travel_log__cinematic__neon")
        ],
        "description": "네온사인과 어두운 골목이 대비되는 밤거리, 영화 같은 어반 무드"
    },
    "라이프로그_fresh.png": {
        "name": "life_log__fresh",
        "mood": ["calm", "fresh", "minimal", "cozy", "natural"],
        "category": ["lifestyle", "study_setup", "workspace", "aesthetic_scene"],
        "suitable_objects": ["notebook", "pen", "glass", "plant", "laptop", "coffee_cup"],
        "safe_zones": [
            (200, 750, 400, 1070, "life_log__fresh__cup"),
            (450, 950, 850, 1300, "life_log__fresh__book"),
            (40, 350, 190, 850, "life_log__fresh__plant_left"),
            (700, 150, 1000, 850, "life_log__fresh__plant_right")
        ],
        "description": "따뜻한 햇빛 아래 미니멀한 책상과 식물들이 있는 차분한 데일리 무드"
    },
    "라이프로그_casual.png": {
        "name": "life_log__casual",
        "mood": ["cozy", "warm", "calm", "minimal", "comfort"],
        "category": ["cafe_moment", "lifestyle", "brunch", "sns_upload"],
        "suitable_objects": ["coffee", "latte", "sandwich", "notebook", "phone"],
        "safe_zones": [
            (130, 750, 500, 1100, "life_log__casual__latte"),
            (530, 600, 970, 950, "life_log__casual__sandwich"),
            (170, 360, 460, 650, "life_log__casual__coffee")
        ],
        "description": "따뜻한 카페 분위기에서 라떼·아메리카노·샌드위치가 놓인 아늑한 브런치 무드"
    },
    "라이프로그_cozydaily.png": {
        "name": "life_log__cozydaily",
        "mood": ["calm", "warm", "serene", "soft", "minimal"],
        "category": ["lifestyle", "home_aesthetic", "reading_moment", "sns_upload"],
        "suitable_objects": ["book", "flowers", "cup", "candle", "notebook"],
        "safe_zones": [
            (320, 1230, 670, 1370, "life_log__cozydaily__book"),
            (620, 900, 850, 1250, "life_log__cozydaily__flower")
        ],
        "description": "부드러운 햇살이 드는 창가, 책과 꽃이 놓인 따뜻하고 고요한 무드"
    },
    "패션메이크업_trendy.png": {
        "name": "fashion_makeup__trendy",
        "mood": ["fresh", "calm", "sunny", "minimal", "pastel"],
        "category": ["travel_log", "street_aesthetic", "daylight_scene", "sns_upload"],
        "suitable_objects": ["person", "bag", "bicycle", "coffee_cup"],
        "safe_zones": [
            (120, 750, 550, 1100, "fashion_makeup__trendy__bench")
        ],
        "description": "파스텔톤 건물이 늘어선 골목과 햇살 아래 벤치가 있는 산뜻한 데일리 스트리트 무드"
    },
    "패션메이크업_chic.png": {
        "name": "fashion_makeup__chic",
        "mood": ["luxury", "elegant", "chic", "warm", "premium"],
        "category": ["beauty_styling", "product_aesthetic", "vanity_setup", "sns_upload"],
        "suitable_objects": ["perfume", "lipstick", "mirror", "jewelry", "skincare"],
        "safe_zones": [
            (370, 1000, 800, 1250, "fashion_makeup__chic__tray"),
            (100, 350, 420, 750, "fashion_makeup__chic__mirror"),
            (560, 550, 900, 900, "fashion_makeup__chic__frame")
        ],
        "description": "골드 톤의 거울·향수·립스틱이 조화된 고급스러운 뷰티 스타일링 무드"
    },
    "패션메이크업_stylish.png": {
        "name": "fashion_makeup__stylish",
        "mood": ["trendy", "stylish", "soft", "minimal", "pastel"],
        "category": ["beauty_styling", "product_aesthetic", "fashion_editorial", "sns_upload"],
        "suitable_objects": ["lipstick", "eyeshadow", "compact", "mirror", "accessories"],
        "safe_zones": [
            #(120, 750, 550, 1100, "lip"),
            #(120, 750, 550, 1100, "lip"),
            #(550, 750, 900, 1100, "glass_table_right"),
            (0, 1000, 300, 1300, "fashion_makeup__stylish__table")
        ],
        "description": "파스텔 조명 아래 투명 의자와 유리 상판 위에 놓인 립스틱·아이팔레트가 강조된 트렌디한 뷰티 무드"
    }
}


# ✅ 새 표준: build_background_templates
def build_background_templates(base_dir: str = "./data/backgrounds") -> Dict[str, Dict]:
    """
    BACKGROUND_METADATA + 실제 이미지 파일 경로를 합쳐서
    BACKGROUND_TEMPLATES를 생성한다.

    결과 예시:
    {
      "sns_upload__cozy": {
        "path": "./data/backgrounds/sns업로드_cozy.png",
        "metadata": { ... }
      },
      ...
    }
    """
    templates: Dict[str, Dict] = {}

    for filename, meta in BACKGROUND_METADATA.items():
        key = meta.get("name") or os.path.splitext(filename)[0]
        templates[key] = {
            "path": os.path.join(base_dir, filename),
            "metadata": meta,
        }

    return templates


# ✅ 기존 코드와 호환용: load_background_templates
#    background_planner.py 에서 이 이름을 import 하고 있음
def load_background_templates(background_dir: str = "./data/backgrounds") -> Dict[str, Dict]:
    """
    이전 코드 호환용 래퍼.
    내부적으로 build_background_templates를 호출한다.
    """
    return build_background_templates(base_dir=background_dir)


# ✅ 실제 전역 템플릿 딕셔너리
BACKGROUND_TEMPLATES: Dict[str, Dict] = build_background_templates()