from src.constants.enums import Role
from fastapi import APIRouter,Depends
from src.config.database import session
from src.middlewares.auth import require
from src.schemas.joint import JointRunInput
from src.controllers.joint_controller import listing,detail,create
router=APIRouter(prefix='/joint-runs')
@router.get('')
def index(db=Depends(session),u=Depends(require(Role.ADMIN,Role.ANALYST,Role.VIEWER))):return listing(db)
@router.get('/{id}')
def show(id:int,db=Depends(session),u=Depends(require(Role.ADMIN,Role.ANALYST,Role.VIEWER))):return detail(db,id)
@router.post('',status_code=202)
def add(data:JointRunInput,db=Depends(session),u=Depends(require(Role.ADMIN,Role.ANALYST))):return create(db,data,u)
