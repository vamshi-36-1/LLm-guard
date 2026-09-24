import type {Metric} from '../types';
export function Metrics({metrics}:{metrics:Metric[]}){return <section><h2>Metrics</h2><div className="grid">{metrics.map((m,i)=><article className="card" key={i}><span>{m.name}</span><strong>{Number.isFinite(m.value)?m.value:0}</strong><small>{m.unit}</small></article>)}</div></section>}
