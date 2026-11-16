export interface User{id:number;email:string;name:string;role:'admin'|'analyst'|'viewer'}
export interface Survey{id:number;code:string;name:string;period:string;description:string}
export interface Mooring{id:number;code:string;name:string;description:string}
export interface Bearing{id:number;survey_id:number;mooring_id:number;code:string;bearing:number;observed_at:string}
export interface Histogram{lower:number;upper:number;count:number;proportion:number;fitted_probability:number|null}
export interface CircularGroup{n:number;mean_bearing:number|null;resultant:number;second_resultant:number;circular_variance:number;kappa:number|null;fit_status:string;histogram:Histogram[];warning:string}
export interface Energy{statistic:number;p_value:number;extreme:number;permutations:number;seed:number;null_statistics:number[];null_quantiles:number[];definition:string}
export interface Run{id:number;name:string;survey_id:number;mooring_a_id:number;mooring_b_id:number;status:string;permutations:number;seed:number;result:{a?:CircularGroup;b?:CircularGroup;energy?:Energy;fingerprint?:string;interpretation?:string};error:string;created_at:string}
export interface JointPair{i:number;j:number;mooring_a_id:number;mooring_b_id:number;mooring_a:string;mooring_b:string;statistic:number;p_raw:number;p_adjusted:number;rank:number;extreme:number}
export interface JointGroup extends CircularGroup{mooring_id:number;code:string;name:string}
export interface JointMeta{permutations:number;seed:number;group_count:number;pair_count:number;definition:string;correction:string}
export interface JointRun{id:number;name:string;survey_id:number;mooring_ids:number[];status:string;permutations:number;seed:number;result:{kind?:string;groups?:JointGroup[];pairs?:JointPair[];joint?:JointMeta;input_snapshot?:unknown;fingerprint?:string;interpretation?:string};null_statistics?:number[][];error:string;created_at:string}
export interface Note{id:number;title:string;run_id:number|null;joint_run_id:number|null;interpretation:string;action:string;status:string;approved_by:string;review_comment:string}
export interface Audit{id:number;actor:string;action:string;target:string;created_at:string}
