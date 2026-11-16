import os,sys,time,resource
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from src.services.joint_algorithm import compare_joint,estimate_peak_bytes,MEMORY_CAP_BYTES
def bench():
    rng=np.random.default_rng(7)
    groups=[np.rad2deg(rng.vonmises(np.deg2rad(10*i),8,100))%360 for i in range(32)]
    started=time.time();joint=compare_joint(groups,999,157);elapsed=time.time()-started
    peak=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
    estimate=estimate_peak_bytes(3200,32,999)
    print(f'32座×100条×999次重分：{elapsed:.1f}s（上限30s），峰值RSS {peak:.0f}MB（上限256MB，预估{estimate/1024**2:.0f}MB），零分布{joint["null_statistics"].shape}')
    assert elapsed<30,f'超时:{elapsed:.1f}s'
    assert peak<256,f'超内存:{peak:.0f}MB'
    return joint
if __name__=='__main__':bench()
