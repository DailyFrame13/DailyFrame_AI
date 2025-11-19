import os
from utils.env import setup_env
from pipeline.analyze_images import run_analysis
from pipeline.background_planner import run_background_selection
from pipeline.compose_collage import run_collage


def run_everything():
    """
    DailyFrame 전체 파이프라인 자동 실행:
      1) YOLO + CLIP 분석 → result.json
      2) LLM 배경 선택 + zone 매핑 → composition_plan.json
      3) Diffusion 합성 → 최종 콜라주 이미지

    개발 중 전체 플로우를 빠르게 테스트할 때 사용한다.
    """
    print("\n============================")
    print("🚀 Step 0: 환경 세팅")
    print("============================")

    PATHS, DEVICE = setup_env()
    print(f"📁 PATHS = {PATHS}")
    print(f"💻 DEVICE = {DEVICE}")

    print("\n============================")
    print("🔍 Step 1: YOLO + CLIP 분석 실행 중…")
    print("============================")

    result, result_path = run_analysis(PATHS)
    print(f"✅ 분석 완료 → {result_path}")

    print("\n============================")
    print("🎨 Step 2: LLM 기반 배경 선택 실행 중…")
    print("============================")

    composition, comp_path = run_background_selection(result_path, PATHS)
    print(f"🎯 배경 선택 완료 → {comp_path}")

    print("\n============================")
    print("🖼️ Step 3: Collage Diffusion 합성 실행 중…")
    print("============================")

    final_image_path = run_collage(comp_path, PATHS)
    print(f"🌟 최종 이미지 생성 완료 → {final_image_path}")

    print("\n============================")
    print("🎉 DailyFrame 전체 파이프라인 완료!")
    print("============================\n")

    return {
        "result_json": result_path,
        "composition_plan": comp_path,
        "final_image": final_image_path,
    }


if __name__ == "__main__":
    run_everything()
