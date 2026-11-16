import numpy as np
MIN_GROUPS=3
MAX_GROUPS=32
MIN_GROUP_SIZE=2
MAX_GROUP_SIZE=250
MIN_PERMUTATIONS=99
MAX_PERMUTATIONS=999
MEMORY_CAP_BYTES=256*1024**2
TOLERANCE=1e-12
_CHORD_BLOCK=256
_BATCH_PERMUTATIONS=16
_BASE_OVERHEAD_BYTES=64*1024**2
def pair_count(groups):return groups*(groups-1)//2
def estimate_peak_bytes(total,groups,repetitions):
    pairs=pair_count(groups);distance=8*total*total
    build=48*_CHORD_BLOCK*total
    batch=2*8*total*groups*_BATCH_PERMUTATIONS
    null=64*repetitions*pairs
    return _BASE_OVERHEAD_BYTES+distance+max(build,batch)+null
def check_capacity(sizes,repetitions):
    estimate=estimate_peak_bytes(sum(sizes),len(sizes),repetitions)
    if estimate>MEMORY_CAP_BYTES:raise ValueError(f'超出容量：估计峰值内存{estimate/1024**2:.0f}MB，超过256MB上限；请减少浮标数、每组样本量或置换次数')
def _validate(groups,repetitions):
    if not MIN_GROUPS<=len(groups)<=MAX_GROUPS:raise ValueError(f'联合研究须{MIN_GROUPS}–{MAX_GROUPS}座浮标')
    sizes=np.array([len(g) for g in groups])
    if len(sizes)==0 or sizes.min()<MIN_GROUP_SIZE or sizes.max()>MAX_GROUP_SIZE:raise ValueError('每组须有2–250个观测')
    values=np.concatenate(groups)
    if not np.isfinite(values).all() or ((values<0)|(values>=360)).any():raise ValueError('角度须在[0,360)')
    if not MIN_PERMUTATIONS<=repetitions<=MAX_PERMUTATIONS:raise ValueError('置换次数无效')
    check_capacity(sizes,repetitions)
    return values,sizes
def _chord_matrix(values):
    xy=np.column_stack([np.cos(np.deg2rad(values)),np.sin(np.deg2rad(values))])
    n=len(values);distance=np.empty((n,n))
    for lo in range(0,n,_CHORD_BLOCK):
        diff=xy[lo:lo+_CHORD_BLOCK,None,:]-xy[None,:,:]
        distance[lo:lo+_CHORD_BLOCK]=np.sqrt(np.maximum(0.0,(diff*diff).sum(axis=2)))
    return distance
def _statistics(block,sizes,first,second):
    cross=block[...,first,second];within_a=block[...,first,first];within_b=block[...,second,second]
    n_a=sizes[first].astype(float);n_b=sizes[second].astype(float)
    return np.maximum(0.0,2*cross/(n_a*n_b)-within_a/n_a**2-within_b/n_b**2)
def compare_joint(groups,repetitions,seed):
    groups=[np.asarray(g,dtype=float) for g in groups]
    values,sizes=_validate(groups,repetitions)
    k=len(groups);m=pair_count(k);n=len(values)
    first,second=np.triu_indices(k,1)
    distance=_chord_matrix(values)
    def block_sums(label_rows):
        batch=len(label_rows)
        onehot=np.zeros((batch,n,k))
        onehot[np.arange(batch)[:,None],np.arange(n)[None,:],label_rows]=1.0
        crossed=distance@onehot.transpose(1,0,2).reshape(n,batch*k)
        return np.matmul(onehot.transpose(0,2,1),crossed.reshape(n,batch,k).transpose(1,0,2))
    labels=np.repeat(np.arange(k),sizes)
    observed=_statistics(block_sums(labels[None,:])[0],sizes,first,second)
    rng=np.random.default_rng(seed);null=np.empty((repetitions,m))
    for lo in range(0,repetitions,_BATCH_PERMUTATIONS):
        perms=np.array([rng.permutation(labels) for _ in range(min(_BATCH_PERMUTATIONS,repetitions-lo))])
        null[lo:lo+len(perms)]=_statistics(block_sums(perms),sizes,first,second)
    order=np.argsort(-observed,kind='stable');ranked=observed[order]
    successive=np.maximum.accumulate(null[:,order][:,::-1],axis=1)[:,::-1]
    stepdown=(np.count_nonzero(successive>=ranked[None,:]-TOLERANCE,axis=0)+1)/(repetitions+1)
    stepdown=np.maximum.accumulate(stepdown)
    p_adjusted=np.empty(m);p_adjusted[order]=stepdown
    extreme=np.count_nonzero(null>=observed[None,:]-TOLERANCE,axis=0)
    rank=np.empty(m,dtype=int);rank[order]=np.arange(1,m+1)
    return {'first':first,'second':second,'statistic':observed,'p_raw':(extreme+1)/(repetitions+1),'p_adjusted':p_adjusted,'rank':rank,'extreme':extreme,'null_statistics':null,'permutations':repetitions,'seed':seed,'group_sizes':sizes}
