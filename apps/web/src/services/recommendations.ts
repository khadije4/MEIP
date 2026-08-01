import { api } from './api'
import type { RecommendationResponse } from '../types/economic'

export async function generateRecommendations(year:number, indicatorCode:string, shockPercent:number, duration='one_year') {
  return (await api.post<RecommendationResponse>('/api/recommendations/generate', {
    year, shocks:[{indicator_code:indicatorCode,shock_rate:shockPercent/100}], shock_duration:duration,
  })).data
}
