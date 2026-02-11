import { create } from 'zustand'
import { authAPI } from '../api'

const useAuthStore = create((set) => ({
  token: localStorage.getItem('token') || null,
  user: JSON.parse(localStorage.getItem('user') || 'null'),

  login: async (username, password) => {
    const { data } = await authAPI.login({ username, password })
    const token = data.access
    const user = data.user
    localStorage.setItem('token', token)
    localStorage.setItem('user', JSON.stringify(user))
    set({ token, user })
    return data
  },

  register: async (values) => {
    // 直接抛出错误让组件层处理，保留完整的 response 信息
    const { data } = await authAPI.register(values)
    return data
  },

  logout: () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    set({ token: null, user: null })
  },

  fetchUser: async () => {
    try {
      const { data } = await authAPI.getMe()
      localStorage.setItem('user', JSON.stringify(data))
      set({ user: data })
    } catch {
      // token 可能已过期，静默处理
    }
  },
}))

export default useAuthStore
