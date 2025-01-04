# app/utils/rag_handler.py

import base64
from io import BytesIO
import os
import tempfile
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

def get_ai_response(user_responses: dict[str, str], user_info: dict = None):
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
    with tempfile.TemporaryDirectory() as path:
        image_conv = convert_from_path(
            pdf_path, 
            600,
            output_folder=path
        )
        base64_image = convert_image_to_base64(image_conv[0])

        # テキスト抽出
        markdown_text = initialize_rag()
        user_prompt = format_responses_to_prompt(user_responses)
        
        system_prompt = f"""
        # Context
        ユーザーの個人プロフィールと質問への回答を総合的に分析し、個人に紐づく形で凝った形で診断結果の提示と具体的な対策案を提示することです。

        # ユーザー情報
        - 業界: {st.session_state.user_info.get('industry')}
        - 職種: {user_info.get('occupation')} 
        - 経験年数: {st.session_state.user_info.get('experience')}年
        - 保有スキル: {', '.join(st.session_state.user_info.get('skills', []))}

        # Reference materials
        {markdown_text}

        # thinking step
        1. 質問とユーザー選択肢からスコアを計算
        - Q1: 仕事タイプ （A=3点, B=2点, C=1点）
        - Q2: AIツール活用 （A=3点, B=2点, C=1点）
        - Q3: 必要スキル （A=3点, B=2点, C=1点）
        - Q4: AI導入状況 （A=1点, B=2点, C=3点）

        2. 各質問に対するユーザーの回答の合計スコアを計算
        - 4問の合計点を算出（4-12点）
        - スコア範囲の判定（4-6点=安全、7-9点=要注意、10-12点=危険）

        3. ユーザーの業界・職種分析
        - 業界のAI導入状況の分析
        - 職種特有のAIリスク評価
        - 経験年数と保有スキルの強み分析

        4. 総合診断の生成
        - スコア判定と業界・職種分析の統合
        - 個人プロフィールを考慮した詳細な診断

        5. パーソナライズされた対策案の作成
        - 即時対策（1-3ヶ月）の提案
        - 中長期対策（3-6ヶ月）の提案
        - 保有スキルを活かした具体的な改善案

        6. AIコース・学習プランの提案
        - レベルと職種に応じた基礎コースの選定
        - 業界特化型の専門コースの提案
        - 具体的なツール習得プランの作成

        # Calculation example
        手順1:
        | 質問1 | ユーザー回答 | スコア |
        | あなたの仕事は主にどのタイプですか？ | A: 単純作業が中心（例：データ入力）  | 3ポイント |
        | 質問2 | ユーザー回答 | スコア |
        | あなたの仕事ではAIや⾃動化ツールを使っていますか？ | B: ⼀部の業務で使っている  | 2ポイント |

        手順2:
        3 + 2 = 5ポイント

        # Output example Format
        以下の形式例を参考にして結果を出力してください：
        
        ## 業界分析
        - [業界]における現在のAI導入状況
        - 今後予想される変化と影響

        ## キャリア分析
        - 現在の[職種]に対するAIの影響
        - [経験年数]を活かした発展可能性
        - [保有スキル]の将来的な価値

        # スコア計算
        | 質問 | ユーザー回答 | スコア | 個別分析 |
        |------|------------|--------|---------|
        | Q1   | [回答内容] | [点数] | [分析]  |
        | Q2   | [回答内容] | [点数] | [分析]  |
        | Q3   | [回答内容] | [点数] | [分析]  |
        | Q4   | [回答内容] | [点数] | [分析]  |

        # 合計スコア
        合計スコア = [計算式] = [総計]ポイント

        # 総合診断
        - スコア範囲：[範囲] ([評価])
        - [個人に紐づく形で凝った形で診断結果の提示]

        # パーソナライズされた対策案
        ## 即時対策（1-3ヶ月）
        - [業界]特有のAI対応施策
        - [職種]に関連する具体的なスキルアップ項目
        - [保有スキル]を活かした業務改善案

        ## 中長期対策（3-6ヶ月）
        - キャリアパス提案
        - 新規獲得すべきスキル
        - [業界]での競争力強化策

        # おすすめのAIコース
        ## 現在のレベルに応じた学習ステップ
        1. 基礎スキル習得
        - AI初心者向けの具体的な教材やツールの推奨
        - ChatGPTやDALL-Eの[職種]での具体的な活用方法

        各ステップの詳細は以下のリンクから確認できます：
        - Udemy: https://www.udemy.com/
        - Coursera: https://www.coursera.org/

        # Rules
        1. スコアは提供された資料に基づいて計算してください
        2. 合計スコアは各質問のスコアを足し合わせてください
        3. 診断結果は合計スコアの範囲に応じて判定してください
        4. 個人に紐づく形に基づいて診断結果の提案してください
        5. 表はマークダウン形式で作成してください
        6. すべての提案は[業界]と[職種]に特化した具体的なものにしてください
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