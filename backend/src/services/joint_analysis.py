from src.services.circular_algorithm import summarize
from src.services.joint_algorithm import compare_joint,pair_count
from src.utils.fingerprint import fingerprint
DEFINITION='V-energy per pair: 2 mean cross chord distance - mean within A (diagonal included) - mean within B; one joint label permutation across all groups per repetition with +1 correction'
CORRECTION='Westfall-Young step-down maxT: pairs ordered by observed statistic descending; adjusted p from successive maxima of the joint null distribution with +1 rule, monotone along the step-down order'
def analyze_joint(moorings,config):
    groups=[];snapshot=[]
    for mooring in moorings:
        rows=sorted(mooring['rows'],key=lambda r:r['code'])
        groups.append([r['bearing'] for r in rows])
        snapshot.append({'mooring_id':mooring['mooring_id'],'code':mooring['code'],'name':mooring['name'],'rows':rows})
    joint=compare_joint(groups,config['permutations'],config['seed'])
    k=len(moorings);first=joint['first'];second=joint['second']
    pairs=[]
    for m in range(pair_count(k)):
        i,j=int(first[m]),int(second[m])
        pairs.append({'i':i,'j':j,'mooring_a_id':moorings[i]['mooring_id'],'mooring_b_id':moorings[j]['mooring_id'],'mooring_a':moorings[i]['code'],'mooring_b':moorings[j]['code'],'statistic':float(joint['statistic'][m]),'p_raw':float(joint['p_raw'][m]),'p_adjusted':float(joint['p_adjusted'][m]),'rank':int(joint['rank'][m]),'extreme':int(joint['extreme'][m])})
    result={'kind':'joint','groups':[{'mooring_id':m['mooring_id'],'code':m['code'],'name':m['name'],**summarize(g)} for m,g in zip(moorings,groups)],'pairs':pairs}
    result['joint']={'permutations':joint['permutations'],'seed':joint['seed'],'group_count':k,'pair_count':len(pairs),'definition':DEFINITION,'correction':CORRECTION}
    result['input_snapshot']={'moorings':snapshot,'config':config}
    result['fingerprint']=fingerprint({'algorithm':'circular-joint-energy-v1','moorings':snapshot,'config':config})
    result['interpretation']='多浮标联合比较：每次统一重分全部采样标签并保留各组大小，所有浮标对共享同一次置换；逐步最大值校正后的p不小于原始p，逐对比较后挑最小原始p会夸大差异。小p不代表差异大小、成因或航行风险；交换性要求观测独立，同浮标连续时间自相关可能破坏置换前提。'
    return result,joint['null_statistics'].tolist()
