# app/pages/pdf_viewer.py
import os

def load_pdf():
    # プロジェクトのルートディレクトリからの相対パスを使用
    current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    pdf_path = os.path.join(current_dir, "pdf", "【納品用PDF】AI時代のサバイバル診断｜あなたの仕事はAIに奪われる？それとも進化する？.pdf")
    return open(pdf_path, "rb").read()