# main.py (설치 없이 바로 돌아가는 테스트용 코드)
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
import shutil
import os
import time

app = FastAPI()

os.makedirs("temp_mock", exist_ok=True)

@app.post("/generate")
async def generate_mock(file: UploadFile = File(...)):
    print(f"🐍 [Python] 파일 받음: {file.filename}")
    
    # 받은 파일 저장
    input_path = f"temp_mock/{file.filename}"
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # AI 흉내내기
    print("🤖 AI 생성 중... (가짜 로딩)")
    time.sleep(3)

    # 받은 파일 그대로 돌려주기
    return FileResponse(input_path)