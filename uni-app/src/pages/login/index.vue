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

    <!-- Profile completion sheet (shown after first wx login) -->
    <view v-if="showProfileSheet" class="sheet-backdrop" @tap="skipProfileSheet"></view>
    <view v-if="showProfileSheet" class="profile-sheet">
      <view class="sheet-header">
        <text class="sheet-title">完善资料</text>
        <view class="sheet-close" @tap="skipProfileSheet">✕</view>
      </view>
      <text class="sheet-hint">设置你的昵称和头像，朋友才能认出你</text>

      <view class="avatar-row">
        <button class="avatar-chooser" open-type="chooseAvatar" @chooseavatar="onChooseAvatar">
          <image v-if="avatarTempPath" :src="avatarTempPath" class="avatar-img" mode="aspectFill" />
          <view v-else class="avatar-placeholder"><text class="cam-icon">📷</text></view>
        </button>
        <text class="avatar-tip">点击获取微信头像</text>
      </view>

      <view class="nickname-row">
        <text class="input-icon">👤</text>
        <input
          v-model="tempNickname"
          type="nickname"
          placeholder="点击获取微信昵称"
          class="nickname-input"
          placeholder-class="ph-class"
          @input="onNicknameInput"
          @blur="onNicknameBlur"
          @change="onNicknameChange"
        />
      </view>

      <button class="btn-primary" :disabled="profileSaving" @tap="saveProfile">
        {{ profileSaving ? '保存中...' : '保存并进入' }}
      </button>
      <text class="skip-link" @tap="skipProfileSheet">稍后再说</text>
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
    // If new user with default nickname, prompt to complete profile
    const u = res.user
    if (!u || u.nickname === '微信用户' || !u.nickname) {
      showProfileSheet.value = true
      return
    }
    if (u.role === 'admin') {
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

// --- Profile completion sheet ---
const showProfileSheet = ref(false)
const avatarTempPath = ref('')
const tempNickname = ref('')
const profileSaving = ref(false)

function onChooseAvatar(e) {
  // WeChat returns a temp file path in e.detail.avatarUrl
  if (e?.detail?.avatarUrl) {
    avatarTempPath.value = e.detail.avatarUrl
  }
}

function onNicknameInput(e) {
  if (e?.detail?.value) {
    tempNickname.value = e.detail.value
  }
}

function onNicknameBlur(e) {
  if (e?.detail?.value) {
    tempNickname.value = e.detail.value
  }
}

function onNicknameChange(e) {
  if (e?.detail?.value) {
    tempNickname.value = e.detail.value
  }
}

async function saveProfile() {
  if (!avatarTempPath.value && !tempNickname.value.trim()) {
    uni.showToast({ title: '请至少设置头像或昵称', icon: 'none' })
    return
  }
  profileSaving.value = true
  try {
    // 1. Upload avatar if chosen
    if (avatarTempPath.value) {
      try {
        await authStore.uploadAvatar(avatarTempPath.value)
      } catch (e) {
        const detail = e?.response?.data?.detail
        const reason = (typeof detail === 'string' && detail) || e?.message || ''
        console.error('[avatar upload failed]', e)
        uni.showToast({ title: reason ? `头像上传失败: ${reason}` : '头像上传失败', icon: 'none', duration: 3000 })
      }
    }
    // 2. Update nickname if provided
    if (tempNickname.value && tempNickname.value.trim()) {
      try {
        await authStore.updateProfile({ nickname: tempNickname.value.trim() })
      } catch (e) {
        uni.showToast({ title: '昵称保存失败', icon: 'none' })
      }
    }
    showProfileSheet.value = false
    // Navigate to dashboard
    if (authStore.user?.role === 'admin') {
      uni.reLaunch({ url: '/pages/dashboard/index' })
    } else {
      uni.switchTab({ url: '/pages/dashboard/index' })
    }
  } finally {
    profileSaving.value = false
  }
}

function skipProfileSheet() {
  showProfileSheet.value = false
  if (authStore.user?.role === 'admin') {
    uni.reLaunch({ url: '/pages/dashboard/index' })
  } else {
    uni.switchTab({ url: '/pages/dashboard/index' })
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

/* Bottom Sheet / Modal for Profile Completion */
.sheet-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 998;
  backdrop-filter: blur(4px);
}

.profile-sheet {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  background: #ffffff;
  border-radius: 40rpx 40rpx 0 0;
  padding: 48rpx 40rpx 60rpx;
  z-index: 999;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 -10rpx 40rpx rgba(0, 0, 0, 0.15);
  animation: slideUp 0.3s cubic-bezier(0.25, 1, 0.5, 1);
}

@keyframes slideUp {
  from {
    transform: translateY(100%);
  }
  to {
    transform: translateY(0);
  }
}

.sheet-header {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12rpx;
}

.sheet-title {
  font-size: 38rpx;
  font-weight: 700;
  color: #1d1d1f;
}

.sheet-close {
  font-size: 36rpx;
  color: #86868b;
  padding: 8rpx 16rpx;
}

.sheet-hint {
  font-size: 26rpx;
  color: #86868b;
  margin-bottom: 40rpx;
  align-self: flex-start;
}

.avatar-row {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 40rpx;
}

.avatar-chooser {
  width: 160rpx;
  height: 160rpx;
  border-radius: 50%;
  padding: 0;
  margin: 0;
  background: #f0f0f2;
  border: 4rpx solid #e5e5ea;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.06);
}

.avatar-chooser::after {
  border: none;
}

.avatar-img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #eef4ff;
}

.cam-icon {
  font-size: 64rpx;
}

.avatar-tip {
  font-size: 24rpx;
  color: #007aff;
  margin-top: 16rpx;
  font-weight: 500;
}

.nickname-row {
  width: 100%;
  display: flex;
  align-items: center;
  background: #f5f5f7;
  border-radius: 28rpx;
  padding: 0 28rpx;
  margin-bottom: 36rpx;
  height: 100rpx;
}

.nickname-input {
  flex: 1;
  height: 100rpx;
  font-size: 32rpx;
  color: #1d1d1f;
}

.skip-link {
  font-size: 28rpx;
  color: #86868b;
  margin-top: 28rpx;
  padding: 12rpx 24rpx;
}
</style>

