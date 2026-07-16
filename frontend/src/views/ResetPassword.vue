<template>
  <div class="auth-page">
    <div class="auth-header">
      <div class="logo-circle">⚙️</div>
      <h1 class="auth-title">重置密码</h1>
      <p class="auth-subtitle">正在处理您的密码重置请求</p>
    </div>

    <div class="auth-card">
      <!-- Loading state -->
      <div v-if="state === 'loading'" class="status-container">
        <div class="spinner">⏳</div>
        <p class="status-text">正在重置密码，请稍候...</p>
      </div>

      <!-- Success state -->
      <div v-else-if="state === 'success'" class="status-container">
        <div class="status-icon success">✓</div>
        <p class="status-text success-title">密码重置成功！</p>
        <div class="reset-box">
          默认密码已设为：<span class="default-password">123456</span>
        </div>
        <p class="info-text">请登录后点击“我的”->“设置”尽快修改您的密码，保障账户安全。</p>
        <router-link to="/login" class="btn-primary-link">立即登录</router-link>
      </div>

      <!-- Error state -->
      <div v-else-if="state === 'error'" class="status-container">
        <div class="status-icon error">✕</div>
        <p class="status-text error-title">密码重置失败</p>
        <p class="info-text error-detail">{{ errorMsg || '该重置链接可能已失效或已过期。' }}</p>
        <router-link to="/forgot-password" class="btn-primary-link btn-error">重新申请重置</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api'

const route = useRoute()
const state = ref('loading') // 'loading' | 'success' | 'error'
const errorMsg = ref('')

async function performReset() {
  const token = route.query.token
  if (!token) {
    state.value = 'error'
    errorMsg.value = '请求中缺少重置令牌(Token)。'
    return
  }

  try {
    await api.post('/auth/reset-password', { token })
    state.value = 'success'
  } catch (e) {
    state.value = 'error'
    const detail = e.response?.data?.detail
    errorMsg.value = typeof detail === 'string' ? detail : '链接无效或已过期，请重新申请。'
  }
}

onMounted(() => {
  performReset()
})
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #ff9500 0%, #ffcc00 40%, #f5f5f7 70%);
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

.status-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 16px 0;
}

.spinner {
  font-size: 36px;
  animation: rotate 2s linear infinite;
  margin-bottom: 16px;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.status-icon {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  font-weight: bold;
  color: #fff;
  margin-bottom: 16px;
}

.status-icon.success {
  background: #34c759;
  box-shadow: 0 4px 12px rgba(52, 199, 89, 0.35);
}

.status-icon.error {
  background: #ff3b30;
  box-shadow: 0 4px 12px rgba(255, 59, 48, 0.35);
}

.status-text {
  font-size: 16px;
  color: #1d1d1f;
  font-weight: 500;
}

.success-title {
  font-size: 18px;
  font-weight: 700;
  color: #34c759;
}

.error-title {
  font-size: 18px;
  font-weight: 700;
  color: #ff3b30;
}

.reset-box {
  background: #f5f5f7;
  border-radius: 12px;
  padding: 12px 20px;
  font-size: 15px;
  color: #1d1d1f;
  margin: 16px 0;
  font-weight: 500;
  border: 1px dashed #d1d1d6;
}

.default-password {
  font-size: 18px;
  font-weight: 700;
  color: #ff9500;
  letter-spacing: 1px;
}

.info-text {
  font-size: 13px;
  color: #86868b;
  line-height: 1.5;
  margin-bottom: 24px;
}

.error-detail {
  color: #ff3b30;
}

.btn-primary-link {
  width: 100%;
  height: 48px;
  background: #34c759;
  color: #fff;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  transition: opacity 0.2s;
  box-shadow: 0 4px 14px rgba(52, 199, 89, 0.3);
}

.btn-primary-link:active {
  opacity: 0.85;
}

.btn-primary-link.btn-error {
  background: #ff3b30;
  box-shadow: 0 4px 14px rgba(255, 59, 48, 0.3);
}
</style>
