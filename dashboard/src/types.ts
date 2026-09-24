export type Metric={name:string;value:number;unit:string};
export type Alert={id:string;severity:'low'|'medium'|'high'|'critical';message:string;timestamp:string};
export type Event={timestamp:string;event_type:string;direction?:string;entity_types?:string[];count?:number;allowed?:boolean;blocked_entities?:string[]};
