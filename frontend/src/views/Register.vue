<template>
  <div class="auth-page">
    <div class="auth-header">
      <div class="logo-circle">⚖️</div>
      <h1 class="auth-title">减脂PK</h1>
      <p class="auth-subtitle">加入我们，开启健康之旅</p>
    </div>

    <div class="auth-card">
      <div class="card-header">注册</div>
      <form @submit.prevent="handleRegister">
        <div class="input-group">
          <span class="input-icon">👤</span>
          <input
            v-model="form.username"
            type="text"
            placeholder="请输入用户名"
            class="auth-input"
            autocomplete="username"
          />
        </div>
        <div class="input-group">
          <span class="input-icon">🔒</span>
          <input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            class="auth-input"
            autocomplete="new-password"
          />
        </div>
        <div class="input-group">
          <span class="input-icon">✨</span>
          <input
            v-model="form.nickname"
            type="text"
            placeholder="请输入昵称"
            class="auth-input"
          />
        </div>

        <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>

        <button type="submit" class="btn-primary" :disabled="loading">
          {{ loading ? '注册中...' : '注 册' }}
        </button>
      </form>

      <div class="auth-footer">
        已有账号？<router-link to="/login" class="link">返回登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = reactive({
  username: '',
  password: '',
  nickname: '',
})
const errorMsg = ref('')
const loading = ref(false)

async function handleRegister() {
  if (!form.username || !form.password || !form.nickname) {
    errorMsg.value = '请填写所有信息'
    return
  }
  loading.value = true
  errorMsg.value = ''
  try {
    await authStore.register(form.username, form.password, form.nickname)
    router.push('/')
  } catch (e) {
    const detail = e.response?.data?.detail
    if (typeof detail === 'string') {
      errorMsg.value = detail
    } else if (Array.isArray(detail)) {
      errorMsg.value = detail.map(d => d.msg || JSON.stringify(d)).join('; ')
    } else {
      errorMsg.value = '注册失败，请稍后重试'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #007aff 0%, #5ac8fa 40%, #f5f5f7 70%);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 50px 20px 40px;
}

.auth-header {
  text-align: center;
  margin-bottom: 24px;
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

.card-header {
  font-size: 22px;
  font-weight: 700;
  color: #1d1d1f;
  margin-bottom: 24px;
  text-align: center;
}

.input-group {
  display: flex;
  align-items: center;
  background: #f5f5f7;
  border-radius: 14px;
  padding: 0 14px;
  margin-bottom: 14px;
  height: 50px;
  transition: all 0.2s;
}

.input-group:focus-within {
  background: #eef4ff;
  box-shadow: 0 0 0 2px #007aff;
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
  margin-bottom: 12px;
  text-align: center;
}

.btn-primary {
  width: 100%;
  height: 50px;
  background: #007aff;
  color: #fff;
  border-radius: 14px;
  font-size: 17px;
  font-weight: 600;
  margin-top: 8px;
  transition: opacity 0.2s;
  border: none;
  cursor: pointer;
}

.btn-primary:active {
  opacity: 0.85;
}

.btn-primary:disabled {
  opacity: 0.5;
}

.auth-footer {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
  color: #86868b;
}

.link {
  color: #007aff;
  text-decoration: none;
  font-weight: 600;
}
</style>
