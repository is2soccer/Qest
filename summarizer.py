import openai
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# OpenAI API 키 설정
api_key = os.getenv("OPENAI_API_KEY")

# OpenAI 클라이언트 초기화
client = openai.OpenAI(api_key=api_key)

def summarize_text(input_text):
    """ OpenAI GPT-4o 모델을 사용하여 상담 내용을 완벽히 요약하는 함수 """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": 
                    "주어진 상담 내용을 완벽하게 정리해줘. 상담 유형(인테리어, 법률, 금융, 의료 등)에 관계없이, "
                    "모든 세부 내용을 빠짐없이 포함해야 해.\n\n"
                    "📌 1. 상담 개요\n"
                    "- 상담의 핵심 내용을 3~5줄 이내로 요약\n"
                    "- 주요 비용, 일정, 계약 변경 사항 등을 포함할 것\n\n"
                    "📌 2. 상담 상세 내용\n"
                    "- 대화의 모든 내용을 번호(1,2,3,4,...)로 정리해야 함.\n"
                    "- 상담에서 논의된 모든 내용이 포함되어야 하며, 작은 세부사항도 빠뜨리지 말 것.\n"
                    "- 비용(금액), 일정(날짜), 계약 조건 등의 숫자는 절대 누락하지 말 것.\n\n"
                    "예시:\n"
                    "1. **방범 방충망 관련 논의**\n"
                    "   - 현관 방범 방충망 가격: 32만 원\n"
                    "   - 작은 방 방충망 가격: 40만 원\n"
                    "   - 거실 방범 방충망 가격: 55만 원 (총 143만 원 VAT 포함)\n"
                    "2. **허니콤 블라인드 설치 요청**\n"
                    "   - 거실 확장부 창: 40만 원, 추가 공간 설치 여부 논의 중\n"
                    "3. **공사 일정 조율**\n"
                    "   - 기존 공사 시작일: 10월 31일 → 변경 요청: 10월 28일\n"
                    "   - 고객 이사일: 10월 29일, 공사와의 조율 필요\n"
                    "...\n"
                    "(위와 같은 방식으로 **모든 상담 내용을 빠짐없이 요약**할 것)"},
                {"role": "user", "content": input_text}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ 요약 오류: {e}")
        return "요약 실패"
