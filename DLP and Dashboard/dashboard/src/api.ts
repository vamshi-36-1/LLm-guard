import type {Alert,Event,Metric} from './types';
const API=import.meta.env.VITE_DLP_API_URL || 'http://localhost:8001';
export async function health(){const r=await fetch(`${API}/health`);return r.json();}
export async function getMetrics():Promise<Metric[]>{const r=await fetch(`${API}/metrics`); const text=await r.text(); return text.split('\n').filter(x=>x&&!x.startsWith('#')).slice(0,8).map((line,i)=>({name:line.split('{')[0],value:Number(line.split(' ').at(-1)),unit:'count'}));}
export async function getAlerts():Promise<Alert[]>{return [];}
export async function getAudit():Promise<Event[]>{return [];}
export {API};
