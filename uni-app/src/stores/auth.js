import { defineStore } from 'pinia'
import api, { setAuth, clearAuth } from '../api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: uni.getStorageSync('access_token') || '',
    user: JSON.parse(uni.getStorageSync('user') || 'null'),
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
  },

  actions: {
    async login(username, password) {
      const res = await api.post('/auth/login', { username, password })
      this.token = res.data.access_token
      this.user = res.data.user
      setAuth(this.token, this.user)
      return res.data
    },

    async register(formData) {
      const res = await api.post('/auth/register', formData)
      this.token = res.data.access_token
      this.user = res.data.user
      setAuth(this.token, this.user)
      return res.data
    },

    async fetchUser() {
      try {
        const res = await api.get('/auth/me')
        this.user = res.data
        uni.setStorageSync('user', JSON.stringify(this.user))
      } catch (e) {
        this.logout()
        throw e
      }
    },

    async updateProfile(profileData) {
      const res = await api.put('/auth/profile', profileData)
      this.user = res.data
      uni.setStorageSync('user', JSON.stringify(this.user))
      return res.data
    },

    async uploadAvatar(filePath) {
      const res = await api.upload('/auth/avatar', filePath, 'file')
      this.user = res.data
      uni.setStorageSync('user', JSON.stringify(this.user))
      return res.data
    },

    async wxLogin(code) {
      const res = await api.post('/auth/wx-login', { code })
      this.token = res.data.access_token
      this.user = res.data.user
      setAuth(this.token, this.user)
      return res.data
    },

    async bindWechat(code) {
      const res = await api.post('/auth/bind-wechat', { code })
      this.user = res.data
      uni.setStorageSync('user', JSON.stringify(this.user))
      return res.data
    },

    async unbindWechat() {
      const res = await api.post('/auth/unbind-wechat')
      this.user = res.data
      uni.setStorageSync('user', JSON.stringify(this.user))
      return res.data
    },

    async setPassword(newPassword) {
      const res = await api.post('/auth/set-password', { new_password: newPassword })
      // Refresh user so has_password / wechat_bound update in storage
      try { await this.fetchUser() } catch {}
      return res.data
    },

    logout() {
      this.token = ''
      this.user = null
      clearAuth()
      uni.reLaunch({ url: '/pages/login/index' })
    },
  },
})
