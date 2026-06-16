import client from './client'

// ── Import ──
export const importFull = () => client.post('/import/full')
export const importIncremental = () => client.post('/import/incremental')
export const importStatus = () => client.get('/import/status')
export const importLogs = (skip = 0, limit = 20) =>
  client.get('/import/logs', { params: { skip, limit } })

// ── Projects ──
export const getProjects = (page = 1, pageSize = 20, search = '') =>
  client.get('/projects', { params: { page, page_size: pageSize, search } })
export const getProject = (id) => client.get(`/projects/${id}`)

// ── Sessions ──
export const getSessions = (page = 1, pageSize = 20, projectId = null) =>
  client.get('/sessions', {
    params: { page, page_size: pageSize, project_id: projectId },
  })
export const getSession = (id) => client.get(`/sessions/${id}`)

// ── Messages ──
export const searchMessages = (q, page = 1, pageSize = 20) =>
  client.get('/messages/search', { params: { q, page, page_size: pageSize } })
export const getMessages = (sessionId = null, page = 1, pageSize = 50) =>
  client.get('/messages', {
    params: { session_id: sessionId, page, page_size: pageSize },
  })

// ── File History ──
export const getFileHistory = (page = 1, pageSize = 20) =>
  client.get('/file-history', { params: { page, page_size: pageSize } })
export const getFileHistoryDetail = (id) => client.get(`/file-history/${id}`)

// ── Stats ──
export const getStatsOverview = () => client.get('/stats/overview')
export const getTimeline = (granularity = 'day') =>
  client.get('/stats/timeline', { params: { granularity } })
export const getTopProjects = (limit = 10) =>
  client.get('/stats/top-projects', { params: { limit } })
