from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse 
import shutil
import os
from torch import float32  # 파일 상단에 추가 (이미 torch import 되어 있으면 생략 가능)
from typing import List

import torch  # ★ 이 줄 추가
# -------------------------------------------------------
# 👇 진짜 파이프라인 모듈들
# -------------------------------------------------------
from utils.env import setup_env
from pipeline.analyze_images import run_analysis
from pipeline.background_planner import run_background_selection
from pipeline.compose_collage import run_collage

from pyngrok import ngrok
import uvicorn

app = FastAPI()

# 1. 모델 로딩 (서버 켤 때 한 번만 함 - 오래 걸림)
print("⏳ 서버 시작 중... 모델과 환경을 로드합니다 (시간이 좀 걸려요)")
# setup_env()가 경로와 디바이스(cuda/cpu)를 리턴한다고 가정
PATHS, CONFIG, DEVICE = setup_env()
print(f"✅ 모델 로드 완료! (Device: {DEVICE})")

@app.post("/generate")
async def generate_diary(files: list[UploadFile] = File(...)):
    try:
        print(f"📥 [요청 도착] 총 {len(files)}개 파일")

        upload_paths = []

        # 여러 파일 저장
        for file in files:
            upload_path = os.path.join(PATHS["uploads"], file.filename)
            with open(upload_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            upload_paths.append(upload_path)

        print(f"💾 {len(upload_paths)}개 파일 저장 완료")

        # ---------------- [진짜 AI 실행] ----------------
        print("🚀 [1단계] 이미지 분석 시작...")
        result, result_path = run_analysis(PATHS) 

        print("🚀 [2단계] 배경 선택 및 좌표 변환...")
        composition, comp_path = run_background_selection(result_path, PATHS)

        print("🚀 [3단계] 최종 합성 (Diffusion)...")
        final_image_path = run_collage(
            composition_plan_path=comp_path,
            paths=PATHS,
            device="cpu",                # ★ GPU 대신 CPU로 강제
            torch_dtype=torch.float32,   # ★ CPU에서는 float16 쓰면 안 됨
        )

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

if __name__ == "__main__":
    # FastAPI 서버 포트
    port = 8000

    # ngrok 터널 자동 생성
    public_url = ngrok.connect(port, "http")
    print("🔗 Public URL:", public_url)

    # 서버 실행
    uvicorn.run(app, host="0.0.0.0", port=port)