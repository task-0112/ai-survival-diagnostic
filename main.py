import streamlit as st
from streamlit_pdf_viewer import pdf_viewer
from app.pages.pdf_viewer import load_pdf
from app.utils.questionnaire import display_questionnaire

st.set_page_config(
    page_title="AI Survival Diagnostic",
    page_icon="🤖",
    layout="wide"
)

def main():
    col1, col2 = st.columns([1, 1])

    with col1:
        display_questionnaire()

    with col2:
        st.markdown("### PDFプレビュー")
        st.divider()
        try:
            pdf_bytes = load_pdf()
            # コンテナで高さを制限し、スクロール可能にする
            with st.container(height=600):  # 高さは適宜調整してください
                pdf_viewer(
                    pdf_bytes,
                    width=None,  # 幅を自動調整
                    rendering="unwrap",  # アンラップモードを使用
                    pages_vertical_spacing=2,  # ページ間のスペース
                    render_text=True,  # テキスト選択を有効化
                    resolution_boost=1.3  # 解像度を少し上げる
                )
        except Exception as e:
            st.error(f"PDFの読み込みに失敗しました: {str(e)}")

if __name__ == "__main__":
    main()