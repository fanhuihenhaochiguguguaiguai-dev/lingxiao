/** Authoritative local combat state. Rendering/DOM events cannot settle damage. */
export type Fighter='lingyuan'|'yueli';
export type CombatMode='practice'|'duel';
export interface Point3 {x:number;y:number;z:number}
export interface CombatUnit {
 id:string;team:number;character:Fighter|'target';hp:number;maxHp:number;alive:boolean;life:number;
 position:Point3;radius:number;halfHeight:number;hitFlash:number;deadFor:number;slow:number;
 slows:Map<string,{until:number;factor:number}>;
}
export interface DamageToken {id:string;source:string;sourceLife:number;round:number;character:Fighter;kind:string;damage:number;expires:number}
export interface DamageEvent {round:number;attack:string;source:string;target:string;targetLife:number;kind:string;tick:number;damage:number;hp:number;killed:boolean;time:number;region?:string;contactAge?:number}
export const fighterHealth:Record<Fighter,number>={lingyuan:1000,yueli:850};
export const basicProfiles={
 lingyuan:{interval:.72,windup:.23,active:.16,recovery:.33,damage:88,range:2.1,speed:0},
 yueli:{interval:.84,windup:.28,active:.12,recovery:.44,damage:66,range:7,speed:8.5},
} as const;
export class CombatState {
 readonly units=new Map<string,CombatUnit>();readonly events:DamageEvent[]=[];
 mode:CombatMode='practice';round=0;clock=0;winner:string|null=null;
 private ledger=new Map<string,number>();
 constructor(){this.add('player',1,'lingyuan');this.add('opponent',2,'yueli');for(let i=0;i<3;i++)this.add('target-'+i,0,'target');this.reset()}
 private add(id:string,team:number,character:CombatUnit['character']){const hp=character==='target'?3000:fighterHealth[character];this.units.set(id,{id,team,character,hp,maxHp:hp,alive:true,life:0,position:{x:0,y:.8,z:0},radius:character==='target'?.45:.36,halfHeight:character==='target'?.20:.49,hitFlash:0,deadFor:0,slow:1,slows:new Map()})}
 unit(id:string){const unit=this.units.get(id);if(!unit)throw Error('Unknown combat unit: '+id);return unit}
 reset(mode=this.mode,character=this.unit('player').character as Fighter){
  this.mode=mode;this.round++;this.clock=0;this.winner=null;this.events.length=0;this.ledger.clear();
  for(const u of this.units.values()){if(u.id==='player')u.character=character;if(u.id==='opponent')u.character=character==='lingyuan'?'yueli':'lingyuan';u.maxHp=u.character==='target'?3000:fighterHealth[u.character];u.hp=u.maxHp;u.alive=true;u.life++;u.hitFlash=u.deadFor=0;u.slow=1;u.slows.clear()}
 }
 replacePlayer(character:Fighter){const u=this.unit('player');u.character=character;u.maxHp=fighterHealth[character];u.hp=u.maxHp;u.life++;u.alive=true;u.hitFlash=u.deadFor=0;u.slow=1;u.slows.clear()}
 canAct(id:string){return this.unit(id).alive&&(this.mode!=='duel'||!this.winner)}
 token(id:string,source:string,kind:string,damage:number):DamageToken|null{const u=this.unit(source);return this.canAct(source)?{id,source,sourceLife:u.life,round:this.round,character:u.character as Fighter,kind,damage,expires:this.clock+20}:null}
 valid(t:DamageToken){const source=this.units.get(t.source);return t.expires>=this.clock&&t.round===this.round&&source?.life===t.sourceLife&&this.canAct(t.source)}
 enemies(source:string){const s=this.unit(source);return [...this.units.values()].filter(u=>u.id!==source&&u.alive&&(this.mode==='practice'?u.character==='target'&&source==='player':u.character!=='target'&&u.team!==s.team))}
 damage(t:DamageToken,targetId:string,tick=0,slow=1){
  if(!this.valid(t)||!Number.isFinite(t.damage)||t.damage<=0||!Number.isInteger(tick)||tick<0)return null;
  const target=this.units.get(targetId);if(!target||!this.enemies(t.source).includes(target))return null;
  const key=[t.round,t.id,t.source,t.sourceLife,target.id,target.life,tick].join('|');if(this.ledger.has(key))return null;
  this.ledger.set(key,this.clock);const amount=Math.min(target.hp,t.damage);target.hp=Math.max(0,target.hp-amount);target.alive=target.hp>0;target.hitFlash=.22;
  if(slow<1){target.slows.set(t.id,{until:this.clock+1.2,factor:Math.max(.15,slow)});target.slow=Math.min(target.slow,slow)}
  const event:DamageEvent={round:this.round,attack:t.id,source:t.source,target:target.id,targetLife:target.life,kind:t.kind,tick,damage:amount,hp:target.hp,killed:!target.alive,time:this.clock};this.events.push(event);if(this.events.length>512)this.events.shift();
  if(!target.alive&&this.mode==='duel')this.winner=t.source;
  return event;
 }
 update(dt:number){this.clock+=dt;for(const u of this.units.values()){u.hitFlash=Math.max(0,u.hitFlash-dt);if(!u.alive)u.deadFor+=dt;for(const [id,s] of u.slows)if(s.until<=this.clock)u.slows.delete(id);u.slow=Math.min(1,...[...u.slows.values()].map(s=>s.factor))}for(const [key,time] of this.ledger)if(this.clock-time>30)this.ledger.delete(key)}
 snapshot(){return {mode:this.mode,round:this.round,clock:this.clock,winner:this.winner,units:[...this.units.values()].map(({slows,...u})=>({...u,position:{...u.position}})),events:[...this.events],ledgerSize:this.ledger.size}}
}
