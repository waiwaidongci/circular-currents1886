from src.constants.enums import Role
from fastapi import APIRouter,Depends
from src.config.database import session
from src.middlewares.auth import require
from src.schemas.mooring import MooringInput,MooringPatch
from src.controllers.mooring_controller import listing,create,patch
router=APIRouter(prefix='/moorings')
@router.get('')
def index(db=Depends(session),u=Depends(require(Role.ADMIN,Role.ANALYST,Role.VIEWER))):return listing(db)
@router.post('',status_code=201)
def add(data:MooringInput,db=Depends(session),u=Depends(require(Role.ADMIN,Role.ANALYST))):return create(db,data,u)
@router.patch('/{id}')
def edit(id:int,data:MooringPatch,db=Depends(session),u=Depends(require(Role.ADMIN))):return patch(db,id,data,u)
