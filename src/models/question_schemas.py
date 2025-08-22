from typing import List
from pydantic import BaseModel,Field, validator

class MCQuestion(BaseModel):

    question: str = Field(description="The question text")

    options: List[str] = Field(description="List of 4 option")

    correct_answer:str = Field(description="The correct answer from the options")

    @validator("question", pre = True)
    def clean_question(cls,v):
        if isinstance(v,dict):
            return v.get("description",str(v))
        return str(v)
    
class FillBlankQuestion(BaseModel):

    question: str = Field(description="The Question text with '__' for the blank")

    answer: str = Field(description="The correct word or phrase for the blank ")

    @validator("question", pre = True)
    def clean_question(cls,v):
        if isinstance(v,dict):
            return v.get("description",str(v))
        return str(v)
