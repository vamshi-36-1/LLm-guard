import type {Alert} from '../types';
export function Alerts({alerts}:{alerts:Alert[]}){return <section><h2>Alerts</h2>{alerts.length===0?<p>No active alerts.</p>:alerts.map(a=><div className={`alert ${a.severity}`} key={a.id}><b>{a.severity.toUpperCase()}</b> {a.message}<small>{a.timestamp}</small></div>)}</section>}
