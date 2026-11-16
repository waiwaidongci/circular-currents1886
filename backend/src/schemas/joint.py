from pydantic import BaseModel,Field,field_validator
class JointRunInput(BaseModel):
    name:str=Field(min_length=3,max_length=160)
    survey_id:int=Field(gt=0)
    mooring_ids:list[int]=Field(min_length=3,max_length=32)
    permutations:int=Field(default=499,ge=99,le=999)
    seed:int=Field(default=157,ge=0,le=2147483647)
    @field_validator('mooring_ids')
    @classmethod
    def distinct(cls,ids):
        if any(i<=0 for i in ids):raise ValueError('浮标编号无效')
        if len(set(ids))!=len(ids):raise ValueError('联合研究浮标不得重复')
        return ids
