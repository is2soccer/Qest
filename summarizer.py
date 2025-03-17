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
    """ OpenAI GPT-4o 모델을 사용하여 상담 내용을 체계적으로 정리하는 함수 """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": 
                    "당신은 **인테리어 디자인 전문가**입니다. "
                    "주어진 상담 내용을 **세부적으로 정리**하고, **누락 없이 모든 정보를 포함**해야 합니다. "
                    "이는 단순 요약이 아니라, **회의록 수준의 정리**이며, 모든 숫자, 금액, 일정, 고객 의견 등을 **빠짐없이** 기록해야 합니다.\n\n"

                    "💡 **정리 규칙**\n"
                    "**1. 인테리어 디자인 맥락에 맞게 단어를 자동 교정하세요.**\n"
                    "**2. 원본 대화에는 화자가 지정되어 있지 않습니다. 따라서 **자동으로 고객과 디자이너의 화자를 구분하여 정리하세요**.\n"
                    "**3. 대화 흐름을 유지하며, 논의 과정과 결론까지 포함하여 **상세하게 정리**할 것.\n"
                    "**4. 상담 내용을 아래 정리 형식 예시에 맞춰 정리하세요.**\n"
                    "**5. 상담 중 등장한 숫자, 금액, 일정, 제품명, 브랜드명 등을 **절대 생략하지 말 것**.\n"
                    "**6. 고객의 고민, 선택 과정, 최종 결정까지 상세히 기록할 것.\n"
                    "**7. 중요 항목은 **강조 표시** (예: 금액, 일정, 고객의 최종 결정 등)\n\n"
                    "**8. 상담 내용에서 논의된 주제의 개수는 정해져 있지 않으며, 모든 주제를 자동으로 정리하세요.**\n\n"
                    "**9. 상담 내용을 아래 정리 형식 예시에 맞춰 정리하세요.**\n\n"

                    "📌 **정리 형식 예시**\n"
                    "### **1. 상담 개요**\n"
                    "- 고객이 기존 아파트 리모델링을 위해 방문 상담 진행.\n"
                    "- 주방, 욕실, 창호 교체 및 거실 조명 변경 등을 논의.\n"
                    "- 초기 예산 1,000만 원, 확장 가능성 있음.\n"
                    "- 가족 구성원: 부부 + 7세 자녀 1명, 반려견 1마리.\n\n"

                    "### **2. 세부 상담 내용**\n"
                    "**1. 주방 리모델링**\n"
                    "- 고객 요청: ‘한샘’과 ‘LG’ 싱크대 비교 후 결정.\n"
                    "- 기존 싱크대 철거 비용: 약 **30만 원** 예상.\n"
                    "- 후드: ‘린나이 자동센서 후드’ 추천, 가격 **45만 원**.\n"
                    "- 조리대 소재: 엔지니어드 스톤 (한샘 기준 **약 150만 원**)\n\n"

                    "**2. 욕실 개선**\n"
                    "- 브랜드: 대림 바스 제품 우선 검토.\n"
                    "- 추가 옵션: ‘웰스 코팅’ 가능 (비용: **15만 원 추가**).\n"
                    "- 타일 변경 시 비용 증가 가능성 있음 (평균 **200만 원 예상**).\n\n"

                    "**3. 창호 교체**\n"
                    "- LG 샤시 246mm 교체 가능 여부 확인 중.\n"
                    "- 거실 창 전체 교체 시 예상 비용 **320만 원**.\n"
                    "- 추가로 방 창도 교체할 경우 **총 450만 원** 예상.\n\n"

                    "(주제가 많을 경우 자동으로 확장되며, 모든 내용을 포함해야 함.)\n\n"

                    "### **3. 결정해야 할 사항**\n"
                    "- 고객과 전문가가 최종적으로 결정해야 할 사항 (예: 마감재 선택, 예산 조정, 일정 확정 등)\n"
                    "- 아직 결론이 나지 않은 논의 사항\n\n"

                    "### **4. 결정된 사항**\n"
                    "- 상담 중 최종 결정된 내용 (예: 벽지 색상, 바닥재 선택, 공사 일정 등)\n"
                    "- 확정된 일정 및 예산\n\n"

                    "위와 같은 형식으로 상담 내용을 최대한 **자세히 기록**하고, 모든 정보를 포함해야 합니다."
                },
                {"role": "user", "content": input_text}
            ],
            max_tokens=4096  # 응답 길이를 충분히 확보
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ 요약 오류 발생: {e}")
        return "요약 실패"
