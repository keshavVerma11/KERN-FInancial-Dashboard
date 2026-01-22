import axios from 'axios'
import { supabase } from './supabase'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Create axios instance
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
apiClient.interceptors.request.use(async (config) => {
  const { data: { session } } = await supabase.auth.getSession()
  
  if (session?.access_token) {
    config.headers.Authorization = `Bearer ${session.access_token}`
  }
  
  return config
})

// API functions
export const api = {
  // Auth
  auth: {
    verify: () => apiClient.get('/api/auth/verify'),
    me: () => apiClient.get('/api/auth/me'),
  },
  
  // Transactions
  transactions: {
    list: (params?: { skip?: number; limit?: number; status?: string }) =>
      apiClient.get('/api/transactions', { params }),
    get: (id: string) => apiClient.get(`/api/transactions/${id}`),
    create: (data: any) => apiClient.post('/api/transactions', data),
    update: (id: string, data: any) => apiClient.put(`/api/transactions/${id}`, data),
    delete: (id: string) => apiClient.delete(`/api/transactions/${id}`),
    summary: (params?: { start_date?: string; end_date?: string }) =>
      apiClient.get('/api/transactions/stats/summary', { params }),
  },
  
  // Documents
  documents: {
    list: (params?: { skip?: number; limit?: number }) =>
      apiClient.get('/api/documents', { params }),
    get: (id: string) => apiClient.get(`/api/documents/${id}`),
    upload: (file: File) => {
      const formData = new FormData()
      formData.append('file', file)
      return apiClient.post('/api/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
    },
    process: (id: string) => apiClient.post(`/api/documents/${id}/process`),
    delete: (id: string) => apiClient.delete(`/api/documents/${id}`),
  },
  
  // Reports
  reports: {
    incomeStatement: (startDate: string, endDate: string) =>
      apiClient.get('/api/reports/income-statement', {
        params: { start_date: startDate, end_date: endDate },
      }),
    balanceSheet: (asOfDate: string) =>
      apiClient.get('/api/reports/balance-sheet', {
        params: { as_of_date: asOfDate },
      }),
    cashFlow: (startDate: string, endDate: string) =>
      apiClient.get('/api/reports/cash-flow', {
        params: { start_date: startDate, end_date: endDate },
      }),
  },
}

export default apiClient
