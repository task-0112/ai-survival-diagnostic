def format_responses_to_prompt(user_responses: dict[str, str]) -> str:
    """回答を生成AIに送信する形式の文字列に変換する

    Args:
        user_responses: 質問文と回答のマッピング
    Returns:
        str: 整形された回答文字列
    """
    # 回答を改行区切りのテキストに変換
    formatted_responses = "ユーザーの回答:\n"
    for question, answer in user_responses.items():
        formatted_responses += f"質問: {question}\n回答: {answer}\n\n"

    return formatted_responses