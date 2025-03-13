import whisper
import torch
import time
import openai
import os
from dotenv import load_dotenv
from pydub import AudioSegment

# GPU 사용 가능 여부 확인
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"🔍 현재 사용 중인 장치: {'GPU' if device == 'cuda' else 'CPU'}")

# Whisper 모델 로드
model = whisper.load_model("large-v3").to(device)

# .env 파일 로드 및 OpenAI API 키 설정
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=api_key)

def get_file_size(file_path):
    """파일 크기 (MB 단위) 반환"""
    return os.path.getsize(file_path) / (1024 * 1024)

def split_audio_by_size(mp3_file, max_size_mb=20):
    """MP3 파일을 주어진 용량 이하로 분할"""
    audio = AudioSegment.from_mp3(mp3_file)
    total_size = get_file_size(mp3_file)

    # 분할 개수 계산 (20MB 단위)
    num_parts = int(total_size / max_size_mb) + 1
    segment_length = len(audio) // num_parts  # 각 파일 길이 (ms)

    parts = []
    for i in range(num_parts):
        start_time = i * segment_length
        end_time = min((i + 1) * segment_length, len(audio))
        part_file = f"{mp3_file[:-4]}_part{i}.mp3"
        
        # 오디오 슬라이싱 후 저장
        audio[start_time:end_time].export(part_file, format="mp3", bitrate="64k")
        parts.append(part_file)

    return parts

def transcribe_audio_local(audio_file, output_text_file):
    print("🧠 Whisper 로컬 변환 시작...")
    start_time = time.time()
    result = model.transcribe(audio_file, language="ko")
    end_time = time.time()
    processing_time = round(end_time - start_time, 2)
    with open(output_text_file, "w", encoding="utf-8") as f:
        for segment in result["segments"]:
            f.write(f"{segment['start']} {segment['end']} {segment['text']}\n")
    print(f"📝 변환된 텍스트 저장 완료: {output_text_file}")
    print(f"⏳ Whisper 로컬 변환 완료. 실행 시간: {processing_time}초")
    print(f"🚀 Whisper 실행 장치: {'GPU' if device == 'cuda' else 'CPU'}")
    return output_text_file

def transcribe_audio_api(audio_file, output_text_file):
    print("☁️ OpenAI API 변환 시작...")
    
    # 지원되는 오디오 확장자 확인 및 변환
    file_extension = os.path.splitext(audio_file)[1].lower()
    
    try:
        # OpenAI API를 위한 MP3 변환
        mp3_file = audio_file.replace(file_extension, ".mp3")
        audio = AudioSegment.from_file(audio_file, format=file_extension[1:])
        audio.export(mp3_file, format="mp3", bitrate="64k")
        print(f"🔄 {file_extension.upper()} → MP3 변환 완료: {mp3_file}")

    except Exception as e:
        print(f"❌ 오디오 변환 오류: {e}")
        return

    # MP3 파일 크기 확인
    file_size = get_file_size(mp3_file)
    print(f"📏 MP3 파일 크기: {file_size:.2f}MB")

    # 25MB 초과 시 분할
    if file_size > 25:
        print(f"⚠️ 파일 크기가 25MB 초과! 분할 진행 중...")
        parts = split_audio_by_size(mp3_file, max_size_mb=20)
    else:
        parts = [mp3_file]
    
    # 🎤 OpenAI Whisper API 변환 실행
    all_text = []
    try:
        for part in parts:
            with open(part, "rb") as audio:
                response = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio,
                    language="ko",
                    response_format="verbose_json"
                )

            # ✅ API 응답 파싱
            segments = response.segments if isinstance(response.segments, list) else list(response.segments)
            for segment in segments:
                all_text.append(f"{segment.start} {segment.end} {segment.text}")

            print(f"✅ OpenAI API 변환 완료: {part}")

            # 🗑️ MP3 분할 파일 삭제
            os.remove(part)
            print(f"🗑️ 분할 파일 삭제 완료: {part}")

    except Exception as e:
        print(f"❌ OpenAI API 변환 오류: {e}")
        return

    # 📝 변환된 텍스트 저장
    with open(output_text_file, "w", encoding="utf-8") as f:
        f.write("\n".join(all_text))

    print(f"✅ 최종 변환 완료: {output_text_file}")

    # 🗑️ MP3 파일 삭제 (임시 변환 파일이므로 삭제)
    os.remove(mp3_file)
    print(f"🗑️ 임시 MP3 파일 삭제 완료: {mp3_file}")

    return output_text_file