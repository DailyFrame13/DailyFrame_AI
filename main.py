from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse 
import shutil
import os

# -------------------------------------------------------
# 👇 진짜 파이프라인 모듈들
# -------------------------------------------------------
from utils.env import setup_env
from pipeline.analyze_images import run_analysis
from pipeline.background_planner import run_background_selection
from pipeline.compose_collage import run_collage

app = FastAPI()

# 1. 모델 로딩 (서버 켤 때 한 번만 함 - 오래 걸림)
print("⏳ 서버 시작 중... 모델과 환경을 로드합니다 (시간이 좀 걸려요)")
# setup_env()가 경로와 디바이스(cuda/cpu)를 리턴한다고 가정
PATHS, DEVICE = setup_env() 
print(f"✅ 모델 로드 완료! (Device: {DEVICE})")

# 입력/출력 폴더 확인
os.makedirs("temp_input", exist_ok=True)

@app.post("/generate")
async def generate_diary(file: UploadFile = File(...)):
    try:
        print(f"📥 [요청 도착] 파일명: {file.filename}")

        # 1. 파일 저장 (파이프라인이 읽을 수 있게)
        input_image_path = os.path.join("temp_input", file.filename)
        
        with open(input_image_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print(f"💾 파일 저장 완료: {input_image_path}")

        # ---------------- [진짜 AI 실행] ----------------
        print("🚀 [1단계] 이미지 분석 시작...")
        result, result_path = run_analysis(PATHS) 

        print("🚀 [2단계] 배경 선택 및 좌표 변환...")
        composition, comp_path = run_background_selection(result_path, PATHS)

        print("🚀 [3단계] 최종 합성 (Diffusion)...")
        final_image_path = run_collage(comp_path, PATHS)

        print(f"🎉 모든 작업 완료! 결과 파일: {final_image_path}")
        # -----------------------------------------------------
        
        # 2. 결과 파일이 진짜 있는지 확인
        if not os.path.exists(final_image_path):
            raise Exception("AI가 결과 파일을 생성하지 못했습니다.")

        # 3. 이미지 파일 전송
        return FileResponse(final_image_path)

    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        raise HTTPException(status_code=500, detail=str(e))