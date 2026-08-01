import { api } from './api'
import type { Indicator, Point } from '../types/economic'

export const simulationSectorCodes = [
  'primary_sector', 'extractive_activities', 'manufacturing',
  'construction_public_works', 'tertiary_sector', 'fishing', 'commerce',
  'transport', 'secondary_sector',
] as const

export type SimulationSectorCode = typeof simulationSectorCodes[number]

export type SingleSimulation = {
  year: number
  baseline_activity_gdp: number
  indicator_code: string
  name_fr: string
  name_ar: string | null
  sector_value: number
  sector_share_of_gdp_pct: number
  shock_rate: number
  direct_loss: number
  simulated_gdp: number
  direct_gdp_impact_pct: number
  current_price_warning_fr: string
  current_price_warning_ar: string
  methodology_disclaimer_fr: string
  methodology_disclaimer_ar: string
  source: string
  unit: string
}

export type DependencyHistory = {
  indicator_code: string
  points: Array<{ year:number; dependency_pct:number }>
  minimum_dependency_pct: number | null
  maximum_dependency_pct: number | null
  latest_dependency_pct: number | null
  average_dependency_pct: number | null
  source: string
  unit: string
}

export type CompositionRow = {
  year:number
  gdp:number|null
  primary_sector:number|null
  extractive_activities:number|null
  manufacturing:number|null
  construction_public_works:number|null
  tertiary_sector:number|null
}

async function series(code:string) {
  return (await api.get<{points:Point[]}>(`/api/indicators/${code}/series`)).data.points
}

export async function loadSimulationPageData() {
  const [indicatorResponse, gdp, primary, extractive, manufacturing, construction, tertiary] = await Promise.all([
    api.get<Indicator[]>('/api/indicators'), series('gdp_activity_market_prices'),
    series('primary_sector'),
    series('extractive_activities'), series('manufacturing'),
    series('construction_public_works'), series('tertiary_sector'),
  ])
  const allowed = new Set<string>(simulationSectorCodes)
  const sectors = indicatorResponse.data.filter(item => allowed.has(item.code))
  const maps = [gdp,primary,extractive,manufacturing,construction,tertiary].map(points => new Map(points.map(point => [point.year,point.value])))
  const years = [...new Set(primary.map(point => point.year))].sort((a,b)=>a-b)
  const composition:CompositionRow[] = years.map(year => ({
    year, gdp:maps[0].get(year)??null, primary_sector:maps[1].get(year)??null, extractive_activities:maps[2].get(year)??null,
    manufacturing:maps[3].get(year)??null, construction_public_works:maps[4].get(year)??null,
    tertiary_sector:maps[5].get(year)??null,
  }))
  return { sectors, years, composition }
}

export async function simulateSingle(year:number, indicatorCode:string, shockPercent:number) {
  return (await api.post<SingleSimulation>('/api/stress-test/single', {
    year, indicator_code:indicatorCode, shock_rate:shockPercent/100,
  })).data
}

export async function loadDependency(indicatorCode:string) {
  return (await api.get<DependencyHistory>(`/api/stress-test/history/${indicatorCode}`)).data
}

export async function loadImpactPreview(indicatorCode:string, year:number) {
  const [sectorPoints,gdpPoints]=await Promise.all([series(indicatorCode),series('gdp_activity_market_prices')])
  return {
    sectorValue:sectorPoints.find(point=>point.year===year)?.value??null,
    baselineGdp:gdpPoints.find(point=>point.year===year)?.value??null,
  }
}
