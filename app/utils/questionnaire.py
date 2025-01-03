# app/utils/questionnaire.py
import streamlit as st

from app.utils.rag_handler import get_ai_response

def display_questionnaire():    
    # セッションステートの初期化
    if "question_index" not in st.session_state:
        st.session_state.question_index = 0
    if "responses" not in st.session_state:
        st.session_state.responses = {}
    if "show_result" not in st.session_state:
        st.session_state.show_result = False
    if "is_generating" not in st.session_state:
        st.session_state.is_generating = False

    # 生成中の表示を最優先
    if st.session_state.is_generating:
        st.markdown("### 質問の診断")
        st.divider()
        with st.spinner("診断結果を生成中..."):
            try:
                response = get_ai_response(st.session_state.responses)
                st.session_state.result = response
                st.session_state.show_result = True
                st.session_state.is_generating = False
                st.rerun()
            except Exception as e:
                st.error(f"エラーが発生しました: {str(e)}")
                st.session_state.is_generating = False
        return  # 生成中は他の要素を表示しない

    # 判定結果の表示
    if st.session_state.show_result:
        st.write("診断結果:")
        st.write(st.session_state.result)
        
        if st.button("もう一度診断を行う"):
            # 状態をリセット
            st.session_state.question_index = 0
            st.session_state.responses = {}
            st.session_state.show_result = False
            st.session_state.is_generating = False
            st.session_state.result = None
            st.rerun()
        return
    else:
        st.markdown("### 質問の診断")
        st.divider()

    # 質問のリスト
    questions = [
        {
            "id": "q1",
            "title": "Q1. あなたの仕事は主にどのタイプですか？",
            "options": ["A: 単純作業が中心（例：データ入力）", "B: 半分以上が定型業務（例：経理業務）", "C: ⾮定型業務や創造的な仕事が中⼼（例：企画、設計）"]
        },
        {
            "id": "q2",
            "title": "Q2. あなたの仕事ではAIや⾃動化ツールを使っていますか？",
            "options": ["A: 全く使っていない", "B: ⼀部の業務で使っている", "C:  多くの業務で活⽤している"]
        },
        {
            "id": "q3",
            "title": "Q3. あなたの仕事に必要なスキルはどのタイプですか？",
            "options": ["A: ⼿順が決まっているスキル（例：⼯場作業)", "B: 分析や判断⼒が必要なスキル（例：マーケティング分析）", "C: ⾼度な専⾨知識や創造⼒が必要なスキル（例：デザイン、研究）"]
        },
        {
            "id": "q4",
            "title": "Q4. あなたの会社の業界はAI導⼊の進⾏状況がどうですか？",
            "options": ["A: AI導⼊が進んでいる（例：IT、⾦融）", "B: ⼀部の領域で導⼊されている（例：製造業）", "C: とても必要"]
        }
    ]

    # 現在の質問を表示
    current_q = questions[st.session_state.question_index]
    
    # 質問ブロックのスタイリング
    with st.container():
        st.markdown(f"""
        <div style='padding: 20px; border-radius: 10px; background-color: #f0f2f6;'>
            <h3>{current_q['title']}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # ラジオボタンで選択肢を表示
        answer = st.radio(
            "以下から選択してください：",
            current_q["options"],
            key=current_q["id"]
        )
        st.session_state.responses[current_q['title']] = answer

    # ナビゲーションボタン
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.session_state.question_index > 0:
            if st.button("← 前の質問"):
                st.session_state.question_index -= 1
                st.rerun()
    
    with col2:
        if st.session_state.question_index < len(questions) - 1:
            if st.button("次の質問 →"):
                st.session_state.question_index += 1
                st.rerun()
        else:
            if st.button("回答の判定結果を表示"):
                st.session_state.is_generating = True
                st.rerun()

    return st.session_state.responses