MOOD_CATEGORIES = {
    "sns_upload": ["cozy", "aesthetic", "film-like"],
    "profile_branding": ["clean", "minimal", "professional"],
    "travel_log": ["scenic", "cinematic", "fresh"],
    "life_log": ["casual", "cozy-daily"],
    "fashion_makeup": ["trendy", "chic", "stylish"],
    "content_creation": ["bold", "eye-catching"],
    "friends_romance": ["warm", "nostalgic", "romantic"],
    "school_work": ["neutral", "informative"]
}

# ② CLIP용 세부 카테고리 (기존과 동일하게 유지)
BACKGROUND_LABELS = [
    "café", "library", "classroom", "office", "home", "park", "beach", "restaurant", "street"
]

ACTIVITY_LABELS = [
    "studying", "eating", "traveling", "relaxing", "chatting",
    "working on a laptop", "taking a photo", "reading"
]

# ① STYLE_LABELS 업데이트 (CLIP 분석용)
STYLE_LABELS = [
    # SNS 업로드
    "cozy", "aesthetic", "film-like", "warm", "intimate", "minimal", "soft_light",
    "calm", "clean", "moody", "evening_glow", "quiet",

    # 프로필/브랜딩
    "professional", "structured", "modern", "bright", "fresh", "simple", "neutral",

    # 여행 기록
    "scenic", "cinematic", "open", "relaxing", "noir", "neon", "lonely",

    # 라이프로그
    "casual", "cozy-daily", "serene", "natural", "comfort",

    # 패션/메이크업
    "trendy", "chic", "stylish", "luxury", "elegant", "premium", "pastel",

    # 콘텐츠 제작
    "bold", "eye-catching", "techy", "dramatic", "studio"
]