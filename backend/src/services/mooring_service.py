from sqlalchemy import select
from fastapi import HTTPException
from src.models import Mooring
from src.utils.audit import record
from src.utils.serializers import serialize
def listing(db):return [serialize(x) for x in db.scalars(select(Mooring).order_by(Mooring.id))]
def create(db,data,user):
    if db.scalar(select(Mooring).where(Mooring.code==data.code)):raise HTTPException(409,'浮标编号已存在')
    row=Mooring(**data.model_dump());db.add(row);db.flush();record(db,user,'mooring.created',row.id);db.commit();return serialize(row)
def patch(db,id,data,user):
    row=db.get(Mooring,id)
    if not row:raise HTTPException(404,'浮标不存在')
    row.description=data.description;record(db,user,'mooring.edited',id);db.commit();return serialize(row)
