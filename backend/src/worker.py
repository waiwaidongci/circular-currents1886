import time,logging
from pathlib import Path
from src.config.database import SessionLocal
from src.config.queue import queue
from src.models import DirectionRun,JointRun
from src.services import run_service,joint_service
logging.basicConfig(level=logging.INFO)
TASKS={run_service.QUEUE:(run_service,DirectionRun),joint_service.QUEUE:(joint_service,JointRun)}
while True:
    Path('/tmp/heartbeat').touch()
    try:
        item=queue.blpop(list(TASKS),timeout=4)
        if not item:continue
        service,model=TASKS[item[0]]
        with SessionLocal() as db:
            try:service.compute(db,int(item[1]))
            except Exception as exc:
                db.rollback();run=db.get(model,int(item[1]))
                if run:run.status='failed';run.error=str(exc)[:500];db.commit()
                logging.exception('direction research failed')
    except Exception:logging.exception('worker loop');time.sleep(2)
