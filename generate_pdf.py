from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import os
import re

# -----------------------------
# 1) 폰트 등록
# -----------------------------
font_path = "assets/NanumGothic.ttf"
bold_font_path = "assets/NanumGothicBold.ttf"

if not os.path.exists(font_path):
    font_path = "C:/Windows/Fonts/malgun.ttf"
    bold_font_path = "C:/Windows/Fonts/malgunbd.ttf"

pdfmetrics.registerFont(TTFont("KoreanFont", font_path))
pdfmetrics.registerFont(TTFont("KoreanFont-Bold", bold_font_path))

# -----------------------------
# 2) 인라인 볼드 & 자동 줄바꿈 함수
# -----------------------------
def draw_wrapped_text_with_bold(c, text, x, y, available_width, line_height, font_size=12):
    """
    **텍스트** 내 인라인 볼드(**)를 감지하여 폰트 변경.
    available_width를 초과하면 단어 단위로 줄바꿈.
    반환값: 출력이 끝난 후 y 좌표
    """
    current_x = x
    current_y = y

    segments = re.split(r"(\*\*.*?\*\*)", text)  # **볼드** 부분 분리
    for segment in segments:
        is_bold = segment.startswith("**") and segment.endswith("**")
        if is_bold:
            seg_text = segment[2:-2]  # ** 제거
            font_name = "KoreanFont-Bold"
        else:
            seg_text = segment
            font_name = "KoreanFont"

        # 단어 단위로 분리
        words = seg_text.split(" ")
        for word in words:
            word_with_space = word + " " if word else " "
            word_width = c.stringWidth(word_with_space, font_name, font_size)

            # 남은 폭보다 길면 줄바꿈
            if (current_x - x) + word_width > available_width:
                current_y -= line_height
                current_x = x

            c.setFont(font_name, font_size)
            c.drawString(current_x, current_y, word_with_space)
            current_x += word_width

    # 마지막 줄 출력 후, 다음 줄로 이동
    return current_y - line_height

# -----------------------------
# 3) 헤더/푸터 그리는 함수
# -----------------------------
def draw_header(c, page_width, page_height,
                top_margin, right_margin, left_margin,
                brand_color, line_width,
                logo_path,
                logo_width, logo_height):
    """
    새 페이지가 열릴 때마다 상단 로고와 컬러 라인을 그려주는 함수.
    반환값: 본문 시작 y 좌표 (헤더 아래로 약간 내려간 위치)
    """
    # 로고 배치 (오른쪽 상단)
    logo_x = page_width - right_margin - logo_width + 30
    # 최대한 위로 붙여 배치 (top_margin만큼 띄운 상태에서 로고 높이를 뺀 위치)
    logo_y = page_height - top_margin - logo_height

    c.drawImage(
        logo_path,
        logo_x,
        logo_y,
        width=logo_width,
        height=logo_height,
        preserveAspectRatio=True
    )

    # 로고 아래 컬러 라인
    c.setStrokeColorRGB(*brand_color)  # (0.3, 0.75, 0.4) 등
    c.setLineWidth(line_width)         # 1.4 (30% 축소 예시)
    line_y = logo_y - 10
    c.line(left_margin, line_y, page_width - right_margin, line_y)

    # 펜/색상 복귀
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(1)

    # 본문 시작 위치 (라인 아래로 조금 더 내려서)
    start_y = line_y - 30
    return start_y

def draw_footer(c, page_width, page_height,
                bottom_margin, left_margin, right_margin,
                brand_color, line_width,
                address_str, phone_str, email_str):
    """
    페이지 하단 푸터(컬러 라인 + 연락처 정보) 그리는 함수
    - 주소는 왼쪽, 이메일은 오른쪽
    - 전화번호는 '주소 오른쪽 끝'과 '이메일 왼쪽 시작' 사이의 중앙
    """
    # 푸터 라인을 살짝 위로 올림 (bottom_margin + 20)
    foot_line_y = bottom_margin + 20

    # 컬러 라인
    c.setStrokeColorRGB(*brand_color)
    c.setLineWidth(line_width)
    c.line(left_margin, foot_line_y, page_width - right_margin, foot_line_y)

    # 푸터 텍스트 (폰트 크기 더 작게, 예: 9)
    footer_font_size = 9
    c.setFont("KoreanFont", footer_font_size)
    c.setFillColorRGB(0, 0, 0)

    text_y = foot_line_y - 15

    # (1) 주소: 왼쪽
    address_x = left_margin
    c.drawString(address_x, text_y, address_str)
    address_width = c.stringWidth(address_str, "KoreanFont", footer_font_size)

    # (2) 이메일: 오른쪽
    email_width = c.stringWidth(email_str, "KoreanFont", footer_font_size)
    email_x = page_width - right_margin - email_width
    c.drawString(email_x, text_y, email_str)

    # (3) 전화번호: 주소와 이메일 사이의 중앙
    phone_width = c.stringWidth(phone_str, "KoreanFont", footer_font_size)
    # 주소 오른쪽 끝 = address_x + address_width
    # 이메일 왼쪽 시작 = email_x
    midpoint = ((address_x + address_width) + email_x) / 2
    phone_x = midpoint - (phone_width / 2)
    c.drawString(phone_x, text_y, phone_str)

    # 펜/색상 복귀
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(1)

# -----------------------------
# 4) 메인 PDF 생성 함수
# -----------------------------
def generate_pdf(text_path, pdf_path):
    """
    다중 페이지 PDF 생성:
    - 헤더를 위로, 푸터를 살짝 위로
    - 전화번호는 주소와 이메일 사이 중앙에 위치
    - 녹색 선 굵기/색상 등은 취향에 맞게 조정
    """

    os.makedirs("pdfs", exist_ok=True)
    c = canvas.Canvas(pdf_path, pagesize=A4)
    page_width, page_height = A4

    # 디자인 파라미터
    brand_color = (0.7, 0.9, 0.7)
    line_width = 1               # 기존 대비 30% 축소

    # 로고
    logo_path = "assets/company_logo.png"
    logo_width = 120
    logo_height = 60

    # 상하좌우 마진
    top_margin = 40
    bottom_margin = 40
    left_margin = 60
    right_margin = 60

    # 본문 폰트/라인
    normal_font_size = 12
    normal_line_height = 20

    # 헤더(###) 폰트/라인
    heading_font_size = 18
    heading_line_height = 28

    # 푸터 연락처 정보
    address_str = "마곡중앙로 59-21 에이스타워 2차 4층 419호"
    phone_str = "02-3662-8929"
    email_str = "info@wellgadesign.com"

    # 첫 페이지 헤더
    y_position = draw_header(
        c,
        page_width, page_height,
        top_margin, right_margin, left_margin,
        brand_color, line_width,
        logo_path,
        logo_width, logo_height
    )

    # 푸터에 필요한 높이(라인+텍스트 등) + 안전 여백
    footer_reserved_space = 70

    # 본문 출력 가능 최대 폭
    usable_width = page_width - left_margin - right_margin

    # 상담 내용 읽기
    with open(text_path, "r", encoding="utf-8") as f:
        summary_text = f.readlines()

    for line in summary_text:
        line = line.strip()

        # 라인 출력에 필요한 폰트 크기/라인 높이 결정
        if line.startswith("### "):
            line_font_size = heading_font_size
            line_height = heading_line_height
        else:
            line_font_size = normal_font_size
            line_height = normal_line_height

        # 현재 페이지에 남은 공간 체크
        if y_position < (bottom_margin + footer_reserved_space):
            # 푸터 그린 뒤 페이지 넘김
            draw_footer(
                c, page_width, page_height,
                bottom_margin, left_margin, right_margin,
                brand_color, line_width,
                address_str, phone_str, email_str
            )
            c.showPage()  # 새 페이지

            # 새 페이지 헤더
            y_position = draw_header(
                c,
                page_width, page_height,
                top_margin, right_margin, left_margin,
                brand_color, line_width,
                logo_path,
                logo_width, logo_height
            )

        # 실제 텍스트 출력
        if line.startswith("### "):
            # 헤더 텍스트만 추출
            y_position -= line_height
            header_text = line.replace("### ", "")
            y_position -= (line_height * 0.3)
            y_position = draw_wrapped_text_with_bold(
                c,
                header_text,
                left_margin,
                y_position,
                usable_width,
                line_height,
                font_size=line_font_size
            )
            y_position -= (line_height * 0.3)

        elif line.startswith("- "):
            bullet_text = "• " + line[2:]
            y_position = draw_wrapped_text_with_bold(
                c,
                bullet_text,
                left_margin + 10,
                y_position,
                usable_width - 10,
                normal_line_height,
                font_size=normal_font_size
            )

        elif line == "":
            # 빈 줄
            y_position -= (normal_line_height * 0.5)
        else:
            # 일반 텍스트
            y_position = draw_wrapped_text_with_bold(
                c,
                line,
                left_margin,
                y_position,
                usable_width,
                normal_line_height,
                font_size=normal_font_size
            )

    # 모든 텍스트 출력 후 마지막 푸터
    draw_footer(
        c, page_width, page_height,
        bottom_margin, left_margin, right_margin,
        brand_color, line_width,
        address_str, phone_str, email_str
    )

    c.save()
    print(f"✅ PDF 저장 완료: {pdf_path}")
