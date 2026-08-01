import { useEffect, useState } from 'react'
import { api } from '../services/api'
import type { HealthResponse } from '../types/api'

export function useHealth() {
  const [data, setData] = useState<HealthResponse | null>(null)
  const [error, setError] = useState<Error | null>(null)
  const [loading, setLoading] = useState(true)
  useEffect(() => {
    const controller = new AbortController()
    api.get<HealthResponse>('/api/health', { signal: controller.signal }).then((response) => setData(response.data)).catch((reason: unknown) => {
      if (!controller.signal.aborted) setError(reason instanceof Error ? reason : new Error('API request failed'))
    }).finally(() => { if (!controller.signal.aborted) setLoading(false) })
    return () => controller.abort()
  }, [])
  return { data, error, loading }
}
