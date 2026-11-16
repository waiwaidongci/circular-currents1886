import{request}from './client';import type{Mooring}from '../types/domain';export const list=()=>request<Mooring[]>('/moorings');
export const create=(data:unknown)=>request<Mooring>('/moorings',{method:'POST',body:JSON.stringify(data)});
export const patch=(id:number,data:unknown)=>request<Mooring>('/moorings/'+id,{method:'PATCH',body:JSON.stringify(data)});
