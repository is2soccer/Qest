# 녹음 관련 설정
FORMAT = 8  # pyaudio.paInt16
CHANNELS = 1  # 모노 채널
RATE = 44100  # 샘플링 레이트
CHUNK = 1024  # 버퍼 크기
RECORD_SECONDS = 10  # 녹음 시간 (초)

# Whisper 모델 설정
MODEL_SIZE = "large-v3"