export type ShockInput={baselineGdp:number|null|undefined;sectorValue:number|null|undefined;shockRate:number}
export type ShockResult={directLoss:number;simulatedGdp:number;directImpactPercentage:number;remainingSectorValue:number;unaffectedGdp:number}
export function calculateSingleSectorShock({baselineGdp,sectorValue,shockRate}:ShockInput):ShockResult{
 if(baselineGdp==null||sectorValue==null)throw new TypeError('Required economic value is missing')
 if(!Number.isFinite(baselineGdp)||!Number.isFinite(sectorValue)||!Number.isFinite(shockRate))throw new TypeError('Values must be finite')
 if(baselineGdp<=0)throw new RangeError('Activity-side GDP must be greater than zero')
 if(sectorValue<0)throw new RangeError('Sector value must not be negative')
 if(sectorValue>baselineGdp)throw new RangeError('Sector value exceeds activity-side GDP')
 if(shockRate<0||shockRate>1)throw new RangeError('Shock rate must be between zero and one')
 const directLoss=sectorValue*shockRate
 return {directLoss,simulatedGdp:baselineGdp-directLoss,directImpactPercentage:directLoss/baselineGdp*100,remainingSectorValue:sectorValue-directLoss,unaffectedGdp:baselineGdp-sectorValue}
}
export function scenarioRisk(impact:number){return impact>=10?'critical':impact>=5?'high':impact>=2?'moderate':'low'}
