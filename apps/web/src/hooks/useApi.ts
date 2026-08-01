import { useEffect, useState } from 'react'
import { api } from '../services/api'

export function useApi<T>(path: string | null) {
  const [data, setData] = useState<T | null>(null); const [error, setError] = useState<Error | null>(null); const [loading, setLoading] = useState(Boolean(path))
  useEffect(() => {
    if (!path) { setLoading(false); return }
    const controller = new AbortController(); setLoading(true); setError(null)
    api.get<T>(path, { signal: controller.signal }).then((r) => setData(r.data)).catch((reason: unknown) => { if (!controller.signal.aborted) setError(reason instanceof Error ? reason : new Error('Request failed')) }).finally(() => { if (!controller.signal.aborted) setLoading(false) })
    return () => controller.abort()
  }, [path])
  return { data, error, loading, setData }
}
