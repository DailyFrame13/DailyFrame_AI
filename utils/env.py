# utils/env.py

import os
import torch
from dotenv import load_dotenv

def setup_env():
    """
    전체 프로젝트의 공통 환경을 초기화한다.
    - .env 로딩
    - 데이터 폴더 생성
    - 모델 캐시 경로 설정
    - GPU/CPU 디바이스 결정
    """

    # -------------------------------------------
    # 1) .env 불러오기
    # -------------------------------------------
    load_dotenv()

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"📂 BASE_DIR = {BASE_DIR}")

    # -------------------------------------------
    # 2) 데이터 경로 설정
    # -------------------------------------------
    paths = {
        "base_dir": BASE_DIR,
        "uploads": os.path.join(BASE_DIR, "data", "uploads"),
        "cutouts": os.path.join(BASE_DIR, "data", "cutouts"),
        "outputs": os.path.join(BASE_DIR, "data", "outputs"),
        "backgrounds": os.path.join(BASE_DIR, "data", "backgrounds"),
        "debug": os.path.join(BASE_DIR, "data", "debug"),

        # 모델 캐시 폴더 (옵션)
        "model_cache": os.path.join(BASE_DIR, "models_cache"),
    }

    for p in paths.values():
        if isinstance(p, str):  # base_dir 같은 str만 mkdir
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
    # 4) HuggingFace Token 체크
    # -------------------------------------------
    hf_token = os.environ.get("HF_TOKEN")
    if hf_token:
        print("🔑 HuggingFace Token loaded")
    else:
        print("⚠️ HF_TOKEN이 .env에 없습니다 (LLM 사용 시 오류 가능)")

    # -------------------------------------------
    # 5) OpenAI/Anthropic Token 체크
    # -------------------------------------------
    if os.environ.get("OPENAI_API_KEY"):
        print("🔑 OPENAI_API_KEY loaded")
    if os.environ.get("ANTHROPIC_API_KEY"):
        print("🔑 ANTHROPIC_API_KEY loaded")

    return paths, device
