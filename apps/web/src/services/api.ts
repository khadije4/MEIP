import axios from 'axios'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000',
  timeout: 15_000,
  headers: { Accept: 'application/json' },
})

api.interceptors.response.use((response) => response, (error: unknown) => Promise.reject(error))
