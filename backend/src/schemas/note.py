from pydantic import BaseModel,Field,model_validator
from typing import Literal
class NoteInput(BaseModel):
    title:str=Field(min_length=3,max_length=160)
    run_id:int|None=Field(default=None,gt=0)
    joint_run_id:int|None=Field(default=None,gt=0)
    interpretation:str=Field(min_length=8,max_length=2000)
    action:str=Field(min_length=5,max_length=1200)
    @model_validator(mode='after')
    def exactly_one_run(self):
        if (self.run_id is None)==(self.joint_run_id is None):raise ValueError('说明须关联且仅关联一项研究')
        return self
class NoteReview(BaseModel):
    decision:Literal['approved','rejected']
    comment:str=Field(min_length=5,max_length=1200)
