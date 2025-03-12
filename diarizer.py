from pyannote.audio.pipelines.speaker_diarization import SpeakerDiarization
from pyannote.core import Segment
import os
from dotenv import load_dotenv

# 🔹 .env 파일에서 Hugging Face Access Token 로드
load_dotenv()
HF_TOKEN = os.getenv("HUGGINGFACE_ACCESS_TOKEN")

# 🔥 Pyannote 모델 로드 시 인증 토큰 사용
pipeline = SpeakerDiarization.from_pretrained(
    "pyannote/speaker-diarization", 
    use_auth_token=HF_TOKEN
)

def diarize_audio(audio_path):
    """
    Pyannote를 사용하여 주어진 오디오 파일에서 화자를 구분하고 타임스탬프를 반환합니다.
    """
    print("🔍 화자 분리 실행 중...")
    diarization = pipeline(audio_path)

    speaker_segments = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        speaker_segments.append({
            "start": turn.start,
            "end": turn.end,
            "speaker": speaker
        })

    return speaker_segments

def find_best_matching_speaker(start_time, end_time, diarized_segments):
    """
    Whisper 텍스트의 타임스탬프(start_time, end_time)와 가장 적절한 Pyannote 화자를 매칭
    """
    best_speaker = "Unknown"
    min_diff = float("inf")  # 최소 시간 차이 초기화

    for segment in diarized_segments:
        # Whisper의 텍스트가 Pyannote 구간 내에 있을 경우, 해당 화자 선택
        if segment["start"] <= start_time <= segment["end"] or segment["start"] <= end_time <= segment["end"]:
            return segment["speaker"]

        # Whisper 타임스탬프와 가장 가까운 Pyannote 구간을 찾기
        start_diff = abs(segment["start"] - start_time)
        end_diff = abs(segment["end"] - end_time)
        avg_diff = (start_diff + end_diff) / 2  # 평균 거리 계산

        if avg_diff < min_diff:
            min_diff = avg_diff
            best_speaker = segment["speaker"]

    return best_speaker

def save_diarized_transcript(audio_path, transcript_path):
    """
    Whisper 변환된 텍스트와 Pyannote의 화자 구분 데이터를 결합하여 최종 스크립트 생성
    """
    diarized_segments = diarize_audio(audio_path)

    # 🔍 Whisper 변환된 텍스트 파일 로드
    if not os.path.exists(transcript_path):
        print(f"❌ 오류: 변환된 텍스트 파일이 존재하지 않음 ({transcript_path})")
        return

    with open(transcript_path, "r", encoding="utf-8") as f:
        transcript_lines = f.readlines()

    if not transcript_lines:
        print(f"❌ 오류: 변환된 텍스트 파일이 비어 있음 ({transcript_path})")
        return

    combined_results = []
    for line in transcript_lines:
        line = line.strip()
        if not line:
            continue

        parts = line.split(" ", 2)
        if len(parts) < 3:
            continue

        try:
            start_time, end_time, text = float(parts[0]), float(parts[1]), parts[2]
        except ValueError:
            print(f"⚠️ 경고: 잘못된 형식의 줄 발견 - {line}")
            continue

        # 🔍 가장 적절한 화자 찾기 (Pyannote 구간 내 또는 가장 가까운 화자 선택)
        speaker = find_best_matching_speaker(start_time, end_time, diarized_segments)

        combined_results.append({
            "start": start_time,
            "end": end_time,
            "speaker": speaker,
            "text": text
        })

    # ✅ 결과 저장
    diarized_output_path = transcript_path.replace(".txt", "_diarized.txt")
    with open(diarized_output_path, "w", encoding="utf-8") as f:
        for item in combined_results:
            f.write(f"[{item['start']:.2f} - {item['end']:.2f}] Speaker {item['speaker']}: {item['text']}\n")

    print(f"✅ 화자 구분 완료! 결과 저장: {diarized_output_path}")
    return diarized_output_path
