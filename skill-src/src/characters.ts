import { GLTFLoader, type GLTF } from 'three/addons/loaders/GLTFLoader.js';
import { motionProfiles, type MotionProfile } from './motion-profile';

export const YUELI_ASSET_REVISION='98bbd76b5e6d';
export type CharacterId = 'lingyuan' | 'yueli';
export interface CharacterDefinition { name:string; url:string; hasSkills:boolean; status:string; motion:Readonly<MotionProfile> }
export const characters:Record<CharacterId,CharacterDefinition> = {
  lingyuan:{name:'凌渊',url:'../lingyuan-lod1.glb',hasSkills:true,status:'三技能展示',motion:motionProfiles.lingyuan},
  yueli:{name:'月璃',url:'../yueli-study.glb?rev='+YUELI_ASSET_REVISION,hasSkills:false,status:'绑定与动态工作稿 · 美术未验收',motion:motionProfiles.yueli},
};

// Retain a single loaded asset per character and share in-flight requests.
export class CharacterAssets {
  private readonly loader = new GLTFLoader();
  private readonly loaded = new Map<CharacterId,GLTF>();
  private readonly pending = new Map<CharacterId,Promise<GLTF>>();
  status(){return {loaded:[...this.loaded.keys()],pending:[...this.pending.keys()]}}
  load(id:CharacterId):Promise<GLTF> {
    const existing=this.loaded.get(id); if(existing)return Promise.resolve(existing);
    const pending=this.pending.get(id); if(pending)return pending;
    const request=this.loader.loadAsync(characters[id].url).then(asset=>{
      this.loaded.set(id,asset);return asset;
    }).finally(()=>this.pending.delete(id));
    this.pending.set(id,request);return request;
  }
}
