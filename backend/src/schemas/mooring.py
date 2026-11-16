from pydantic import BaseModel,Field
class MooringInput(BaseModel):
    code:str=Field(min_length=2,max_length=40,pattern=r'^[A-Za-z0-9-]+$')
    name:str=Field(min_length=2,max_length=100)
    description:str=Field(default='',max_length=800)
class MooringPatch(BaseModel):
    description:str=Field(max_length=800)
