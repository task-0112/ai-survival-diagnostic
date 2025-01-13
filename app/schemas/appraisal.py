from pydantic import BaseModel, Field
from typing import Literal


class Employee(BaseModel):
    """初心者か中級者以上か判断"""
    appraisal_type: Literal["beginner", "intermediate_or_above"] = Field(
        description="ユーザー情報から初心者か中級者以上か判断する"
    )

