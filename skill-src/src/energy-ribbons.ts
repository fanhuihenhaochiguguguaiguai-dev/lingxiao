import * as THREE from 'three/webgpu';
/** Several tapered ribbons in one mesh, following a supplied three-dimensional path. */
export class EnergyRibbons {
 readonly mesh:THREE.Mesh;private readonly positions:THREE.BufferAttribute;private readonly vertices:Float32Array;private readonly n:number;private readonly count:number;private readonly width:number;private readonly center=new THREE.Vector3();private readonly tangent=new THREE.Vector3();private readonly side=new THREE.Vector3();private readonly up=new THREE.Vector3();private readonly samples:THREE.Vector3[];
 constructor(options:{color:number;opacity:number;width:number;segments?:number;count?:number}){
  this.n=options.segments??48;this.count=options.count??4;this.width=options.width;this.samples=Array.from({length:this.n+1},()=>new THREE.Vector3());
  this.vertices=new Float32Array(this.count*(this.n+1)*2*3);const colors=new Float32Array(this.vertices.length),idx:number[]=[];
  for(let k=0;k<this.count;k++)for(let i=0;i<=this.n;i++){
   const u=i/this.n,brightness=Math.pow(Math.sin(Math.PI*u),.6)*(.65+.35*(k%2));const base=(k*(this.n+1)*2+i*2)*3;for(let j=0;j<2;j++){colors[base+j*3]=brightness;colors[base+j*3+1]=brightness;colors[base+j*3+2]=brightness}
   if(i<this.n){const a=k*(this.n+1)*2+i*2;idx.push(a,a+1,a+2,a+1,a+3,a+2)}
  }
  const geometry=new THREE.BufferGeometry();this.positions=new THREE.BufferAttribute(this.vertices,3);this.positions.setUsage(THREE.DynamicDrawUsage);geometry.setAttribute('position',this.positions);geometry.setAttribute('color',new THREE.BufferAttribute(colors,3));geometry.setIndex(idx);
  const material=new THREE.MeshBasicMaterial({color:options.color,vertexColors:true,transparent:true,opacity:options.opacity,blending:THREE.AdditiveBlending,depthWrite:false,side:THREE.DoubleSide});material.forceSinglePass=true;this.mesh=new THREE.Mesh(geometry,material);this.mesh.name='layered energy ribbons';this.mesh.frustumCulled=false;this.mesh.renderOrder=2;
 }
 update(sample:(u:number)=>THREE.Vector3,t:number,envelope:number){
  const n=this.n;for(let i=0;i<=n;i++)this.samples[i]!.copy(sample(i/n));
  for(let i=0;i<=n;i++){
   const u=i/n,baseCenter=this.samples[i]!;this.tangent.copy(this.samples[Math.min(n,i+1)]!).sub(this.samples[Math.max(0,i-1)]!).normalize();if(this.tangent.lengthSq()<.1)this.tangent.set(1,0,0);
   this.side.crossVectors(this.tangent,THREE.Object3D.DEFAULT_UP).normalize();if(this.side.lengthSq()<.1)this.side.set(0,0,1);this.up.crossVectors(this.side,this.tangent).normalize();
   for(let k=0;k<this.count;k++){
    const center=this.center.copy(baseCenter),phase=k*Math.PI*2/this.count+u*6-t*3,offset=.13*Math.sin(phase),width=this.width*Math.sin(Math.PI*u)*envelope*(.65+.35*Math.sin(phase*2+t));
    center.addScaledVector(this.side,offset).addScaledVector(this.up,.11*Math.cos(phase));const base=(k*(n+1)*2+i*2)*3;
    this.vertices[base]=center.x+this.up.x*width;this.vertices[base+1]=center.y+this.up.y*width;this.vertices[base+2]=center.z+this.up.z*width;
    this.vertices[base+3]=center.x-this.up.x*width;this.vertices[base+4]=center.y-this.up.y*width;this.vertices[base+5]=center.z-this.up.z*width;
   }
  }this.positions.needsUpdate=true;
 }
}
