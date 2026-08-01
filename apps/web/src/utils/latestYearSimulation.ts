import type { Point } from '../types/economic'

export type MiningKey='snim_iron'|'gold_copper'|'oil_gas_extraction'
export type DiversificationKey='agriculture_fishing'|'manufacturing'|'services_commerce'
export type LatestYearScenarioInput={
 baseGdp:number|null|undefined
 primarySector:number|null|undefined
 secondarySector:number|null|undefined
 tertiarySector:number|null|undefined
 miningValues:Record<MiningKey,number|null|undefined>
 miningRates:Record<MiningKey,number>
 diversificationValues:Record<DiversificationKey,number|null|undefined>
 diversificationRates:Record<DiversificationKey,number>
}
export type ImpactCategory={key:'primary'|'secondary'|'tertiary'|'minerals'|'gdp';base:number|null;scenario:number|null}
export type LatestYearScenarioResult={baseGdp:number;scenarioGdp:number;variationAbsolute:number;variationPercent:number;totalMiningLosses:number;totalPositiveMiningChanges:number;totalDiversificationGains:number;netImpact:number;miningChanges:Record<MiningKey,number|null>;diversificationGains:Record<DiversificationKey,number|null>;categories:ImpactCategory[];warnings:string[]}

export function detectLatestAvailableYear(gdpSeries:Point[]){const years=gdpSeries.filter(point=>point.value!=null).map(point=>point.year);if(!years.length)throw new TypeError('No available GDP observation');return Math.max(...years)}
export function latestValue(points:Point[]|undefined,year:number){return points?.find(point=>point.year===year)?.value??null}

function validateRate(value:number,min:number,max:number){if(!Number.isFinite(value)||value<min||value>max)throw new RangeError(`Rate must be between ${min} and ${max}`)}
export function calculateLatestYearScenario(input:LatestYearScenarioInput):LatestYearScenarioResult{
 const {baseGdp}=input;if(baseGdp==null)throw new TypeError('Latest GDP value is missing');if(!Number.isFinite(baseGdp)||baseGdp<=0)throw new RangeError('Latest GDP must be finite and greater than zero')
 const warnings:string[]=[];const miningChanges={} as Record<MiningKey,number|null>
 for(const key of Object.keys(input.miningRates) as MiningKey[]){const rate=input.miningRates[key];validateRate(rate,-.8,.5);const value=input.miningValues[key];if(value==null){miningChanges[key]=null;warnings.push(`missing:${key}`)}else{if(!Number.isFinite(value)||value<0)throw new RangeError('Mining values must be finite and non-negative');miningChanges[key]=value*rate}}
 const diversificationGains={} as Record<DiversificationKey,number|null>
 for(const key of Object.keys(input.diversificationRates) as DiversificationKey[]){const rate=input.diversificationRates[key];validateRate(rate,0,.5);const value=input.diversificationValues[key];if(value==null){diversificationGains[key]=null;warnings.push(`missing:${key}`)}else{if(!Number.isFinite(value)||value<0)throw new RangeError('Diversification values must be finite and non-negative');diversificationGains[key]=value*rate}}
 const miningChangeValues=Object.values(miningChanges).filter((value):value is number=>value!=null);const diversificationGainValues=Object.values(diversificationGains).filter((value):value is number=>value!=null)
 const totalMiningLosses=Math.abs(miningChangeValues.filter(value=>value<0).reduce((sum,value)=>sum+value,0));const totalPositiveMiningChanges=miningChangeValues.filter(value=>value>0).reduce((sum,value)=>sum+value,0);const totalDiversificationGains=diversificationGainValues.reduce((sum,value)=>sum+value,0)
 const netImpact=-totalMiningLosses+totalPositiveMiningChanges+totalDiversificationGains;const scenarioGdp=baseGdp+netImpact;const variationAbsolute=scenarioGdp-baseGdp;const variationPercent=variationAbsolute/baseGdp*100
 const miningComplete=Object.values(input.miningValues).every(value=>value!=null);const mineralBase=miningComplete?Object.values(input.miningValues).reduce<number>((sum,value)=>sum+(value as number),0):null;const mineralScenario=mineralBase==null?null:mineralBase+miningChangeValues.reduce((sum,value)=>sum+value,0)
 const primaryGain=diversificationGains.agriculture_fishing??0;const secondaryChange=miningChangeValues.reduce((sum,value)=>sum+value,0)+(diversificationGains.manufacturing??0);const tertiaryGain=diversificationGains.services_commerce??0
 const category=(base:number|null|undefined,change:number)=>base==null?null:base+change
 const categories:ImpactCategory[]=[{key:'primary',base:input.primarySector??null,scenario:category(input.primarySector,primaryGain)},{key:'secondary',base:input.secondarySector??null,scenario:category(input.secondarySector,secondaryChange)},{key:'tertiary',base:input.tertiarySector??null,scenario:category(input.tertiarySector,tertiaryGain)},{key:'minerals',base:mineralBase,scenario:mineralScenario},{key:'gdp',base:baseGdp,scenario:scenarioGdp}]
 if(![scenarioGdp,variationAbsolute,variationPercent,totalMiningLosses,totalPositiveMiningChanges,totalDiversificationGains].every(Number.isFinite))throw new RangeError('Scenario results must be finite')
 return {baseGdp,scenarioGdp,variationAbsolute,variationPercent,totalMiningLosses,totalPositiveMiningChanges,totalDiversificationGains,netImpact,miningChanges,diversificationGains,categories,warnings}
}
