<template>
  <view class="auth-page">
    <view class="auth-header">
      <view class="logo-circle">⚖️</view>
      <text class="auth-title">减脂PK</text>
      <text class="auth-subtitle">健康减脂，快乐对战</text>
    </view>

    <view class="auth-card">
      <text class="card-header">登录</text>

      <view class="input-group">
        <text class="input-icon">👤</text>
        <input
          v-model="form.username"
          type="text"
          placeholder="请输入用户名"
          class="auth-input"
          placeholder-class="ph-class"
        />
      </view>
      <view class="input-group">
        <text class="input-icon">🔒</text>
        <input
          v-model="form.password"
          :password="true"
          placeholder="请输入密码"
          class="auth-input"
          placeholder-class="ph-class"
        />
      </view>

      <text v-if="errorMsg" class="error-msg">{{ errorMsg }}</text>

      <button class="btn-primary" :disabled="loading" @tap="handleLogin">
        {{ loading ? '登录中...' : '登 录' }}
      </button>

      <view class="divider">
        <view class="divider-line"></view>
        <text class="divider-text">或</text>
        <view class="divider-line"></view>
      </view>

      <button class="btn-wechat" :disabled="wxLoading" @tap="handleWxLogin">
        <text class="wx-icon">💬</text>
        <text>{{ wxLoading ? '登录中...' : '微信一键登录' }}</text>
      </button>

      <view class="auth-footer">
        <text class="footer-text">还没有账号？</text>
        <text class="link" @tap="goRegister">立即注册</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useAuthStore } from '../../stores/auth'

const authStore = useAuthStore()

const form = reactive({
  username: '',
  password: '',
})
const errorMsg = ref('')
const loading = ref(false)
const wxLoading = ref(false)

async function handleLogin() {
  if (!form.username || !form.password) {
    errorMsg.value = '请输入用户名和密码'
    return
  }
  loading.value = true
  errorMsg.value = ''
  try {
    const res = await authStore.login(form.username, form.password)
    if (res.user?.role === 'admin') {
      uni.reLaunch({ url: '/pages/dashboard/index' })
    } else {
      uni.switchTab({ url: '/pages/dashboard/index' })
    }
  } catch (e) {
    const detail = e?.response?.data?.detail || e?.data?.detail
    if (typeof detail === 'string') {
      errorMsg.value = detail
    } else if (Array.isArray(detail)) {
      errorMsg.value = detail.map(d => d.msg || JSON.stringify(d)).join('; ')
    } else {
      errorMsg.value = '用户名或密码错误'
    }
  } finally {
    loading.value = false
  }
}

async function handleWxLogin() {
  wxLoading.value = true
  errorMsg.value = ''
  try {
    // uni.login returns a temporary code that the backend exchanges for openid
    const loginRes = await new Promise((resolve, reject) => {
      uni.login({ provider: 'weixin', success: resolve, fail: reject })
    })
    const code = loginRes.code
    if (!code) {
      errorMsg.value = '未获取到微信登录凭证'
      return
    }
    const res = await authStore.wxLogin(code)
    if (res.user?.role === 'admin') {
      uni.reLaunch({ url: '/pages/dashboard/index' })
    } else {
      uni.switchTab({ url: '/pages/dashboard/index' })
    }
  } catch (e) {
    const detail = e?.response?.data?.detail || e?.data?.detail
    if (typeof detail === 'string') {
      errorMsg.value = detail
    } else if (typeof e?.errMsg === 'string' && e.errMsg.includes('login:fail')) {
      errorMsg.value = '微信登录取消或失败'
    } else {
      errorMsg.value = e?.message || '微信登录失败，请重试'
    }
  } finally {
    wxLoading.value = false
  }
}

function goRegister() {
  uni.navigateTo({ url: '/pages/register/index' })
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #007aff 0%, #5ac8fa 40%, #f5f5f7 70%);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 120rpx 40rpx 80rpx;
}

.auth-header {
  text-align: center;
  margin-bottom: 60rpx;
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

.ph-class {
  color: #aeaeb2;
}

.error-msg {
  color: #ff3b30;
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

.divider {
  display: flex;
  align-items: center;
  margin: 36rpx 0 24rpx;
}

.divider-line {
  flex: 1;
  height: 2rpx;
  background: #e5e5ea;
}

.divider-text {
  font-size: 26rpx;
  color: #aeaeb2;
  margin: 0 20rpx;
}

.btn-wechat {
  width: 100%;
  height: 100rpx;
  background: #07c160;
  color: #fff;
  border-radius: 28rpx;
  font-size: 34rpx;
  font-weight: 600;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-wechat[disabled] {
  opacity: 0.5;
  background: #07c160;
  color: #fff;
}

.wx-icon {
  margin-right: 12rpx;
  font-size: 36rpx;
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
