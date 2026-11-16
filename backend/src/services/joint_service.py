from sqlalchemy import select,func
from fastapi import HTTPException
from src.models import JointRun,DirectionSurvey,Mooring,BearingReading
from src.config.queue import queue
from src.constants.enums import RunStatus
from src.utils.audit import record
from src.utils.serializers import serialize
from src.services.joint_analysis import analyze_joint
from src.services.joint_algorithm import estimate_peak_bytes,MEMORY_CAP_BYTES
QUEUE='currents:joint-runs'
def _trim(row,full):
    data=serialize(row)
    if not full:
        data.pop('null_statistics',None)
        result=dict(data.get('result') or {});result.pop('input_snapshot',None);data['result']=result
    return data
def listing(db):return [_trim(x,False) for x in db.scalars(select(JointRun).order_by(JointRun.id.desc()))]
def detail(db,id):
    run=db.get(JointRun,id)
    if not run:raise HTTPException(404,'联合研究不存在')
    return _trim(run,True)
def create(db,data,user):
    if not db.get(DirectionSurvey,data.survey_id):raise HTTPException(404,'调查不存在')
    moorings={m.id:m for m in db.scalars(select(Mooring).where(Mooring.id.in_(data.mooring_ids)))}
    if len(moorings)!=len(data.mooring_ids):raise HTTPException(404,'浮标不存在')
    if db.scalar(select(JointRun).where(JointRun.name==data.name)):raise HTTPException(409,'研究名称重复')
    sizes=[]
    for mooring_id in data.mooring_ids:
        sizes.append(db.scalar(select(func.count()).select_from(BearingReading).where(BearingReading.survey_id==data.survey_id,BearingReading.mooring_id==mooring_id)))
    estimate=estimate_peak_bytes(sum(sizes),len(sizes),data.permutations)
    if estimate>MEMORY_CAP_BYTES:raise HTTPException(422,f'超出容量：估计峰值内存{estimate/1024**2:.0f}MB，超过256MB上限；请减少浮标数、每组样本量或置换次数')
    row=JointRun(**data.model_dump(),created_by=user.id,status=RunStatus.QUEUED);db.add(row);db.flush();record(db,user,'joint_run.queued',row.id);db.commit();queue.rpush(QUEUE,str(row.id));return serialize(row)
def compute(db,id):
    run=db.get(JointRun,id)
    if not run or run.status not in ['queued','running']:return
    run.status=RunStatus.RUNNING;db.commit()
    moorings=[]
    for mooring_id in run.mooring_ids:
        mooring=db.get(Mooring,mooring_id)
        items=db.scalars(select(BearingReading).where(BearingReading.survey_id==run.survey_id,BearingReading.mooring_id==mooring_id).order_by(BearingReading.code)).all()
        moorings.append({'mooring_id':mooring_id,'code':mooring.code,'name':mooring.name,'rows':[{'code':x.code,'bearing':x.bearing,'observed_at':x.observed_at} for x in items]})
    result,null_statistics=analyze_joint(moorings,{'survey_id':run.survey_id,'mooring_ids':run.mooring_ids,'permutations':run.permutations,'seed':run.seed})
    run.result=result;run.null_statistics=null_statistics;run.status=RunStatus.COMPLETED;run.error='';db.commit();return serialize(run)
