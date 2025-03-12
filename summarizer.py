import openai
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# OpenAI API 키 설정
api_key = os.getenv("OPENAI_API_KEY")

# OpenAI 클라이언트 초기화 (최신 방식)
client = openai.OpenAI(api_key=api_key)

def summarize_text(input_text):
    """ OpenAI GPT-4o 모델을 사용하여 General한 인테리어 상담 보고서 형식으로 요약 """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": 
                    "주어진 인테리어 상담 내용을 다음 형식으로 정리해줘. "
                    "이 포맷은 초기 견적 상담과 계약 후 상담 모두를 포함할 수 있도록 설계되었어.\n\n"
                    "📌 1. 기본 정보\n"
                    "- 고객 이름: (고객 이름)\n"
                    "- 연락처: (연락처)\n"
                    "- 상담 일자: (상담 날짜)\n"
                    "- 상담 유형: (초기 견적 상담 / 계약 후 상세 협의 / 추가 요청 / 문제 해결 등)\n"
                    "- 상담 장소: (오프라인 미팅 / 전화 상담 / 온라인 회의 등)\n\n"
                    "📌 2. 상담 개요\n"
                    "- 주요 논의 사항: (핵심 내용 요약)\n"
                    "- 고객의 주요 관심사: (예산, 디자인 스타일, 기능 등)\n"
                    "- 현재 진행 상태: (계약 전 / 계약 후 / 공사 진행 중 / 추가 요청 등)\n"
                    "- 기한 및 일정 조율: (완공 희망 시기, 중간 점검 일정 등)\n\n"
                    "📌 3. 상세 요청 내용\n"
                    "✅ 거실\n"
                    "- (거실 관련 요청 정리)\n"
                    "✅ 주방\n"
                    "- (주방 관련 요청 정리)\n"
                    "✅ 기타 공간 (욕실, 침실 등)\n"
                    "- (기타 공간 관련 요청 정리)\n\n"
                    "📌 4. 추가 요청 / 변경 사항\n"
                    "- (고객이 추가 요청한 사항)\n"
                    "- (기존 계약 대비 변경된 내용)\n"
                    "- (특이 사항 - 예산 변경, 일정 조정 등)\n\n"
                    "📌 5. 해결해야 할 문제 & 다음 단계\n"
                    "- 해결이 필요한 이슈 (예: 자재 변경, 디자인 조율, 예산 초과 등)\n"
                    "- 다음 단계 진행 계획\n"
                    "- 고객 피드백 반영 사항\n"},
                {"role": "user", "content": input_text}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ 요약 오류: {e}")
        return "요약 실패"
