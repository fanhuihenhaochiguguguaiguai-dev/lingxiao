import { GLTFLoader, type GLTF } from 'three/addons/loaders/GLTFLoader.js';

export type CharacterId = 'lingyuan' | 'yueli';
export interface CharacterDefinition { name:string; url:string; hasSkills:boolean; status:string }
export const characters:Record<CharacterId,CharacterDefinition> = {
  lingyuan:{name:'凌渊',url:'../lingyuan-lod1.glb',hasSkills:true,status:'三技能展示'},
  yueli:{name:'月璃',url:'../yueli-study.glb',hasSkills:false,status:'绑定与动态工作稿 · 美术未验收'},
};

// Retain a single loaded asset per character and share in-flight requests.
export class CharacterAssets {
  private readonly loader = new GLTFLoader();
  private readonly loaded = new Map<CharacterId,GLTF>();
  private readonly pending = new Map<CharacterId,Promise<GLTF>>();
  load(id:CharacterId):Promise<GLTF> {
    const existing=this.loaded.get(id); if(existing)return Promise.resolve(existing);
    const pending=this.pending.get(id); if(pending)return pending;
    const request=this.loader.loadAsync(characters[id].url).then(asset=>{
      this.loaded.set(id,asset);return asset;
    }).finally(()=>this.pending.delete(id));
    this.pending.set(id,request);return request;
  }
}
