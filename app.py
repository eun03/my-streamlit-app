
import streamlit as st
from openai import OpenAI

# OpenAI 클라이언트 생성
client = OpenAI()

# 페이지 설정
st.set_page_config(
    page_title="ABLE AI 개인비서",
    page_icon="🤖",
    layout="wide"
)

# 역할 지정
sys_role = """
당신은 김 대리의 AI 개인비서 '에이블'입니다.
김 대리의 업무를 효율적으로 지원합니다.
친절하고 이해하기 쉽게 답변합니다.
"""

# -------------------------
# 1. 왼쪽 사이드바 메뉴
# -------------------------

st.sidebar.title("🤖 ABLE")
st.sidebar.caption("김 대리의 AI 개인비서")
st.sidebar.divider()

menu = st.sidebar.radio(
    "메뉴",
    [
        "홈",
        "일정",
        "회의 관리",
        "회의록 요약",
        "자료 조사",
        "자료 요약",
        "자료 번역",
        "자료 교정",
        "이메일 작성",
        "이메일 관리",
        "음성 명령",
        "실시간 음성 대화",
        "새로운 대화",
        "최근 대화"
    ]
)

# -------------------------
# 2. 오른쪽 메인 화면
# -------------------------

if menu == "홈":

    st.title("안녕하세요, 김 대리님! 👋")
    st.write("에이블이 업무를 도와드리겠습니다.")

    st.subheader("주요 기능")

    col1, col2 = st.columns(2)

    with col1:
        st.info("📅 일정 관리\n\n업무 및 회의 일정 확인")

        st.info("📁 자료 관리\n\n자료 조사 및 요약, 번역, 교정")

    with col2:
        st.info("📝 회의 관리\n\n회의록 요약 및 업무 추출")

        st.info("✉️ 이메일 관리\n\n이메일 작성 및 발송")

    st.info("🎙 음성 비서와 AI에게 질문하기를 통해 에이블과 대화할 수 있습니다.")


elif menu == "일정":

    st.title("📅 일정")
    st.write("업무 및 회의 일정을 관리합니다.")
    st.info("일정 조회 및 등록 기능을 구현할 예정입니다.")


elif menu == "회의 관리":

    st.title("📝 회의 관리")
    st.write("회의 일정과 관련 정보를 관리합니다.")
    st.info("회의 관리 기능을 구현할 예정입니다.")


elif menu == "회의록 요약":

    st.title("📄 회의록 요약")
    st.write("회의록을 업로드하면 AI가 핵심 내용을 요약합니다.")
    st.info("회의록 요약 기능을 구현할 예정입니다.")


elif menu == "자료 조사":

    st.title("🔍 자료 조사")
    st.write("업무에 필요한 자료와 정보를 조사합니다.")
    st.info("자료 조사 기능을 구현할 예정입니다.")


elif menu == "자료 요약":

    st.title("📁 자료 요약")
    st.write("문서를 업로드하면 핵심 내용을 요약합니다.")
    st.info("자료 요약 기능을 구현할 예정입니다.")


elif menu == "자료 번역":

    st.title("🌐 자료 번역")
    st.write("문서 및 텍스트를 원하는 언어로 번역합니다.")
    st.info("자료 번역 기능을 구현할 예정입니다.")


elif menu == "자료 교정":

    st.title("✏️ 자료 교정")
    st.write("문서의 맞춤법과 문장 표현을 교정합니다.")
    st.info("자료 교정 기능을 구현할 예정입니다.")


elif menu == "이메일 작성":

    st.title("✉️ 이메일 작성")
    st.write("업무 상황에 맞는 이메일을 작성합니다.")
    st.info("이메일 작성 기능을 구현할 예정입니다.")


elif menu == "이메일 관리":

    st.title("📬 이메일 관리")
    st.write("이메일 내용을 확인하고 관리합니다.")
    st.info("이메일 관리 기능을 구현할 예정입니다.")


elif menu == "음성 명령":

    st.title("🎙 음성 명령")
    st.write("음성으로 업무를 요청하고 AI 답변을 확인하세요.")

    # 음성 명령 입력
    with st.form("voice_form"):

        uploaded_file = st.file_uploader(
            "텍스트 파일 업로드",
            type=["txt"]
        )

        audio_value = st.audio_input("무엇을 도와드릴까요?")

        submit = st.form_submit_button("실행")

    # 실행 버튼을 눌렀을 때
    if submit:

        # 업로드 파일 읽기
        text = ""

        if uploaded_file is not None:
            text = uploaded_file.read().decode("utf-8")

        # 음성 녹음 확인
        if audio_value is None:
            st.warning("음성을 녹음해주세요.")
            st.stop()

        # 시스템 메시지 구성
        system_content = sys_role

        if text:
            system_content += f"\n\n다음 내용을 참고하세요:\n{text}"

        input_messages = [
            {"role": "system", "content": system_content}
        ]

        # STT: 음성을 텍스트로 변환
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=("audio.wav", audio_value, "audio/wav")
        )

        # 음성 인식 결과 출력
        st.subheader("음성 인식 결과")
        st.write(transcript.text)

        input_messages.append(
            {"role": "user", "content": transcript.text}
        )

        # LLM 호출
        with st.spinner("답변을 준비하고 있습니다..."):

            response = client.responses.create(
                model="gpt-4o-mini",
                input=input_messages
            )

            answer = response.output_text

            st.subheader("에이블의 답변")
            st.write(answer)


elif menu == "실시간 음성 대화":

    st.title("🎧 실시간 음성 대화")
    st.write("에이블과 음성으로 대화를 이어가세요.")
    st.info("실시간 음성 대화 기능을 구현할 예정입니다.")


elif menu == "새로운 대화":

    st.title("💬 새로운 대화")
    st.write("에이블에게 궁금한 내용을 질문해 보세요.")
    st.info("새로운 대화 기능을 구현할 예정입니다.")


elif menu == "최근 대화":

    st.title("🕘 최근 대화")
    st.write("이전에 나눈 대화 내용을 확인할 수 있습니다.")
    st.info("최근 대화 10개 저장 기능을 구현할 예정입니다.")
