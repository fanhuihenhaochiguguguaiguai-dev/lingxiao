/** Character-specific motion values. The solver still measures actual joint lengths. */
export interface MotionProfile {
 id:string; walkStride:number; runStride:number; stance:number; runStance:number;
 walkLift:number; runLift:number; armSwing:number; runArmSwing:number;
 pelvisDrop:number; breath:number; headSway:number; secondaryLag:number;
 castStyle:'spear'|'lunar';
}
export const motionProfiles:Record<'lingyuan'|'yueli',Readonly<MotionProfile>>={
 lingyuan:Object.freeze({id:'lingyuan',walkStride:.82,runStride:1.32,stance:.62,runStance:.38,walkLift:.065,runLift:.185,armSwing:.16,runArmSwing:.41,pelvisDrop:.028,breath:.0015,headSway:.018,secondaryLag:.025,castStyle:'spear'}),
 yueli:Object.freeze({id:'yueli',walkStride:.72,runStride:1.12,stance:.62,runStance:.38,walkLift:.065,runLift:.185,armSwing:.16,runArmSwing:.41,pelvisDrop:.028,breath:.0015,headSway:.018,secondaryLag:.025,castStyle:'lunar'}),
};
