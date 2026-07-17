<template>
  <view class="auth-page">
    <view class="auth-header">
      <view class="logo-circle">⚖️</view>
      <text class="auth-title">减脂PK</text>
      <text class="auth-subtitle">加入我们，开启健康之旅</text>
    </view>

    <view class="auth-card">
      <text class="card-header">注册</text>

      <view class="input-group">
        <text class="input-icon">👤</text>
        <input
          v-model="form.username"
          type="text"
          placeholder="用户名(6-8位,小写字母开头)"
          class="auth-input"
          placeholder-class="ph-class"
        />
      </view>
      <view class="input-group">
        <text class="input-icon">📧</text>
        <input
          v-model="form.email"
          type="text"
          placeholder="请输入邮箱"
          class="auth-input"
          placeholder-class="ph-class"
        />
      </view>
      <view class="input-group code-group">
        <text class="input-icon">🔐</text>
        <input
          v-model="form.verification_code"
          type="number"
          placeholder="验证码"
          class="auth-input code-input"
          placeholder-class="ph-class"
          maxlength="6"
        />
        <button
          class="btn-send-code"
          :disabled="codeCooldown > 0 || sendingCode"
          @tap="handleSendCode"
        >
          {{ codeCooldown > 0 ? `${codeCooldown}s` : (sendingCode ? '...' : '获取验证码') }}
        </button>
      </view>
      <view class="input-group">
        <text class="input-icon">🔒</text>
        <input
          v-model="form.password"
          :password="true"
          placeholder="密码(至少8位,含两种字符类型)"
          class="auth-input"
          placeholder-class="ph-class"
        />
      </view>
      <view class="input-group">
        <text class="input-icon">🔒</text>
        <input
          v-model="form.confirm_password"
          :password="true"
          placeholder="请确认密码"
          class="auth-input"
          placeholder-class="ph-class"
        />
      </view>

      <text v-if="errorMsg" class="error-msg">{{ errorMsg }}</text>
      <text v-if="successMsg" class="success-msg">{{ successMsg }}</text>

      <button class="btn-primary" :disabled="loading" @tap="handleRegister">
        {{ loading ? '注册中...' : '注 册' }}
      </button>

      <view class="auth-footer">
        <text class="footer-text">已有账号？</text>
        <text class="link" @tap="goLogin">返回登录</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { reactive, ref, onUnmounted } from 'vue'
import { onUnload } from '@dcloudio/uni-app'
import { useAuthStore } from '../../stores/auth'
import api from '../../api'

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
onUnload(() => {
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
    successMsg.value = res.data?.message || '验证码已发送，请查收邮箱'
    codeCooldown.value = 60
    cooldownTimer = setInterval(() => {
      codeCooldown.value--
      if (codeCooldown.value <= 0) {
        clearInterval(cooldownTimer)
      }
    }, 1000)
  } catch (e) {
    const detail = e?.response?.data?.detail || e?.data?.detail
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
    uni.reLaunch({ url: '/pages/login/index' })
  } catch (e) {
    const detail = e?.response?.data?.detail || e?.data?.detail
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

function goLogin() {
  uni.navigateBack({ fail: () => {
    uni.reLaunch({ url: '/pages/login/index' })
  }})
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #007aff 0%, #5ac8fa 40%, #f5f5f7 70%);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 100rpx 40rpx 80rpx;
}

.auth-header {
  text-align: center;
  margin-bottom: 48rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.logo-circle {
  width: 160rpx;
  height: 160rpx;
  background: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 80rpx;
  margin-bottom: 32rpx;
  box-shadow: 0 16rpx 48rpx rgba(0, 0, 0, 0.1);
}

.auth-title {
  font-size: 56rpx;
  font-weight: 700;
  color: #fff;
  letter-spacing: 4rpx;
}

.auth-subtitle {
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.85);
  margin-top: 12rpx;
}

.auth-card {
  width: 100%;
  background: #fff;
  border-radius: 36rpx;
  padding: 56rpx 48rpx;
  box-shadow: 0 16rpx 64rpx rgba(0, 0, 0, 0.08);
}

.card-header {
  font-size: 44rpx;
  font-weight: 700;
  color: #1d1d1f;
  margin-bottom: 48rpx;
  text-align: center;
  display: block;
}

.input-group {
  display: flex;
  align-items: center;
  background: #f5f5f7;
  border-radius: 28rpx;
  padding: 0 28rpx;
  margin-bottom: 28rpx;
  height: 100rpx;
  transition: all 0.2s;
}

.input-group:focus-within {
  background: #eef4ff;
  box-shadow: 0 0 0 4rpx #007aff;
}

.code-group {
  gap: 16rpx;
  padding-right: 16rpx;
}

.input-icon {
  font-size: 36rpx;
  margin-right: 20rpx;
  opacity: 0.6;
}

.auth-input {
  flex: 1;
  height: 100rpx;
  font-size: 32rpx;
  color: #1d1d1f;
}

.code-input {
  min-width: 0;
}

.ph-class {
  color: #aeaeb2;
}

.btn-send-code {
  flex-shrink: 0;
  height: 76rpx;
  padding: 0 24rpx;
  background: #007aff;
  color: #fff;
  border: none;
  border-radius: 20rpx;
  font-size: 26rpx;
  font-weight: 600;
  white-space: nowrap;
  line-height: 76rpx;
}

.btn-send-code[disabled] {
  opacity: 0.5;
  background: #007aff;
  color: #fff;
}

.error-msg {
  color: #ff3b30;
  font-size: 26rpx;
  margin-bottom: 24rpx;
  text-align: center;
  display: block;
}

.success-msg {
  color: #34c759;
  font-size: 26rpx;
  margin-bottom: 24rpx;
  text-align: center;
  display: block;
}

.btn-primary {
  width: 100%;
  height: 100rpx;
  background: #007aff;
  color: #fff;
  border-radius: 28rpx;
  font-size: 34rpx;
  font-weight: 600;
  margin-top: 16rpx;
  border: none;
  line-height: 100rpx;
}

.btn-primary[disabled] {
  opacity: 0.5;
  background: #007aff;
  color: #fff;
}

.auth-footer {
  text-align: center;
  margin-top: 40rpx;
  font-size: 28rpx;
  color: #86868b;
  display: flex;
  align-items: center;
  justify-content: center;
}

.footer-text {
  color: #86868b;
}

.link {
  color: #007aff;
  font-weight: 600;
}
</style>
