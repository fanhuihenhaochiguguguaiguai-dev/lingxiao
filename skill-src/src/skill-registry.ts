import * as THREE from 'three/webgpu';
import { DragonEffect } from './dragon';
import { BindStar } from './bind-star';
import { StarVortex } from './star-vortex';
import { MoonFrost } from './moon-frost';
import { MoonTide } from './moon-tide';
import { Moonfall } from './moonfall';
import { tracks } from './skill-audio';
import type { CastKind } from './instance-audio';

export type SkillEffect=DragonEffect|BindStar|StarVortex|MoonFrost|MoonTide|Moonfall;
type HitTiming={start:number;end:number;repeat?:number;slow?:number};
export interface SkillDefinition {
 character:'lingyuan'|'yueli';slot:number;duration:number;audioStyle:0|1|2|3;damage:number;
 cues:ReadonlyArray<readonly [number,string]>;
 create:(root:THREE.Group)=>SkillEffect;
 update:(effect:SkillEffect,age:number,id:number)=>void;
 hit:HitTiming;
 aim:{shape:'direction'|'field';reach:number;radius:number};
 action:{basicCancel:number;gesture:number;moveScale:number};
 hitAudio?:{file:string;gain:number};
 concurrency?:(effect:SkillEffect,count:number)=>void;
 /** These two effects own dynamic resources but borrow shared immutable geometry. */
 dispose?:(effect:SkillEffect)=>void;
}
const layers={dragon:true,circle:true,crystals:true,beams:true,chains:true,particles:true};
const legacy=(slot:number)=>tracks[slot].map((c,n)=>[c.t,`legacy:${n}`] as const);
const regular=(fx:SkillEffect,t:number)=>{(fx as DragonEffect|StarVortex|MoonFrost).update(t,true)};
export const skillRegistry:Record<CastKind,SkillDefinition>={
 'lingyuan-1':{action:{basicCancel:1.75,gesture:3.3,moveScale:1},aim:{shape:'direction',reach:4.3,radius:.45},character:'lingyuan',slot:1,duration:4.4,audioStyle:0,damage:135,cues:legacy(1),create:r=>new DragonEffect(r),update:regular,
  hit:{start:.95,end:3.65},hitAudio:{file:'blade_03',gain:.35}},
 'lingyuan-2':{action:{basicCancel:0.95,gesture:2,moveScale:1},aim:{shape:'field',reach:0,radius:3.03},character:'lingyuan',slot:2,duration:6.4,audioStyle:0,damage:95,cues:legacy(2),create:r=>new BindStar(r),update:(e,t)=>(e as BindStar).update(t,true,layers),
  hit:{start:1,end:5.45},hitAudio:{file:'chain_02',gain:.32}},
 'lingyuan-3':{action:{basicCancel:5.3,gesture:6.5,moveScale:0.7},aim:{shape:'field',reach:0,radius:3.75},character:'lingyuan',slot:3,duration:7.4,audioStyle:0,damage:260,cues:legacy(3),create:r=>new StarVortex(r),update:regular,
  hit:{start:1.1,end:5.85},hitAudio:{file:'stones_03',gain:.50}},
 'yueli-1':{action:{basicCancel:0.85,gesture:1.8,moveScale:1},aim:{shape:'direction',reach:4.1,radius:.8},character:'yueli',slot:1,duration:4.4,audioStyle:1,damage:115,cues:[[0,'cast'],[.32,'moon'],[.66,'crystal'],[2.12,'burst'],[2.6,'field'],[3.6,'dissolve']],create:r=>new MoonFrost(r),update:regular,
  hit:{start:.85,end:3.3}},
 'yueli-2':{action:{basicCancel:1.45,gesture:1.8,moveScale:1},aim:{shape:'field',reach:2.4,radius:3.1},character:'yueli',slot:2,duration:8.6,audioStyle:2,damage:55,cues:[[0,'cast'],[.42,'moon'],[.95,'crystal'],[1.45,'burst'],[1.9,'field'],[5.1,'field:tail'],[7,'dissolve']],create:r=>new MoonTide(r),update:(e,t,id)=>(e as MoonTide).update(t,true,id),concurrency:(e,n)=>(e as MoonTide).setConcurrency(n),dispose:e=>(e as MoonTide).dispose(),
  hit:{start:1.45,end:7,repeat:1,slow:.55}},
 'yueli-3':{action:{basicCancel:4.4,gesture:2.6,moveScale:0.7},aim:{shape:'field',reach:1.5,radius:3.95},character:'yueli',slot:3,duration:11.4,audioStyle:3,damage:100,cues:[[0,'cast'],[.45,'moon'],[.9,'dragon'],[2.75,'crystal'],[3.8,'burst'],[4.4,'field'],[7.7,'field:tail'],[9.5,'dissolve']],create:r=>new Moonfall(r),update:(e,t,id)=>(e as Moonfall).update(t,true,id),concurrency:(e,n)=>(e as Moonfall).setConcurrency(n),dispose:e=>(e as Moonfall).dispose(),
  hit:{start:1.65,end:9.4,repeat:1,slow:.55}},
};
