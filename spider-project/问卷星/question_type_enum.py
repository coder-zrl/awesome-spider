from enum import Enum


class QuestionType(Enum):
    Radio = 3  # 单选
    ControlGroup = 4  # 多选
    Scoring = 6  # 评分（非常满意、满意...）
