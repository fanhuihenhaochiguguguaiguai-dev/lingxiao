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
type HitShape={start:number;end:number;radius:(age:number)=>number;point:(effect:SkillEffect)=>THREE.Vector3;area?:boolean;repeat?:number;slow?:number};
export interface SkillDefinition {
 character:'lingyuan'|'yueli';slot:number;duration:number;audioStyle:0|1|2|3;damage:number;
 cues:ReadonlyArray<readonly [number,string]>;
 create:(root:THREE.Group)=>SkillEffect;
 update:(effect:SkillEffect,age:number,id:number)=>void;
 hit:HitShape;
 hitAudio?:{file:string;gain:number};
 concurrency?:(effect:SkillEffect,count:number)=>void;
 /** These two effects own dynamic resources but borrow shared immutable geometry. */
 dispose?:(effect:SkillEffect)=>void;
}
const layers={dragon:true,circle:true,crystals:true,beams:true,chains:true,particles:true};
const legacy=(slot:number)=>tracks[slot].map((c,n)=>[c.t,`legacy:${n}`] as const);
const point=(x:number,y:number,z:number)=>()=>new THREE.Vector3(x,y,z);
const regular=(fx:SkillEffect,t:number)=>{(fx as DragonEffect|StarVortex|MoonFrost).update(t,true)};
export const skillRegistry:Record<CastKind,SkillDefinition>={
 'lingyuan-1':{character:'lingyuan',slot:1,duration:4.4,audioStyle:0,damage:135,cues:legacy(1),create:r=>new DragonEffect(r),update:regular,
  hit:{start:.95,end:3.2,radius:()=>1,point:e=>{const f=e as DragonEffect;return f.group.parent!.worldToLocal(f.head.getWorldPosition(new THREE.Vector3()))},area:false},hitAudio:{file:'blade_03',gain:.35}},
 'lingyuan-2':{character:'lingyuan',slot:2,duration:6.4,audioStyle:0,damage:95,cues:legacy(2),create:r=>new BindStar(r),update:(e,t)=>(e as BindStar).update(t,true,layers),
  hit:{start:1,end:3,radius:()=>3,point:point(0,1,0)},hitAudio:{file:'chain_02',gain:.32}},
 'lingyuan-3':{character:'lingyuan',slot:3,duration:7.4,audioStyle:0,damage:260,cues:legacy(3),create:r=>new StarVortex(r),update:regular,
  hit:{start:4.85,end:5.85,radius:t=>.3+3*1.15*THREE.MathUtils.smoothstep(t,4.85,5.8),point:point(0,.1,0),area:true},hitAudio:{file:'stones_03',gain:.50}},
 'yueli-1':{character:'yueli',slot:1,duration:4.4,audioStyle:1,damage:115,cues:[[0,'cast'],[.32,'moon'],[.66,'crystal'],[2.12,'burst'],[2.6,'field'],[3.6,'dissolve']],create:r=>new MoonFrost(r),update:regular,
  hit:{start:.85,end:2.8,radius:()=>.5,point:e=>new THREE.Vector3((e as MoonFrost).sample().crescentX,.6,0)}},
 'yueli-2':{character:'yueli',slot:2,duration:8.6,audioStyle:2,damage:55,cues:[[0,'cast'],[.42,'moon'],[.95,'crystal'],[1.45,'burst'],[1.9,'field'],[5.1,'field:tail'],[7,'dissolve']],create:r=>new MoonTide(r),update:(e,t,id)=>(e as MoonTide).update(t,true,id),concurrency:(e,n)=>(e as MoonTide).setConcurrency(n),dispose:e=>(e as MoonTide).dispose(),
  hit:{start:1.45,end:7,radius:t=>3.15*THREE.MathUtils.smoothstep(t,1.1,2.2),point:point(2.4,.6,0),area:true,repeat:1,slow:.55}},
 'yueli-3':{character:'yueli',slot:3,duration:11.4,audioStyle:3,damage:100,cues:[[0,'cast'],[.45,'moon'],[.9,'dragon'],[2.75,'crystal'],[3.8,'burst'],[4.4,'field'],[7.7,'field:tail'],[9.5,'dissolve']],create:r=>new Moonfall(r),update:(e,t,id)=>(e as Moonfall).update(t,true,id),concurrency:(e,n)=>(e as Moonfall).setConcurrency(n),dispose:e=>(e as Moonfall).dispose(),
  hit:{start:3.8,end:9.4,radius:()=>4.5,point:point(1.5,.6,0),area:true,repeat:1,slow:.55}},
};
