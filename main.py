# main.py

from utils.env import setup_env
from pipeline.analyze_images import run_analysis
from pipeline.background_planner import run_background_selection
from pipeline.compose_collage import run_collage

if __name__ == "__main__":
    PATHS, DEVICE = setup_env()

    # 1) 분석
    result, result_path = run_analysis(PATHS)

    # 2) 배경 선택 + 좌표 변환
    composition, comp_path = run_background_selection(result_path, PATHS)

    # 3) Diffusion 합성
    final = run_collage(comp_path, PATHS)

    print("🎉 파이프라인 완료:", final)