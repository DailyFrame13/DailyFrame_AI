from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# 기존 코드의 모듈들 가져오기
from utils.env import setup_env
from pipeline.analyze_images import run_analysis
from pipeline.background_planner import run_background_selection
from pipeline.compose_collage import run_collage

# 1. FastAPI 앱 생성
app = FastAPI()

# 2. 환경 설정 및 모델 로드 (서버 켜질 때 딱 한 번만 실행)
# 전역 변수로 설정해두어 매 요청마다 모델을 다시 로드하지 않게 합니다.
print("⏳ 서버 시작 중... 모델을 로드합니다.")
PATHS, DEVICE = setup_env()
print("✅ 모델 로드 완료! 서버가 준비되었습니다.")

# 3. 요청 데이터 정의 (필요하다면)
class GenerateRequest(BaseModel):
    # 만약 사용자가 특정 ID나 옵션을 보내야 한다면 여기에 추가
    user_id: str = "default_user" 

@app.get("/")
def health_check():
    return {"status": "DailyFrame AI Server is Running"}

@app.post("/generate")
def generate_diary(req: GenerateRequest):
    try:
        print("🚀 파이프라인 시작...")
        
        # 1) 분석
        print(f"[{req.user_id}] 1단계: 이미지 분석 중...")
        result, result_path = run_analysis(PATHS)

        # 2) 배경 선택 + 좌표 변환
        print(f"[{req.user_id}] 2단계: 배경 선택 및 좌표 변환 중...")
        composition, comp_path = run_background_selection(result_path, PATHS)

        # 3) Diffusion 합성
        print(f"[{req.user_id}] 3단계: 최종 합성 중...")
        final_image_path = run_collage(comp_path, PATHS)

        print("🎉 파이프라인 완료:", final_image_path)
        
        # 결과 반환 (이미지 경로 또는 URL)
        return {
            "status": "success",
            "message": "일기 생성이 완료되었습니다.",
            "result_path": final_image_path
        }

    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 실행 명령: uvicorn main:app --host 0.0.0.0 --port 8000