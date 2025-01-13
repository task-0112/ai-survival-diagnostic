from typing import Literal
from pydantic import BaseModel, Field

class CourseRecommendation(BaseModel):
    """どのコースが適切か判断"""
    appraisal_type: Literal[
        "music_ai", 
        "video_ai", 
        "chatgpt", 
        "image_ai", 
        "prompt_collection", 
        "document_creation"
    ] = Field(
        description="ユーザー情報から最適なコースを判断する"
    )
