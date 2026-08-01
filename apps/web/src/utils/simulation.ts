import type { Point } from '../types/economic'

export type ShockInput={baselineGdp:number|null|undefined;sectorValue:number|null|undefined;shockRate:number}
export type SectorShockInput={baselineGdp:number|null|undefined;affectedSectorValue:number|null|undefined;shockRate:number}
export type ShockResult={directLoss:number;simulatedGdp:number;directImpactPercentage:number;remainingSectorValue:number;unaffectedGdp:number;affectedSectorRemainingValue:number;unaffectedEconomyValue:number}

export function calculateSectorShock({baselineGdp,affectedSectorValue,shockRate}:SectorShockInput):ShockResult{
 if(baselineGdp==null||affectedSectorValue==null)throw new TypeError('Required economic value is missing')
 if(!Number.isFinite(baselineGdp)||!Number.isFinite(affectedSectorValue)||!Number.isFinite(shockRate))throw new TypeError('Values must be finite')
 if(baselineGdp<=0)throw new RangeError('Activity-side GDP must be greater than zero')
 if(affectedSectorValue<0)throw new RangeError('Sector value must not be negative')
 if(affectedSectorValue>baselineGdp)throw new RangeError('Sector value exceeds activity-side GDP')
 if(shockRate<0||shockRate>1)throw new RangeError('Shock rate must be between zero and one')
 const directLoss=affectedSectorValue*shockRate
 const affectedSectorRemainingValue=affectedSectorValue-directLoss
 const unaffectedEconomyValue=baselineGdp-affectedSectorValue
 return {directLoss,simulatedGdp:baselineGdp-directLoss,directImpactPercentage:directLoss/baselineGdp*100,remainingSectorValue:affectedSectorRemainingValue,unaffectedGdp:unaffectedEconomyValue,affectedSectorRemainingValue,unaffectedEconomyValue}
}

export function calculateSingleSectorShock({baselineGdp,sectorValue,shockRate}:ShockInput):ShockResult{return calculateSectorShock({baselineGdp,affectedSectorValue:sectorValue,shockRate})}

export type CompensationResult={targetSectorValue:number;directLossToCompensate:number;requiredAdditionalValue:number;requiredGrowthPercentage:number;targetValueAfterCompensation:number;status:'calculated';warnings:string[]}
export function calculateRequiredCompensationGrowth({directLoss,targetSectorValue}:{directLoss:number|null|undefined;targetSectorValue:number|null|undefined}):CompensationResult{
 if(directLoss==null||targetSectorValue==null)throw new TypeError('Required economic value is missing')
 if(!Number.isFinite(directLoss)||!Number.isFinite(targetSectorValue))throw new TypeError('Values must be finite')
 if(directLoss<0)throw new RangeError('Direct loss must not be negative')
 if(targetSectorValue<=0)throw new RangeError('Target sector value must be greater than zero')
 const requiredGrowthPercentage=directLoss/targetSectorValue*100
 const targetValueAfterCompensation=targetSectorValue+directLoss
 if(!Number.isFinite(requiredGrowthPercentage)||!Number.isFinite(targetValueAfterCompensation))throw new RangeError('Compensation result must be finite')
 return {targetSectorValue,directLossToCompensate:directLoss,requiredAdditionalValue:directLoss,requiredGrowthPercentage,targetValueAfterCompensation,status:'calculated',warnings:[]}
}

export type Allocation={code:string;share:number;targetSectorValue:number|null|undefined}
export function calculateSharedCompensation(directLoss:number,allocations:Allocation[]){
 if(!allocations.length)throw new RangeError('At least one target sector is required')
 const total=allocations.reduce((sum,item)=>sum+item.share,0)
 if(!Number.isFinite(total)||Math.abs(total-100)>0.01)throw new RangeError('Allocation total must equal 100%')
 return allocations.map(item=>{if(!Number.isFinite(item.share)||item.share<0||item.share>100)throw new RangeError('Allocation share must be between zero and 100%');const allocatedLoss=directLoss*item.share/100;return {code:item.code,allocationShare:item.share,allocatedLoss,...calculateRequiredCompensationGrowth({directLoss:allocatedLoss,targetSectorValue:item.targetSectorValue})}})
}

export const hierarchyParents:Record<string,string|undefined>={
 agriculture_forestry:'primary_sector',livestock_hunting:'primary_sector',fishing:'primary_sector',
 extractive_activities:'secondary_sector',oil_gas_extraction:'extractive_activities',non_oil_extractive_activities:'extractive_activities',metallic_mineral_extraction:'non_oil_extractive_activities',snim_iron:'metallic_mineral_extraction',gold_copper:'metallic_mineral_extraction',other_extractive_activities:'non_oil_extractive_activities',
 manufacturing:'secondary_sector',manufacturing_excluding_water_electricity:'manufacturing',water_electricity:'manufacturing',construction_public_works:'secondary_sector',
 transport_information_communication:'tertiary_sector',transport:'transport_information_communication',information_communication:'transport_information_communication',commerce:'tertiary_sector',other_services:'tertiary_sector',public_administration:'tertiary_sector',
}
function ancestors(code:string){const result=new Set<string>();let current=hierarchyParents[code];while(current){result.add(current);current=hierarchyParents[current]}return result}
export function hasHierarchyOverlap(first:string,second:string){return first===second||ancestors(first).has(second)||ancestors(second).has(first)}
export function targetConflict(affected:string,existing:string[],candidate:string){if(hasHierarchyOverlap(affected,candidate))return 'affected-overlap';if(existing.some(code=>hasHierarchyOverlap(code,candidate)))return 'target-overlap';return null}

export type HistoricalEvidence={averageGrowth:number|null;maximumGrowth:number|null;latestGrowth:number|null;volatility:number|null;completeness:number;observationCount:number;growthCount:number}
export function historicalEvidence(points:Point[]):HistoricalEvidence{
 const ordered=[...points].sort((a,b)=>a.year-b.year);const valid=ordered.filter(point=>point.value!=null);const growth=ordered.slice(1).flatMap((point,index)=>{const previous=ordered[index];return point.year===previous.year+1&&point.value!=null&&previous.value!=null&&previous.value!==0?[(point.value-previous.value)/Math.abs(previous.value)*100]:[]})
 const averageGrowth=growth.length?growth.reduce((sum,value)=>sum+value,0)/growth.length:null;const maximumGrowth=growth.length?Math.max(...growth):null;const latestGrowth=growth.at(-1)??null
 const volatility=growth.length>=2&&averageGrowth!=null?Math.sqrt(growth.reduce((sum,value)=>sum+(value-averageGrowth)**2,0)/(growth.length-1)):null
 return {averageGrowth,maximumGrowth,latestGrowth,volatility,completeness:ordered.length?valid.length/ordered.length*100:0,observationCount:valid.length,growthCount:growth.length}
}

export type FeasibilityLevel='attainable'|'demanding'|'highly-demanding'|'very-difficult'|'extreme'
export function accountingFeasibility(requiredGrowth:number):FeasibilityLevel{if(requiredGrowth<10)return'attainable';if(requiredGrowth<25)return'demanding';if(requiredGrowth<50)return'highly-demanding';if(requiredGrowth<100)return'very-difficult';return'extreme'}
export function scenarioRisk(impact:number){return impact>=10?'critical':impact>=5?'high':impact>=2?'moderate':'low'}

export type RankingInput={code:string;sectorValue:number|null;baselineGdp:number|null;directLoss:number;points:Point[];hierarchyConflict:boolean}
export type RankingResult=RankingInput&HistoricalEvidence&{requiredGrowth:number|null;gdpShare:number|null;score:number;confidence:'high'|'medium'|'low'}
/** Experimental score: size 20%, compensation burden 35%, trend 15%, volatility 10%, completeness 15%, hierarchy compatibility 5%. */
export function resilienceRanking(items:RankingInput[]):RankingResult[]{return items.map(item=>{const evidence=historicalEvidence(item.points);const requiredGrowth=item.sectorValue!=null&&item.sectorValue>0?item.directLoss/item.sectorValue*100:null;const gdpShare=item.sectorValue!=null&&item.baselineGdp?item.sectorValue/item.baselineGdp*100:null;const sizeScore=Math.min(Math.max(gdpShare??0,0)/20,1)*20;const burdenScore=requiredGrowth==null?0:35/(1+requiredGrowth/25);const trendScore=evidence.averageGrowth==null?0:Math.min(Math.max((evidence.averageGrowth+10)/30,0),1)*15;const volatilityScore=evidence.volatility==null?0:10/(1+evidence.volatility/20);const completenessScore=evidence.completeness/100*15;const compatibilityScore=item.hierarchyConflict?0:5;const score=item.hierarchyConflict?0:sizeScore+burdenScore+trendScore+volatilityScore+completenessScore+compatibilityScore;const confidence:RankingResult['confidence']=evidence.completeness>=90&&evidence.growthCount>=5?'high':evidence.completeness>=70&&evidence.growthCount>=3?'medium':'low';return {...item,...evidence,requiredGrowth,gdpShare,score,confidence}}).sort((a,b)=>b.score-a.score)}
