import os
import torch
from dotenv import load_dotenv

def setup_env(base_dir: str | None = None):
    """
    전체 프로젝트의 공통 환경을 초기화한다.
    - .env 로딩
    - 데이터 폴더 생성
    - 모델 설정(CONFIG) 구성
    - GPU/CPU 디바이스 결정
    """

    # -------------------------------------------
    # 1) .env 불러오기
    # -------------------------------------------
    load_dotenv()

    # base_dir 우선순위:
    # 1) 인자로 받은 base_dir
    # 2) .env의 BASE_DIR
    # 3) 현재 파일 기준 상위 디렉토리
    if base_dir is not None:
        BASE_DIR = base_dir
    else:
        BASE_DIR = os.getenv(
            "BASE_DIR",
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        )

    print(f"📂 BASE_DIR = {BASE_DIR}")

    # -------------------------------------------
    # 2) 경로 PATHS 설정 (.env + 기본값)
    # -------------------------------------------
    def _join_base(env_key: str, default_rel: str) -> str:
        """
        .env에 상대경로가 적혀 있어도 BASE_DIR 기준으로 붙여주기.
        """
        rel_path = os.getenv(env_key, default_rel)
        # 이미 절대경로면 그대로 사용
        if os.path.isabs(rel_path):
            return rel_path
        return os.path.join(BASE_DIR, rel_path)

    paths = {
        "base": BASE_DIR,
        "uploads": _join_base("UPLOAD_DIR", "data/uploads"),
        "cutouts": _join_base("CUTOUT_DIR", "data/cutouts"),
        "outputs": _join_base("OUTPUT_DIR", "data/outputs"),
        "backgrounds": _join_base("BACKGROUND_DIR", "data/backgrounds"),
        "debug": _join_base("DEBUG_DIR", "data/debug"),
        # 모델 캐시 폴더 (옵션)
        "model_cache": os.path.join(BASE_DIR, "models_cache"),
    }

    # 디렉토리 생성
    for key, p in paths.items():
        if key == "base":
            # base는 이미 존재하는 프로젝트 루트라고 가정
            continue
        if isinstance(p, str):
            os.makedirs(p, exist_ok=True)

    # -------------------------------------------
    # 3) 디바이스 설정
    # -------------------------------------------
    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"⚡ Device set to: {device}")
    except Exception as e:
        print("⚠️ CUDA 체크 중 오류 발생 → CPU fallback")
        print(e)
        device = "cpu"

    print(f"📦 Torch version: {torch.__version__}")

    # -------------------------------------------
    # 4) 모델/토큰 CONFIG 설정
    # -------------------------------------------
    config = {
        # 토큰
        "HF_TOKEN": os.getenv("HF_TOKEN"),

        # 모델 경로 / 이름
        "YOLO_MODEL_PATH": os.getenv("YOLO_MODEL_PATH", "yolov8s-seg.pt"),
        "CLIP_MODEL_NAME": os.getenv("CLIP_MODEL_NAME", "ViT-B/32"),
        "DIFFUSION_MODEL": os.getenv(
            "DIFFUSION_MODEL",
            "stabilityai/stable-diffusion-2-inpainting",
        ),
        "LLM_MODEL": os.getenv(
            "LLM_MODEL",
            "llava-hf/llava-v1.6-vicuna-7b-hf",  # 기본값은 LLaVA로
        ),
    }

    if config["HF_TOKEN"]:
        print("🔑 HuggingFace Token loaded")
    else:
        print("⚠️ HF_TOKEN이 .env에 없습니다 (LLM / Diffusers 사용 시 오류 가능)")

    if os.getenv("OPENAI_API_KEY"):
        print("🔑 OPENAI_API_KEY loaded")
    if os.getenv("ANTHROPIC_API_KEY"):
        print("🔑 ANTHROPIC_API_KEY loaded")

    # -------------------------------------------
    # 5) 최종 반환
    # -------------------------------------------
    return paths, config, device
