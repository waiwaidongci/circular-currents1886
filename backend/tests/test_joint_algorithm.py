import os,sys
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from src.services.energy_algorithm import chord_matrix,statistic,compare
from src.services.joint_algorithm import compare_joint,estimate_peak_bytes,MEMORY_CAP_BYTES
def _reference(groups,repetitions,seed):
    values=np.concatenate(groups);sizes=[len(g) for g in groups];k=len(groups)
    distance=chord_matrix(values,[]);labels=np.repeat(np.arange(k),sizes)
    pairs=[(i,j) for i in range(k) for j in range(i+1,k)]
    observed=np.array([statistic(distance,np.where(labels==i)[0],np.where(labels==j)[0]) for i,j in pairs])
    rng=np.random.default_rng(seed);null=[]
    for _ in range(repetitions):
        perm=rng.permutation(labels)
        null.append([statistic(distance,np.where(perm==i)[0],np.where(perm==j)[0]) for i,j in pairs])
    return observed,np.array(null)
def _brute_stepdown(observed,null):
    repetitions,m=null.shape;order=np.argsort(-observed,kind='stable');ranked=observed[order]
    adjusted=np.empty(m);best=0.0
    for r in range(m):
        successive=null[:,order[r:]].max(axis=1)
        best=max(best,(1+np.count_nonzero(successive>=ranked[r]-1e-12))/(repetitions+1))
        adjusted[order[r]]=best
    return adjusted
def test_cross_check_small_samples():
    rng=np.random.default_rng(42)
    for k,sizes,repetitions,seed in [(3,[3,4,5],99,7),(4,[2,3,4,6],99,11),(5,[4,4,4,4,4],199,13),(3,[10,12,9],499,17),(6,[3,5,2,4,6,3],99,23)]:
        groups=[np.sort(rng.uniform(0,360,n)) for n in sizes]
        joint=compare_joint(groups,repetitions,seed)
        observed,null=_reference(groups,repetitions,seed)
        assert np.allclose(joint['statistic'],observed,atol=1e-9),'观测统计量与直接距离矩阵不一致'
        assert np.allclose(joint['null_statistics'],null,atol=1e-9),'逐次置换统计量与直接距离矩阵不一致'
        p_raw=(np.count_nonzero(null>=observed[None,:]-1e-12,axis=0)+1)/(repetitions+1)
        assert np.allclose(joint['p_raw'],p_raw,atol=1e-12),'原始p与加一规则不一致'
        assert np.allclose(joint['p_adjusted'],_brute_stepdown(observed,null),atol=1e-12),'校正p与暴力逐步最大值不一致'
def test_stepdown_monotone_and_bounds():
    rng=np.random.default_rng(3);groups=[rng.uniform(0,360,12) for _ in range(5)]
    joint=compare_joint(groups,499,29)
    ranked=joint['p_adjusted'][np.argsort(-joint['statistic'],kind='stable')]
    assert np.all(np.diff(ranked)>=-1e-15),'校正p须沿降序逐步单调'
    assert np.all(joint['p_adjusted']>=joint['p_raw']-1e-15),'校正p不得小于原始p'
    assert joint['p_raw'].min()>=1/(499+1) and joint['p_adjusted'].max()<=1.0,'加一规则界限'
def test_deterministic_seed():
    rng=np.random.default_rng(5);groups=[rng.uniform(0,360,8) for _ in range(4)]
    a=compare_joint(groups,99,5);b=compare_joint(groups,99,5)
    assert np.array_equal(a['null_statistics'],b['null_statistics']) and np.array_equal(a['p_adjusted'],b['p_adjusted'])
def test_identical_groups_p_one():
    joint=compare_joint([np.zeros(5) for _ in range(3)],99,3)
    assert (joint['p_raw']==1.0).all() and (joint['p_adjusted']==1.0).all()
def test_capacity():
    assert estimate_peak_bytes(3200,32,999)<=MEMORY_CAP_BYTES,'32座×100条×999次须在容量内'
    try:compare_joint([np.zeros(250) for _ in range(32)],99,1);raise AssertionError('超出容量应拒绝')
    except ValueError as e:assert '超出容量' in str(e)
def test_validation():
    for groups,repetitions in [([np.zeros(4)]*2,99),([np.zeros(4)]*33,99),([np.zeros(4)]*3,98),([np.zeros(4)]*3,1000),([np.zeros(1)]*3,99),([np.zeros(251)]*3,99),([np.r_[np.zeros(3),360.0]]*3,99),([np.r_[np.zeros(3),np.nan]]*3,99)]:
        try:compare_joint(groups,repetitions,1);raise AssertionError(f'应拒绝:{repetitions}')
        except ValueError:pass
def test_two_group_study_unchanged():
    extreme=compare([0,0],[180,180],999,157)
    assert extreme['statistic']==4.0 and abs(extreme['p_value']-1/3)<0.06,'双组极端分割参考p=1/3'
    same=compare([0,180],[0,180],99,7)
    assert same['statistic']==0.0 and same['p_value']==1.0
if __name__=='__main__':
    for name,fn in list(globals().items()):
        if name.startswith('test_'):fn();print('ok',name)
    print('ALL JOINT ALGORITHM TESTS PASSED')
