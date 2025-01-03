# app/utils/rag_handler.py

import base64
from io import BytesIO
import os
import streamlit as st
import pymupdf4llm
from pdf2image import convert_from_path
from app.utils.dict_change_str import format_responses_to_prompt
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))


def convert_image_to_base64(pil_image) -> str:
    """PIL画像をbase64エンコードされた文字列に変換する"""
    buffered = BytesIO()
    pil_image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')


def initialize_rag() -> str:
    """PDFからテキストを抽出してマークダウン形式で返す
    
    Returns:
        str: マークダウン形式に変換されたPDFのテキスト
    """
    current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    pdf_path = os.path.join(current_dir, "pdf", "【納品用PDF】AI時代のサバイバル診断｜あなたの仕事はAIに奪われる？それとも進化する？.pdf")
    
    # PDFをマークダウンに変換
    markdown_text = pymupdf4llm.to_markdown(
        pdf_path,
        dpi=600
    )
    
    return markdown_text

def get_ai_response(user_responses: dict[str, str]):
    """
    ユーザーの回答に基づいてAIレスポンスを生成する

    Args:
        user_responses (dict[str, str]): 質問IDと回答のマッピング
            例: {
                "Q1. あなたの仕事は主にどのタイプですか？": "A: 単純作業が中心（例：データ入力）",
                "Q2. あなたの仕事ではAIや⾃動化ツールを使っていますか？": "B: ⼀部の業務で使っている",
                "Q3. あなたの仕事に必要なスキルはどのタイプですか？": "A: ⼿順が決まっているスキル（例：⼯場作業）",
                "Q4. あなたの会社の業界はAI導⼊の進⾏状況がどうですか？": "C: ほとんど導⼊が進んでいない（例：飲⾷業、⼩売業）"
            }
    Returns:
        適切な戻り値の型アノテーションも必要に応じて追加
    """
    # 画像変換
    current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    pdf_path = os.path.join(current_dir, "pdf", "【納品用PDF】AI時代のサバイバル診断｜あなたの仕事はAIに奪われる？それとも進化する？.pdf")
    image_conv = convert_from_path(pdf_path, 600)
    base64_image = convert_image_to_base64(image_conv[0])

    # テキスト抽出
    markdown_text = initialize_rag()
    user_prompt = format_responses_to_prompt(user_responses)
    
    system_prompt = f"""
    # Context
    質問に対するユーザーの各選択を与えられた提供資料からスコアリングし、全てのスコアを合計して回答として
    判定結果とその対策案を提示することです。

    # Reference materials
    {markdown_text}
    
    # thinking step
    1. 質問とユーザー選択肢からスコアを計算
    2. 各質問に対するユーザーの回答の合計スコアを計算
    3. 合計スコアに応じて判定結果を生成
    4. 判定結果に基づいて推奨案を提示
    
    # Calculation example
    手順1:
    | 質問1 | ユーザー回答 | スコア |
    | あなたの仕事は主にどのタイプですか？ | A: 単純作業が中心（例：データ入力）  | 3ポイント |
    | 質問2 | ユーザー回答 | スコア |
    | あなたの仕事ではAIや⾃動化ツールを使っていますか？ | B: ⼀部の業務で使っている  | 2ポイント |
    
    手順2:
    3 + 2 = 5ポイント
    
    手順3:
    合計スコア 5ポイント
    
    # Output Format
    以下の形式で結果を出力してください：

    # スコア計算

    | 質問 | ユーザー回答 | スコア |
    |------|--------------|--------|
    | Q1   | [回答内容]   | [点数] |
    | Q2   | [回答内容]   | [点数] |
    | Q3   | [回答内容]   | [点数] |
    | Q4   | [回答内容]   | [点数] |

    # 合計スコア
    合計スコア = [計算式] = [総計]ポイント

    # 診断結果
    - スコア範囲：[範囲] ([評価])
    - [診断結果の詳細説明]

    # 具体的対策
    - [対策1]
    - [対策2]
    - [対策3]

    # Rules
    1. スコアは提供された資料に基づいて計算してください
    2. 合計スコアは各質問のスコアを足し合わせてください
    3. 診断結果は合計スコアの範囲に応じて判定してください
    4. 具体的対策は診断結果に基づいて提案してください
    5. 表はマークダウン形式で作成してください
    """
    # レスポンス生成
    messages = [
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "user",
            "content": [
                {"type": "text", "text": user_prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{base64_image}"
                    }
                }
            ],
        },
    ]
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    return response.choices[0].message.content