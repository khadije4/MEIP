import axios from 'axios'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
  timeout: 15_000,
  headers: { Accept: 'application/json' },
})

api.interceptors.response.use((response) => response, (error: unknown) => Promise.reject(error))
