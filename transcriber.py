import whisper
import torch
import time
import openai
import os
from dotenv import load_dotenv
from pydub import AudioSegment
from diarizer import save_diarized_transcript

# GPU 사용 가능 여부 확인
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"🔍 현재 사용 중인 장치: {'GPU' if device == 'cuda' else 'CPU'}")

# Whisper 모델 로드
model = whisper.load_model("large-v3").to(device)

# .env 파일 로드 및 OpenAI API 키 설정
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=api_key)

def transcribe_audio_local(audio_file, output_text_file):
    print("🧠 Whisper 로컬 변환 시작...")
    start_time = time.time()
    result = model.transcribe(audio_file, language="ko")
    end_time = time.time()
    processing_time = round(end_time - start_time, 2)
    with open(output_path, "w", encoding="utf-8") as f:
        for segment in result["segments"]:
            f.write(f"{segment['start']} {segment['end']} {segment['text']}\n")
    print(f"📝 변환된 텍스트 저장 완료: {output_text_file}")
    print(f"⏳ Whisper 로컬 변환 완료. 실행 시간: {processing_time}초")
    print(f"🚀 Whisper 실행 장치: {'GPU' if device == 'cuda' else 'CPU'}")

    # 🔥 Pyannote로 화자 구분 적용
    diarized_transcript_path = save_diarized_transcript(audio_file, output_text_file)
    return diarized_transcript_path

def transcribe_audio_api(audio_file, output_text_file):
    print("☁️ OpenAI API 변환 시작...")
    
    # 지원되는 오디오 확장자 확인 및 변환
    file_extension = os.path.splitext(audio_file)[1].lower()
    if file_extension == ".wav":
        mp3_file = audio_file.replace(".wav", ".mp3")
    elif file_extension == ".m4a":
        mp3_file = audio_file.replace(".m4a", ".mp3")
    else:
        print(f"❌ 지원되지 않는 파일 형식: {file_extension}")
        return
    
    try:
        audio = AudioSegment.from_file(audio_file, format=file_extension[1:])  # 확장자에서 '.' 제거 후 사용
        audio.export(mp3_file, format="mp3", bitrate="64k")  # 64kbps로 압축하여 크기 줄이기
        print(f"🔄 {file_extension.upper()} → MP3 변환 완료: {mp3_file}")
    except Exception as e:
        print(f"❌ MP3 변환 오류: {e}")
        return
    
 # 🎤 OpenAI Whisper API 변환 실행
    try:
        with open(mp3_file, "rb") as audio:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio,
                language="ko",
                response_format="verbose_json"  # JSON 형태로 응답 받기
            )

        # ✅ API 응답이 리스트인지 확인하고 변환
        segments = response.segments if isinstance(response.segments, list) else list(response.segments)

        # 📝 변환된 텍스트 저장
        with open(output_text_file, "w", encoding="utf-8") as f:
            for segment in segments:
                f.write(f"{segment.start} {segment.end} {segment.text}\n")

        print(f"✅ OpenAI API 변환 완료: {output_text_file}")

    except Exception as e:
        print(f"❌ OpenAI API 변환 오류: {e}")
        return

    # 🗑️ MP3 파일 삭제 (임시 변환 파일이므로 삭제)
    os.remove(mp3_file)
    print(f"🗑️ 임시 MP3 파일 삭제 완료: {mp3_file}")

    # 🔥 Pyannote 화자 구분 실행
    diarized_transcript_path = save_diarized_transcript(audio_file, output_text_file)

    return diarized_transcript_path


    
