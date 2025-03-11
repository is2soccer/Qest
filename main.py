from recorder import record_audio
from transcriber import transcribe_audio
import datetime

# 현재 날짜/시간으로 파일 이름 설정
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
audio_path = f"recordings/{timestamp}.wav"
text_path = f"transcriptions/{timestamp}.txt"

# 녹음 및 변환 실행
record_audio(audio_path)
transcribe_audio(audio_path, text_path)