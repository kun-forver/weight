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
            placeholder="用户名(6-8位,小写字母开头)"
            class="auth-input"
            autocomplete="username"
          />
        </div>
        <div class="input-group">
          <span class="input-icon">📧</span>
          <input
            v-model="form.email"
            type="email"
            placeholder="请输入邮箱"
            class="auth-input"
            autocomplete="email"
          />
        </div>
        <div class="input-group code-group">
          <span class="input-icon">🔐</span>
          <input
            v-model="form.verification_code"
            type="text"
            placeholder="验证码"
            class="auth-input code-input"
            maxlength="6"
          />
          <button
            type="button"
            class="btn-send-code"
            :disabled="codeCooldown > 0 || sendingCode"
            @click="handleSendCode"
          >
            {{ codeCooldown > 0 ? `${codeCooldown}s` : (sendingCode ? '...' : '获取验证码') }}
          </button>
        </div>
        <div class="input-group">
          <span class="input-icon">🔒</span>
          <input
            v-model="form.password"
            type="password"
            placeholder="密码(至少8位,含两种字符类型)"
            class="auth-input"
            autocomplete="new-password"
          />
        </div>
        <div class="input-group">
          <span class="input-icon">🔒</span>
          <input
            v-model="form.confirm_password"
            type="password"
            placeholder="请确认密码"
            class="auth-input"
            autocomplete="new-password"
          />
        </div>

        <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>
        <p v-if="successMsg" class="success-msg">{{ successMsg }}</p>

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
import { reactive, ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../api'

const router = useRouter()
const authStore = useAuthStore()

const form = reactive({
  username: '',
  email: '',
  verification_code: '',
  password: '',
  confirm_password: '',
})
const errorMsg = ref('')
const successMsg = ref('')
const loading = ref(false)
const sendingCode = ref(false)
const codeCooldown = ref(0)
let cooldownTimer = null

onUnmounted(() => {
  if (cooldownTimer) clearInterval(cooldownTimer)
})

async function handleSendCode() {
  if (!form.email) {
    errorMsg.value = '请先输入邮箱'
    return
  }
  errorMsg.value = ''
  successMsg.value = ''
  sendingCode.value = true
  try {
    const res = await api.post('/auth/send-code', { email: form.email })
    successMsg.value = res.data.message || '验证码已发送，请查收邮箱'
    codeCooldown.value = 60
    cooldownTimer = setInterval(() => {
      codeCooldown.value--
      if (codeCooldown.value <= 0) {
        clearInterval(cooldownTimer)
      }
    }, 1000)
  } catch (e) {
    const detail = e.response?.data?.detail
    errorMsg.value = typeof detail === 'string' ? detail : '验证码发送失败，请稍后重试'
  } finally {
    sendingCode.value = false
  }
}

async function handleRegister() {
  if (!form.username || !form.email || !form.verification_code || !form.password) {
    errorMsg.value = '请填写所有必填信息'
    return
  }
  if (form.password !== form.confirm_password) {
    errorMsg.value = '两次输入的密码不一致'
    return
  }
  loading.value = true
  errorMsg.value = ''
  successMsg.value = ''
  try {
    await authStore.register(form)
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

.code-group {
  gap: 8px;
  padding-right: 8px;
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

.code-input {
  min-width: 0;
}

.auth-input::placeholder {
  color: #aeaeb2;
}

.btn-send-code {
  flex-shrink: 0;
  height: 38px;
  padding: 0 12px;
  background: #007aff;
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn-send-code:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.error-msg {
  color: #ff3b30;
  font-size: 13px;
  margin-bottom: 12px;
  text-align: center;
}

.success-msg {
  color: #34c759;
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
