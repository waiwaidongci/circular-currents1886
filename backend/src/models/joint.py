from datetime import datetime
from sqlalchemy import String,ForeignKey,JSON,DateTime
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class JointRun(Base):
    __tablename__='joint_runs'
    id:Mapped[int]=mapped_column(primary_key=True)
    name:Mapped[str]=mapped_column(String(160),unique=True)
    survey_id:Mapped[int]=mapped_column(ForeignKey('direction_surveys.id'))
    mooring_ids:Mapped[list]=mapped_column(JSON,default=list)
    permutations:Mapped[int]=mapped_column(default=499)
    seed:Mapped[int]=mapped_column(default=157)
    status:Mapped[str]=mapped_column(String(20),default='queued')
    result:Mapped[dict]=mapped_column(JSON,default=dict)
    null_statistics:Mapped[list]=mapped_column(JSON,default=list)
    error:Mapped[str]=mapped_column(String(700),default='')
    created_by:Mapped[int]=mapped_column(ForeignKey('users.id'))
    created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
