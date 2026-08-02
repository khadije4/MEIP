import {api} from './api'
import type {DashboardOverview,Point} from '../types/economic'

export const executiveSeriesCodes=['gdp_activity_market_prices','primary_sector','secondary_sector','tertiary_sector','agriculture_forestry','fishing','extractive_activities','manufacturing','construction_public_works','commerce','other_services','exports','imports'] as const
export type ExecutiveSeriesCode=typeof executiveSeriesCodes[number]
export type ExecutiveDashboardData={overview:DashboardOverview;series:Record<ExecutiveSeriesCode,Point[]>}

export async function loadExecutiveDashboard():Promise<ExecutiveDashboardData>{
 const [overview,...responses]=await Promise.all([api.get<DashboardOverview>('/api/dashboard/overview'),...executiveSeriesCodes.map(code=>api.get<{points:Point[]}>(`/api/indicators/${code}/series`))])
 return {overview:overview.data,series:Object.fromEntries(executiveSeriesCodes.map((code,index)=>[code,responses[index].data.points])) as Record<ExecutiveSeriesCode,Point[]>}
}
