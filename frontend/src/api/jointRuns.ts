import{request}from './client';import type{JointRun}from '../types/domain';export const list=()=>request<JointRun[]>('/joint-runs');
export const detail=(id:number)=>request<JointRun>('/joint-runs/'+id);
export const create=(data:unknown)=>request<JointRun>('/joint-runs',{method:'POST',body:JSON.stringify(data)});
