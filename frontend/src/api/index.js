import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

// 请求拦截器 - 自动附加 JWT token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器 - 统一错误处理
api.interceptors.response.use(
  (res) => res,
  (err) => {
    const status = err.response?.status

    if (status === 401) {
      // Token 过期或无效，清除本地登录状态
      const currentPath = window.location.pathname
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      // 只在非登录页时跳转，避免登录失败也触发跳转
      if (currentPath !== '/login') {
        window.location.href = '/login'
      }
    } else if (status === 403) {
      // 无权限 - 不自动跳转，由各组件自行处理
      console.warn('[API] 权限不足:', err.config?.url)
    } else if (status >= 500) {
      console.error('[API] 服务器错误:', err.config?.url, err.response?.data)
    } else if (!err.response) {
      // 网络错误（后端未启动、断网等）
      console.error('[API] 网络连接失败，请检查后端服务是否启动')
    }

    return Promise.reject(err)
  }
)

// ============ 用户认证 ============
export const authAPI = {
  login: (data) => api.post('/users/login/', data),
  register: (data) => api.post('/users/register/', data),
  getMe: () => api.get('/users/me/'),
  updateProfile: (data) => api.put('/users/profile/', data),
}

// ============ 用户管理 ============
export const userAPI = {
  list: (params) => api.get('/users/users/', { params }),
  get: (id) => api.get(`/users/users/${id}/`),
  create: (data) => api.post('/users/users/', data),
  update: (id, data) => api.put(`/users/users/${id}/`, data),
  patch: (id, data) => api.patch(`/users/users/${id}/`, data),
  delete: (id) => api.delete(`/users/users/${id}/`),
  promote: (id) => api.post(`/users/users/${id}/promote/`),
  demote: (id) => api.post(`/users/users/${id}/demote/`),
  transferSuperuser: (id) => api.post(`/users/users/${id}/transfer-superuser/`),
}

// ============ 角色权限 ============
export const roleAPI = {
  list: () => api.get('/users/roles/'),
  get: (id) => api.get(`/users/roles/${id}/`),
  create: (data) => api.post('/users/roles/', data),
  update: (id, data) => api.put(`/users/roles/${id}/`, data),
  delete: (id) => api.delete(`/users/roles/${id}/`),
}

export const permissionAPI = {
  list: () => api.get('/users/permissions/'),
  create: (data) => api.post('/users/permissions/', data),
  update: (id, data) => api.put(`/users/permissions/${id}/`, data),
  delete: (id) => api.delete(`/users/permissions/${id}/`),
}

// ============ 岗位数据 ============
export const positionAPI = {
  list: (params) => api.get('/position/positions/', { params }),
  get: (id) => api.get(`/position/positions/${id}/`),
  favorite: (id) => api.post(`/position/positions/${id}/favorite/`),
  unfavorite: (id) => api.post(`/position/positions/${id}/unfavorite/`),
  favorites: (params) => api.get('/position/favorites/', { params }),
  queries: () => api.get('/position/queries/'),
}

// ============ 数据采集 ============
export const dataAPI = {
  oneClickCollection: () => api.post('/data/one-click-collection/'),
  sources: { list: (p) => api.get('/data/sources/', { params: p }), create: (d) => api.post('/data/sources/', d), delete: (id) => api.delete(`/data/sources/${id}/`) },
  tasks: {
    list: (p) => api.get('/data/tasks/', { params: p }),
    get: (id) => api.get(`/data/tasks/${id}/`),
    create: (d) => api.post('/data/tasks/', d),
    update: (id, d) => api.put(`/data/tasks/${id}/`, d),
    delete: (id) => api.delete(`/data/tasks/${id}/`),
    run: (id) => api.post(`/data/tasks/${id}/run/`),
    pause: (id) => api.post(`/data/tasks/${id}/pause/`),
  },
  records: { list: (p) => api.get('/data/records/', { params: p }) },
}

// ============ 统计分析 ============
export const statisticsAPI = {
  basic: (p) => api.get('/statistics/basic/', { params: p }),
  salaryDist: (p) => api.get('/statistics/salary-distribution/', { params: p }),
  expDist: (p) => api.get('/statistics/experience-distribution/', { params: p }),
  eduDist: (p) => api.get('/statistics/education-distribution/', { params: p }),
  typeDist: (p) => api.get('/statistics/position-type-distribution/', { params: p }),
  cityDist: (p) => api.get('/statistics/city-distribution/', { params: p }),
  industryDist: (p) => api.get('/statistics/industry-distribution/', { params: p }),
  companyDist: (p) => api.get('/statistics/company-distribution/', { params: p }),
  reports: { list: (p) => api.get('/statistics/reports/', { params: p }), create: (d) => api.post('/statistics/reports/', d) },
}

// ============ 可视化 ============
export const vizAPI = {
  dashboards: {
    list: (p) => api.get('/visualization/dashboards/', { params: p }),
    get: (id) => api.get(`/visualization/dashboards/${id}/`),
    create: (d) => api.post('/visualization/dashboards/', d),
    update: (id, d) => api.put(`/visualization/dashboards/${id}/`, d),
    delete: (id) => api.delete(`/visualization/dashboards/${id}/`),
  },
  charts: {
    list: (p) => api.get('/visualization/charts/', { params: p }),
    create: (d) => api.post('/visualization/charts/', d),
    update: (id, d) => api.put(`/visualization/charts/${id}/`, d),
    delete: (id) => api.delete(`/visualization/charts/${id}/`),
    testData: (id) => api.post(`/visualization/charts/${id}/test_data/`),
    addToDashboard: (id, d) => api.post(`/visualization/charts/${id}/add_to_dashboard/`, d),
  },
}

// ============ 操作日志 ============
export const logAPI = {
  operations: (p) => api.get('/logs/operation-logs/', { params: p }),
  system: (p) => api.get('/logs/system-logs/', { params: p }),
}

// ============ AI分析 ============
export const aiAPI = {
  algorithms: { list: () => api.get('/ai/algorithms/'), create: (d) => api.post('/ai/algorithms/', d) },
  tasks: {
    list: (p) => api.get('/ai/tasks/', { params: p }),
    get: (id) => api.get(`/ai/tasks/${id}/`),
    create: (d) => api.post('/ai/tasks/', d),
    delete: (id) => api.delete(`/ai/tasks/${id}/`),
    execute: (id) => api.post(`/ai/tasks/${id}/execute/`),
    result: (id) => api.get(`/ai/tasks/${id}/result/`),
  },
  analyzeResume: (data) => api.post('/ai/analyze-resume/', data, {
    headers: data instanceof FormData ? { 'Content-Type': 'multipart/form-data' } : undefined,
  }),
}

export default api
