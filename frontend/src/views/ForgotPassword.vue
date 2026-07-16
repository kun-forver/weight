<template>
  <div class="auth-page">
    <div class="auth-header">
      <div class="logo-circle">🔑</div>
      <h1 class="auth-title">找回密码</h1>
      <p class="auth-subtitle">请填写您的注册邮箱以重置密码</p>
    </div>

    <div class="auth-card">
      <form v-if="!submitted" @submit.prevent="handleSendLink">
        <div class="input-group">
          <span class="input-icon">✉️</span>
          <input
            v-model="email"
            type="email"
            placeholder="请输入电子邮箱"
            class="auth-input"
            required
            autocomplete="email"
          />
        </div>

        <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>

        <button type="submit" class="btn-primary" :disabled="loading">
          {{ loading ? '发送中...' : '发 送 重 置 链 接' }}
        </button>
      </form>

      <div v-else class="success-container">
        <div class="success-icon">✉️</div>
        <p class="success-text">密码重置链接已成功发送！</p>
        <p class="info-text">
          请检查您的邮箱收件箱或垃圾箱。链接有效时间为 15 分钟。<br />
          <small class="dev-hint">（如果您在开发环境下，请直接查看后端控制台输出的重置链接）</small>
        </p>
      </div>

      <div class="auth-footer">
        <router-link to="/login" class="link">返回登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../api'

const email = ref('')
const loading = ref(false)
const submitted = ref(false)
const errorMsg = ref('')

async function handleSendLink() {
  if (!email.value) {
    errorMsg.value = '请输入您的注册邮箱'
    return
  }
  loading.value = true
  errorMsg.value = ''
  try {
    await api.post('/auth/forgot-password', { email: email.value })
    submitted.value = true
  } catch (e) {
    const detail = e.response?.data?.detail
    errorMsg.value = typeof detail === 'string' ? detail : '发送失败，请确认邮箱是否正确'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #ff3b30 0%, #ff9500 40%, #f5f5f7 70%);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60px 20px 40px;
}

.auth-header {
  text-align: center;
  margin-bottom: 30px;
}

.logo-circle {
  width: 80px;
  height: 80px;
  background: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40px;
  margin: 0 auto 16px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.auth-title {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
  letter-spacing: 2px;
}

.auth-subtitle {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.85);
  margin-top: 6px;
}

.auth-card {
  width: 100%;
  background: #fff;
  border-radius: 18px;
  padding: 28px 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
}

.input-group {
  display: flex;
  align-items: center;
  background: #f5f5f7;
  border-radius: 14px;
  padding: 0 14px;
  margin-bottom: 20px;
  height: 50px;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.input-group:focus-within {
  background: #fff0f0;
  border-color: #ff3b30;
  box-shadow: 0 0 0 2px rgba(255, 59, 48, 0.15);
}

.input-icon {
  font-size: 18px;
  margin-right: 10px;
  opacity: 0.6;
}

.auth-input {
  flex: 1;
  height: 100%;
  font-size: 16px;
  color: #1d1d1f;
  background: none;
  border: none;
  outline: none;
}

.auth-input::placeholder {
  color: #aeaeb2;
}

.error-msg {
  color: #ff3b30;
  font-size: 13px;
  margin-bottom: 16px;
  text-align: center;
}

.btn-primary {
  width: 100%;
  height: 50px;
  background: #ff3b30;
  color: #fff;
  border-radius: 14px;
  font-size: 17px;
  font-weight: 600;
  transition: opacity 0.2s;
  border: none;
  cursor: pointer;
  box-shadow: 0 4px 14px rgba(255, 59, 48, 0.3);
}

.btn-primary:active {
  opacity: 0.85;
}

.btn-primary:disabled {
  opacity: 0.5;
}

.success-container {
  text-align: center;
  padding: 10px 0;
}

.success-icon {
  font-size: 48px;
  color: #34c759;
  margin-bottom: 12px;
}

.success-text {
  font-size: 18px;
  font-weight: 700;
  color: #1d1d1f;
  margin-bottom: 8px;
}

.info-text {
  font-size: 13px;
  color: #86868b;
  line-height: 1.5;
}

.dev-hint {
  color: #ff9500;
  font-weight: 500;
}

.auth-footer {
  text-align: center;
  margin-top: 24px;
  font-size: 14px;
  color: #86868b;
}

.link {
  color: #ff3b30;
  text-decoration: none;
  font-weight: 600;
}
</style>
