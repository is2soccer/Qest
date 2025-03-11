import whisper
import torch
import time

# GPU 사용 가능 여부 확인
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"🔍 현재 사용 중인 장치: {'GPU' if device == 'cuda' else 'CPU'}")

# Whisper 모델 로드
model = whisper.load_model("large-v3").to(device)

def transcribe_audio(audio_file, output_text_file):
    print("🧠 Whisper 변환 시작...")
    
    start_time = time.time()  # 변환 시작 시간 기록
    result = model.transcribe(audio_file, language="ko")  # 🔹 한국어 강제 설정
    end_time = time.time()  # 변환 완료 시간 기록
    processing_time = round(end_time - start_time, 2)

    # 변환된 텍스트 저장
    with open(output_text_file, "w", encoding="utf-8") as f:
        f.write(result["text"])

    print(f"📝 변환된 텍스트 저장 완료: {output_text_file}")
    print(f"⏳ Whisper 변환 완료. 실행 시간: {processing_time}초")
    print(f"🚀 Whisper 실행 장치: {'GPU' if device == 'cuda' else 'CPU'}")