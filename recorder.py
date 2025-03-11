import pyaudio
import wave
import time
import threading
from config import RECORD_SECONDS, RATE, CHUNK, CHANNELS, FORMAT

recording = False  # 녹음 상태 변수

def get_device_index():
    """ 기본 입력 가능한 마이크 장치 찾기 """
    audio = pyaudio.PyAudio()
    for i in range(audio.get_device_count()):
        dev = audio.get_device_info_by_index(i)
        if dev['maxInputChannels'] > 0:
            return i  # 첫 번째 사용 가능한 마이크 선택
    return None

def start_recording(output_file):
    """ 녹음 시작 함수 """
    global recording
    recording = True  # 녹음 시작 상태 설정

    audio = pyaudio.PyAudio()
    device_index = get_device_index()
    print(f"🎤 선택된 마이크 장치: {device_index}")

    if device_index is None:
        print("❌ 사용 가능한 마이크가 없습니다.")
        return

    try:
        stream = audio.open(format=FORMAT, channels=CHANNELS,
                            rate=RATE, input=True, input_device_index=device_index,
                            frames_per_buffer=CHUNK)
    except Exception as e:
        print(f"❌ 마이크 오류 발생: {e}")
        return

    print("🎤 녹음 시작...")
    frames = []
    start_time = time.time()

    while recording:
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)

        elapsed_time = round(time.time() - start_time, 2)
        print(f"⏳ 녹음 중... {elapsed_time}s", end="\r", flush=True)

    end_time = time.time()
    recorded_seconds = round(end_time - start_time, 2)

    print(f"\n🛑 녹음 완료. 실제 녹음 시간: {recorded_seconds}초")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    # WAV 파일 저장
    with wave.open(output_file, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    print(f"📁 파일 저장 완료: {output_file}")

def stop_recording():
    """ 녹음 중지 함수 """
    global recording
    recording = False