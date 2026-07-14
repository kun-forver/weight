import { defineStore } from 'pinia'
import api from '../api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('access_token') || '',
    user: JSON.parse(localStorage.getItem('user') || 'null'),
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
  },

  actions: {
    async login(username, password) {
      const res = await api.post('/auth/login', { username, password })
      this.token = res.data.access_token
      this.user = res.data.user
      localStorage.setItem('access_token', this.token)
      localStorage.setItem('user', JSON.stringify(this.user))
      return res.data
    },

    async register(username, password, nickname) {
      const res = await api.post('/auth/register', { username, password, nickname })
      this.token = res.data.access_token
      this.user = res.data.user
      localStorage.setItem('access_token', this.token)
      localStorage.setItem('user', JSON.stringify(this.user))
      return res.data
    },

    async fetchUser() {
      try {
        const res = await api.get('/auth/me')
        this.user = res.data
        localStorage.setItem('user', JSON.stringify(this.user))
        return res.data
      } catch (e) {
        this.logout()
        throw e
      }
    },

    async updateProfile(profileData) {
      const res = await api.put('/auth/profile', profileData)
      this.user = res.data
      localStorage.setItem('user', JSON.stringify(this.user))
      return res.data
    },

    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    },
  },
})
