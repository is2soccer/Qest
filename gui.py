import tkinter as tk
import threading
import datetime
import os
import time
import numpy as np
import pyaudio
from recorder import start_recording, stop_recording, get_device_index
from transcriber import transcribe_audio
from summarizer import summarize_text
from config import FORMAT, CHANNELS, RATE, CHUNK

recording = False  # 녹음 상태 변수
latest_audio_path = ""  # 마지막으로 저장된 녹음 파일 경로
start_time = None  # 녹음 시작 시간
mic_volume = 0  # 마이크 볼륨 (1~100)

# 필요한 폴더 생성
os.makedirs("recordings", exist_ok=True)
os.makedirs("transcriptions", exist_ok=True)
os.makedirs("summaries", exist_ok=True)

def check_microphone():
    """ 🎤 마이크 입력 감지 및 볼륨 측정 (1~100) """
    global mic_volume
    audio = pyaudio.PyAudio()
    device_index = get_device_index()

    try:
        stream = audio.open(format=FORMAT, channels=CHANNELS,
                            rate=RATE, input=True, input_device_index=device_index,
                            frames_per_buffer=CHUNK)

        data = stream.read(CHUNK, exception_on_overflow=False)
        audio_np = np.frombuffer(data, dtype=np.int16)
        mic_volume = max(1, min(100, int((np.max(np.abs(audio_np)) / 32768) * 100 * 10)))
        mic_volume_label.config(text=f"🎚️ 마이크 볼륨: {mic_volume}/100")

        stream.stop_stream()
        stream.close()
    except Exception as e:
        mic_volume = 0
        mic_volume_label.config(text="❌ 마이크 오류")
        print(f"❌ 마이크 오류: {e}")

    audio.terminate()
    root.after(500, check_microphone)

def update_timer():
    """ ⏳ 녹음 중인 동안 시간 업데이트 """
    if recording:
        elapsed_time = round(time.time() - start_time, 1)
        timer_label.config(text=f"⏳ 녹음 중... {elapsed_time}s")
        root.after(100, update_timer)

def toggle_recording():
    global recording, latest_audio_path, start_time
    if not recording:
        print("🎤 녹음 시작 버튼 클릭됨")
        recording = True
        start_time = time.time()
        record_button.config(text="중지", bg="red")

        os.makedirs("recordings", exist_ok=True)
        os.makedirs("transcriptions", exist_ok=True)
        os.makedirs("summaries", exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        latest_audio_path = f"recordings/{timestamp}.wav"

        thread = threading.Thread(target=start_recording, args=(latest_audio_path,))
        thread.daemon = True
        thread.start()

        update_timer()
    else:
        print("🛑 녹음 중지 버튼 클릭됨")
        stop_recording()
        recording = False
        record_button.config(text="녹음", bg="green")
        timer_label.config(text="✅ 녹음 완료")

        transcribe_thread = threading.Thread(target=wait_for_file_and_transcribe, args=(latest_audio_path,))
        transcribe_thread.daemon = True
        transcribe_thread.start()

def wait_for_file_and_transcribe(audio_path):
    """ 🔄 파일 저장 완료 후 변환 실행 """
    text_path = audio_path.replace("recordings/", "transcriptions/").replace(".wav", ".txt")

    timeout = 1
    elapsed = 0
    while not os.path.exists(audio_path) and elapsed < timeout:
        print(f"⏳ 변환 대기 중... ({elapsed+1}/{timeout}초)")
        time.sleep(1)
        elapsed += 1

    if not os.path.exists(audio_path):
        print(f"❌ 오류: 파일이 존재하지 않음 {audio_path}")
        root.after(0, lambda: result_label.config(text="❌ 오류: 파일이 존재하지 않음"))
        return

    print(f"📝 변환 시작: {audio_path} → {text_path}")
    transcribe_audio(audio_path, text_path)
    root.after(0, lambda: summary_button.config(state=tk.NORMAL))

def summarize_text_file():
    """ 🔥 변환된 텍스트를 요약하는 버튼 기능 """
    global latest_audio_path
    if not latest_audio_path:
        result_label.config(text="❌ 변환된 파일 없음")
        return
    text_path = latest_audio_path.replace("recordings/", "transcriptions/").replace(".wav", ".txt")
    summary_path = latest_audio_path.replace("recordings/", "summaries/").replace(".wav", ".txt")

    if not os.path.exists(text_path):
        result_label.config(text="❌ 변환된 텍스트 파일 없음")
        return

    print(f"📄 요약 시작: {text_path} → {summary_path}")
    with open(text_path, "r", encoding="utf-8") as f:
        transcribed_text = f.read()
    summary_text = summarize_text(transcribed_text)
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(summary_text)

    print(f"✅ 요약 완료: {summary_path}")
    root.after(0, lambda: result_label.config(text=f"✅ 요약 완료: {summary_path}"))

# GUI 설정
root = tk.Tk()
root.title("음성 녹음 & Whisper 변환 & AI 요약")
root.geometry("400x350")

mic_volume_label = tk.Label(root, text="🎚️ 마이크 볼륨: 측정 중...", font=("Arial", 12))
mic_volume_label.pack(pady=5)

record_button = tk.Button(root, text="녹음", font=("Arial", 14), bg="green", command=toggle_recording)
record_button.pack(pady=10)

timer_label = tk.Label(root, text="⏳ 대기 중...", font=("Arial", 12))
timer_label.pack(pady=5)

summary_button = tk.Button(root, text="요약", font=("Arial", 14), bg="blue", command=summarize_text_file, state=tk.DISABLED)
summary_button.pack(pady=10)

result_label = tk.Label(root, text="", font=("Arial", 12))
result_label.pack(pady=10)

root.after(1000, check_microphone)
root.mainloop()
