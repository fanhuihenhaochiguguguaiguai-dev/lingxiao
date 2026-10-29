import type {CastKind} from './instance-audio';
export interface AimState {pointer:number;kind:CastKind;x:number;y:number;dx:number;dy:number;cancelled:boolean;heldMs:number}
/** Pointer ownership is per finger. A synthetic click never duplicates pointer-up. */
export class SkillInput {
 private pointers=new Map<number,{button:HTMLButtonElement;startX:number;startY:number;state:AimState;at:number}>();
 readonly events:{kind:CastKind;phase:string;at:number}[]=[];
 constructor(private canCast:(kind:CastKind)=>boolean,private release:(kind:CastKind,aim:AimState|null)=>void,private preview:(state:AimState|null)=>void){
  const entries=[...document.querySelectorAll<HTMLButtonElement>('[data-cast]')].map(b=>[b.id,b.dataset.cast as CastKind] as const);
  for(const [id,kind] of entries){
   const button=document.getElementById(id) as HTMLButtonElement;let lastPointer=-Infinity;
   button.addEventListener('contextmenu',e=>e.preventDefault());
   button.addEventListener('pointerdown',e=>{if(e.button!==0||!this.canCast(kind)||[...this.pointers.values()].some(p=>p.button===button))return;e.preventDefault();lastPointer=performance.now();button.setPointerCapture(e.pointerId);const state={pointer:e.pointerId,kind,x:e.clientX,y:e.clientY,dx:0,dy:0,cancelled:false,heldMs:0};this.pointers.set(e.pointerId,{button,startX:e.clientX,startY:e.clientY,state,at:performance.now()});button.classList.add('aiming');this.record(kind,'aim');this.preview(state)});
   button.addEventListener('pointermove',e=>{const p=this.pointers.get(e.pointerId);if(!p)return;p.state={...p.state,x:e.clientX,y:e.clientY,dx:e.clientX-p.startX,dy:e.clientY-p.startY,heldMs:performance.now()-p.at};const zone=document.getElementById('cast-cancel')!.getBoundingClientRect();p.state.cancelled=Math.hypot(p.state.dx,p.state.dy)>175||(e.clientX>=zone.left&&e.clientX<=zone.right&&e.clientY>=zone.top&&e.clientY<=zone.bottom);button.classList.toggle('cancel-aim',p.state.cancelled);this.preview(p.state)});
   button.addEventListener('pointerup',e=>{const p=this.pointers.get(e.pointerId);if(!p)return;e.preventDefault();lastPointer=performance.now();this.pointers.delete(e.pointerId);button.classList.remove('aiming','cancel-aim');if(!p.state.cancelled&&this.canCast(kind)){this.record(kind,'release');this.release(kind,Math.hypot(p.state.dx,p.state.dy)>=8?p.state:null)}else this.record(kind,'cancel');this.showLatest()});
   for(const event of ['pointercancel','lostpointercapture'])button.addEventListener(event,e=>{const p=this.pointers.get((e as PointerEvent).pointerId);if(!p)return;this.pointers.delete((e as PointerEvent).pointerId);button.classList.remove('aiming','cancel-aim');this.record(kind,'cancel');this.showLatest()});
   button.addEventListener('click',e=>{if(e.detail!==0&&performance.now()-lastPointer<1500)return;if(e.detail===0&&this.canCast(kind)){this.record(kind,'click');this.release(kind,null)}});
  }
 }
 private record(kind:CastKind,phase:string){this.events.push({kind,phase,at:performance.now()});if(this.events.length>128)this.events.shift()}
 private showLatest(){this.preview([...this.pointers.values()].at(-1)?.state||null)}
 cancelAll(){for(const [id,p] of this.pointers){p.button.classList.remove('aiming','cancel-aim');this.record(p.state.kind,'cancel');if(p.button.hasPointerCapture(id))p.button.releasePointerCapture(id)}this.pointers.clear();this.preview(null)}
 snapshot(){return {pointers:[...this.pointers.values()].map(p=>({...p.state,heldMs:performance.now()-p.at})),events:[...this.events]}}
}
