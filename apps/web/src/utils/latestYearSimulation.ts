import type { Point } from '../types/economic'

export type MiningKey='snim_iron'|'gold_copper'|'oil_gas_extraction'
export type DiversificationKey='agriculture_fishing'|'manufacturing'|'services_commerce'
export type SectorAdjustment={indicatorCode:string;baseValue:number|null|undefined;adjustmentPercent:number;parentIndicatorCode?:string;canonicalIndicatorCode?:string}
export type SectorSimulationResult={indicatorCode:string;baseValue:number;adjustmentPercent:number;change:number;scenarioValue:number}
export type SimulationResult={baselineGdp:number;totalLosses:number;totalGains:number;netImpact:number;simulatedGdp:number;variationPercent:number;sectorResults:SectorSimulationResult[];unavailableIndicatorCodes:string[]}
export type ScenarioInput={baselineGdp:number|null|undefined;shockAdjustments:SectorAdjustment[];diversificationAdjustments:SectorAdjustment[];sliderLimits?:{min:number;max:number}}
export type ImpactCategory={key:'primary'|'secondary'|'tertiary'|'minerals'|'gdp';base:number|null;scenario:number|null}
export type LatestYearViewInput={baselineGdp:number|null|undefined;primarySector:number|null|undefined;secondarySector:number|null|undefined;tertiarySector:number|null|undefined;miningValues:Record<MiningKey,number|null|undefined>;miningPercents:Record<MiningKey,number>;diversificationValues:Record<DiversificationKey,number|null|undefined>;diversificationPercents:Record<DiversificationKey,number>}
export type LatestYearScenarioView={simulation:SimulationResult;categories:ImpactCategory[];miningChanges:Record<MiningKey,number|null>;diversificationChanges:Record<DiversificationKey,number|null>}

export function detectLatestAvailableYear(gdpSeries:Point[]){const years=gdpSeries.filter(point=>point.value!=null&&Number.isFinite(point.value)).map(point=>point.year);if(!years.length)throw new TypeError('No available GDP observation');return Math.max(...years)}
export function detectLatestCommonYear(series:Point[][]){if(!series.length)throw new TypeError('No simulator series supplied');const valid=series.map(points=>new Set(points.filter(point=>point.value!=null&&Number.isFinite(point.value)).map(point=>point.year)));const common=[...valid[0]].filter(year=>valid.every(years=>years.has(year)));if(!common.length)throw new TypeError('No common valid simulator year');return Math.max(...common)}
export function latestValue(points:Point[]|undefined,year:number){return points?.find(point=>point.year===year)?.value??null}

export function calculateLatestYearScenario({baselineGdp,shockAdjustments,diversificationAdjustments,sliderLimits={min:-80,max:50}}:ScenarioInput):SimulationResult{
 if(baselineGdp==null)throw new TypeError('Baseline GDP is unavailable')
 if(!Number.isFinite(baselineGdp)||baselineGdp<=0)throw new RangeError('Baseline GDP must be finite and positive')
 const all=[...shockAdjustments,...diversificationAdjustments]
 const seen=new Set<string>();const selected=new Set(all.map(a=>a.canonicalIndicatorCode??a.indicatorCode));const unavailableIndicatorCodes:string[]=[];const sectorResults:SectorSimulationResult[]=[]
 for(const adjustment of all){
  const canonical=adjustment.canonicalIndicatorCode??adjustment.indicatorCode
  if(seen.has(canonical))throw new RangeError(`Duplicate or alias adjustment: ${canonical}`)
  if(adjustment.parentIndicatorCode&&selected.has(adjustment.parentIndicatorCode))throw new RangeError(`Parent and child adjustments overlap: ${canonical}`)
  seen.add(canonical)
  if(!Number.isFinite(adjustment.adjustmentPercent)||adjustment.adjustmentPercent<sliderLimits.min||adjustment.adjustmentPercent>sliderLimits.max)throw new RangeError(`Adjustment percent must be between ${sliderLimits.min} and ${sliderLimits.max}`)
  if(adjustment.baseValue==null){unavailableIndicatorCodes.push(adjustment.indicatorCode);continue}
  if(!Number.isFinite(adjustment.baseValue)||adjustment.baseValue<0)throw new RangeError(`Base value must be finite and non-negative: ${canonical}`)
  const change=adjustment.baseValue*adjustment.adjustmentPercent/100
  sectorResults.push({indicatorCode:adjustment.indicatorCode,baseValue:adjustment.baseValue,adjustmentPercent:adjustment.adjustmentPercent,change,scenarioValue:adjustment.baseValue+change})
 }
 const totalLosses=Math.abs(sectorResults.filter(r=>r.change<0).reduce((sum,r)=>sum+r.change,0))
 const totalGains=sectorResults.filter(r=>r.change>0).reduce((sum,r)=>sum+r.change,0)
 const netImpact=totalGains-totalLosses
 const simulatedGdp=baselineGdp+netImpact
 const variationPercent=netImpact/baselineGdp*100
 return {baselineGdp,totalLosses,totalGains,netImpact,simulatedGdp,variationPercent,sectorResults,unavailableIndicatorCodes}
}

export function buildLatestYearSimulationView(input:LatestYearViewInput):LatestYearScenarioView{
 const shockAdjustments=(Object.keys(input.miningPercents) as MiningKey[]).map(indicatorCode=>({indicatorCode,baseValue:input.miningValues[indicatorCode],adjustmentPercent:input.miningPercents[indicatorCode]}))
 const diversificationAdjustments=(Object.keys(input.diversificationPercents) as DiversificationKey[]).map(indicatorCode=>({indicatorCode,baseValue:input.diversificationValues[indicatorCode],adjustmentPercent:input.diversificationPercents[indicatorCode]}))
 const simulation=calculateLatestYearScenario({baselineGdp:input.baselineGdp,shockAdjustments,diversificationAdjustments,sliderLimits:{min:-80,max:50}})
 const change=(code:string)=>simulation.sectorResults.find(r=>r.indicatorCode===code)?.change??0
 const miningChanges=Object.fromEntries((Object.keys(input.miningPercents) as MiningKey[]).map(key=>[key,input.miningValues[key]==null?null:change(key)])) as Record<MiningKey,number|null>
 const diversificationChanges=Object.fromEntries((Object.keys(input.diversificationPercents) as DiversificationKey[]).map(key=>[key,input.diversificationValues[key]==null?null:change(key)])) as Record<DiversificationKey,number|null>
 const mineralBase=Object.values(input.miningValues).every(v=>v!=null)?Object.values(input.miningValues).reduce<number>((sum,v)=>sum+(v as number),0):null
 const miningTotal=Object.values(miningChanges).reduce<number>((sum,v)=>sum+(v??0),0)
 const category=(base:number|null|undefined,delta:number)=>base==null?null:base+delta
 const categories:ImpactCategory[]=[
  {key:'primary',base:input.primarySector??null,scenario:category(input.primarySector,diversificationChanges.agriculture_fishing??0)},
  {key:'secondary',base:input.secondarySector??null,scenario:category(input.secondarySector,miningTotal+(diversificationChanges.manufacturing??0))},
  {key:'tertiary',base:input.tertiarySector??null,scenario:category(input.tertiarySector,diversificationChanges.services_commerce??0)},
  {key:'minerals',base:mineralBase,scenario:mineralBase==null?null:mineralBase+miningTotal},
  {key:'gdp',base:simulation.baselineGdp,scenario:simulation.simulatedGdp},
 ]
 return {simulation,categories,miningChanges,diversificationChanges}
}
