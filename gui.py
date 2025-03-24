import tkinter as tk
import threading
import datetime
import os
import time
import numpy as np
import pyaudio
from recorder import start_recording, stop_recording, get_device_index
from transcriber import transcribe_audio_local, transcribe_audio_api
from summarizer import summarize_text
from config import FORMAT, CHANNELS, RATE, CHUNK
from generate_pdf import generate_pdf

recording = False  # 녹음 상태 변수
latest_audio_path = ""  # 마지막으로 저장된 녹음 파일 경로
start_time = None  # 녹음 시작 시간
mic_volume = 0  # 마이크 볼륨 (1~100)
transcribe_method = "local"  # 변환 방식 (local 또는 api)

# 필요한 폴더 생성
os.makedirs("recordings", exist_ok=True)
os.makedirs("transcriptions", exist_ok=True)
os.makedirs("summaries", exist_ok=True)
os.makedirs("pdfs", exist_ok=True)

def check_microphone():
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
        
        # 🔄 파일이 저장될 때까지 대기 후 변환 실행
        transcribe_thread = threading.Thread(target=wait_for_file_and_transcribe, args=(latest_audio_path,))
        transcribe_thread.daemon = True
        transcribe_thread.start()

def wait_for_file_and_transcribe(audio_path):
    text_path = audio_path.replace("recordings/", "transcriptions/").replace(".wav", ".txt")
    
    # 🔄 파일이 저장될 때까지 최대 3초 대기
    timeout = 3
    elapsed = 0
    while not os.path.exists(audio_path) and elapsed < timeout:
        print(f"⏳ 파일 저장 대기 중... ({elapsed+1}/{timeout}초)")
        time.sleep(1)
        elapsed += 1
    
    if not os.path.exists(audio_path):
        print(f"❌ 오류: 파일이 존재하지 않음 {audio_path}")
        root.after(0, lambda: result_label.config(text="❌ 오류: 파일이 존재하지 않음"))
        return
    
    # 🔥 Whisper 변환 실행
    if transcribe_method == "local":
        transcribed_text_path = transcribe_audio_local(audio_path, text_path)
    else:
        transcribed_text_path = transcribe_audio_api(audio_path, text_path)

    if transcribed_text_path:
        root.after(0, lambda: result_label.config(text=f"✅ 변환 완료: {transcribed_text_path}"))
        root.after(0, lambda: summary_button.config(state=tk.NORMAL))

def transcribe_test_audio():
    test_audio_path = "recordings/test.wav"
    text_path = test_audio_path.replace("recordings/", "transcriptions/").replace(".wav", ".txt")
    if not os.path.exists(test_audio_path):
        result_label.config(text="❌ test.m4a 파일이 존재하지 않습니다.")
        return
    if transcribe_method == "local":
        transcribed_text_path = transcribe_audio_local(test_audio_path, text_path)
    else:
        transcribed_text_path = transcribe_audio_api(test_audio_path, text_path)

    root.after(0, lambda: result_label.config(text=f"✅ 변환 완료: {transcribed_text_path}"))

def summarize_text_file():
    global latest_audio_path
    text_path = latest_audio_path.replace("recordings/", "transcriptions/").replace(".wav", ".txt")
    summary_path = latest_audio_path.replace("recordings/", "summaries/").replace(".wav", ".txt")
    with open(text_path, "r", encoding="utf-8") as f:
        transcribed_text = f.read()
    summary_text = summarize_text(transcribed_text)
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(summary_text)
    root.after(0, lambda: result_label.config(text=f"✅ 요약 완료: {summary_path}"))
    root.after(0, lambda: pdf_button.config(state=tk.NORMAL))  # 📄 PDF 버튼 활성화

def summarize_test_file():
    test_text_path = "transcriptions/test.txt"
    summary_path = "summaries/test_summary.txt"

    if not os.path.exists(test_text_path):
        result_label.config(text="❌ test.txt 파일이 존재하지 않습니다.")
        return
    
    with open(test_text_path, "r", encoding="utf-8") as f:
        input_text = f.read()

    summary_text = summarize_text(input_text)

    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(summary_text)

    result_label.config(text=f"✅ 요약 완료: {summary_path}")

def set_transcribe_method(method):
    global transcribe_method
    transcribe_method = method

def generate_pdf_from_summary():
    """ 일반 녹음 파일의 요약본을 PDF로 변환하는 함수 """
    global latest_audio_path
    text_path = latest_audio_path.replace("recordings/", "summaries/").replace(".wav", ".txt")
    pdf_path = latest_audio_path.replace("recordings/", "pdfs/").replace(".wav", ".pdf")

    result_label.config(text="📄 PDF 생성 중...")
    generate_pdf(text_path, pdf_path)
    result_label.config(text=f"✅ PDF 저장 완료: {pdf_path}")

def generate_pdf_from_test_summary():
    """ test 파일의 요약본을 PDF로 변환하는 함수 """
    test_text_path = "summaries/test_summary.txt"
    test_pdf_path = "pdfs/test_summary.pdf"

    if not os.path.exists(test_text_path):
        result_label.config(text="❌ test_summary.txt 파일이 존재하지 않습니다.")
        return

    result_label.config(text="📄 PDF 생성 중 (test)...")
    generate_pdf(test_text_path, test_pdf_path)
    result_label.config(text=f"✅ PDF 저장 완료: {test_pdf_path}")

# GUI 설정
root = tk.Tk()
root.title("음성 녹음 & 변환 & AI 요약")
root.geometry("500x800")  # 높이를 살짝 늘려줌

mic_volume_label = tk.Label(root, text="🎚️ 마이크 볼륨: 측정 중...", font=("Arial", 12))
mic_volume_label.pack(pady=5)

# 🎤 녹음 버튼
record_button = tk.Button(root, text="녹음", font=("Arial", 14), bg="green", command=toggle_recording)
record_button.pack(pady=10)

# ⏳ 타이머 라벨
timer_label = tk.Label(root, text="⏳ 대기 중...", font=("Arial", 12))
timer_label.pack(pady=5)

# 🔵 요약 버튼
summary_button = tk.Button(root, text="요약", font=("Arial", 14), bg="blue", command=summarize_text_file, state=tk.DISABLED)
summary_button.pack(pady=10)

# 📄 PDF 저장 버튼 (일반 파일)
pdf_button = tk.Button(root, text="📄 PDF 저장", font=("Arial", 14), bg="gray", command=generate_pdf_from_summary, state=tk.DISABLED)
pdf_button.pack(pady=10)

# 🟠 Test 파일 변환 버튼
test_transcribe_button = tk.Button(root, text="Test 파일 변환", font=("Arial", 14), bg="orange", command=transcribe_test_audio)
test_transcribe_button.pack(pady=10)

# 🟣 Test 파일 요약 버튼
test_summarize_button = tk.Button(root, text="Test 파일 요약", font=("Arial", 14), bg="purple", command=summarize_test_file)
test_summarize_button.pack(pady=10)

# 📄 PDF 저장 버튼 (test 파일)
test_pdf_button = tk.Button(root, text="📄 PDF 저장 (test)", font=("Arial", 14), bg="gray", command=generate_pdf_from_test_summary, state=tk.NORMAL)
test_pdf_button.pack(pady=10)

# 결과 라벨
result_label = tk.Label(root, text="", font=("Arial", 12))
result_label.pack(pady=10)

# 🎚️ 변환 방식 선택 (로컬/ API)
transcribe_method_var = tk.StringVar(value="local")
tk.Radiobutton(root, text="로컬 변환", variable=transcribe_method_var, value="local", command=lambda: set_transcribe_method("local")).pack()
tk.Radiobutton(root, text="API 변환", variable=transcribe_method_var, value="api", command=lambda: set_transcribe_method("api")).pack()

# 마이크 볼륨 체크
root.after(1000, check_microphone)
root.mainloop()