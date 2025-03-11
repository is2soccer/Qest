# Qest
Qest is an innovative app designed for interior designers and contractors, streamlining the consultation and estimation process. With Qest, you can effortlessly record client discussions, summarize key points, and generate professional estimates—all in one place.

✨ Key Features:
✅ Instant Consultation Summaries – AI-powered summaries of client discussions for quick reference.
✅ Automated Estimates – Generate accurate cost estimates based on project details.
✅ Seamless Data Management – Store, organize, and retrieve past consultations effortlessly.
✅ User-Friendly Interface – Simple and intuitive design for fast and efficient workflow.

No more paperwork or lost notes—Qest keeps everything organized so you can focus on what truly matters: creating beautiful spaces!

🚀 Try Qest today and transform the way you handle interior design projects!

## 🚀 실행 방법
1. `pip install -r requirements.txt` 실행하여 필요한 패키지 설치
2. `python main.py` 실행하면 자동으로 녹음 및 변환 진행
3. 변환된 텍스트는 `transcriptions/` 폴더에 저장됨

## 📂 폴더 구조
- `recordings/` → 녹음된 음성 파일 저장
- `transcriptions/` → 변환된 텍스트 저장
- `models/` → Whisper 모델 캐시
