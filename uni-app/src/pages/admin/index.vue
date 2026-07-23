<template>
  <view class="page" :class="{ 'dark-mode': isDark }">
    <!-- Header -->
    <view class="page-header">
      <text class="page-title">管理中心</text>
    </view>

    <!-- Stats Cards -->
    <view class="stats-grid">
      <view class="stat-card">
        <text class="stat-icon">👥</text>
        <text class="stat-value">{{ users.length }}</text>
        <text class="stat-label">总用户数</text>
      </view>
      <view class="stat-card">
        <text class="stat-icon">✅</text>
        <text class="stat-value">{{ activeUsers }}</text>
        <text class="stat-label">已完善资料</text>
      </view>
    </view>

    <!-- User List -->
    <text class="section-title">用户列表</text>
    <view class="user-list">
      <view
        v-for="u in users"
        :key="u.id"
        class="user-item"
        @tap="viewUserDetail(u)"
      >
        <view class="user-avatar">
          <image v-if="getAvatarUrl(u)" :src="getAvatarUrl(u)" class="avatar-img" mode="aspectFill" />
          <text v-else>{{ getInitial(u.nickname || u.username) }}</text>
        </view>
        <view class="user-info">
          <view class="user-name-row">
            <text class="user-name">{{ u.nickname || u.username }}</text>
            <text v-if="u.role === 'admin'" class="admin-tag">管理员</text>
          </view>
          <text class="user-meta">@{{ u.username }} · {{ u.email || '未绑定邮箱' }}</text>
          <text class="user-meta">注册于 {{ formatDate(u.created_at) }}</text>
        </view>
        <text class="arrow">›</text>
      </view>
      <view v-if="users.length === 0" class="empty-state">
        <text>暂无用户</text>
      </view>
    </view>

    <!-- User Detail Sheet -->
    <view v-if="showDetailSheet" class="bottom-sheet-backdrop" @tap="closeDetailSheet"></view>
    <view v-if="showDetailSheet" class="bottom-sheet">
      <view class="sheet-header">
        <text class="sheet-title">{{ selectedUser?.nickname || selectedUser?.username }}</text>
        <view class="sheet-close" @tap="closeDetailSheet">✕</view>
      </view>
      <scroll-view scroll-y class="detail-scroll" v-if="userDetail">
        <!-- User Profile -->
        <view class="detail-section">
          <text class="detail-label">基本信息</text>
          <view class="detail-grid">
            <view class="detail-item">
              <text class="di-label">用户名</text>
              <text class="di-value">{{ selectedUser?.username }}</text>
            </view>
            <view class="detail-item">
              <text class="di-label">邮箱</text>
              <text class="di-value">{{ selectedUser?.email || '-' }}</text>
            </view>
            <view class="detail-item">
              <text class="di-label">性别</text>
              <text class="di-value">{{ selectedUser?.gender === 1 ? '男' : selectedUser?.gender === 0 ? '女' : '-' }}</text>
            </view>
            <view class="detail-item">
              <text class="di-label">身高</text>
              <text class="di-value">{{ selectedUser?.height ? selectedUser.height + 'cm' : '-' }}</text>
            </view>
            <view class="detail-item">
              <text class="di-label">目标体重</text>
              <text class="di-value">{{ selectedUser?.target_weight ? selectedUser.target_weight + 'kg' : '-' }}</text>
            </view>
            <view class="detail-item">
              <text class="di-label">每日热量</text>
              <text class="di-value">{{ selectedUser?.daily_calorie_goal || '-' }}kcal</text>
            </view>
          </view>
        </view>

        <!-- Weight Stats -->
        <view class="detail-section" v-if="userDetail.weight_history?.length">
          <text class="detail-label">体重记录（最近{{ userDetail.weight_history.length }}条）</text>
          <view class="weight-list">
            <view v-for="w in userDetail.weight_history" :key="w.id" class="weight-row">
              <text class="wr-date">{{ formatDate(w.logged_at) }}</text>
              <text class="wr-value">{{ w.weight }}kg</text>
              <text class="wr-note" v-if="w.note">{{ w.note }}</text>
            </view>
          </view>
        </view>

        <!-- Calorie Summary -->
        <view class="detail-section" v-if="userDetail.calorie_summary">
          <text class="detail-label">今日饮食</text>
          <view class="detail-grid">
            <view class="detail-item">
              <text class="di-label">已摄入</text>
              <text class="di-value">{{ userDetail.calorie_summary.consumed || 0 }}kcal</text>
            </view>
            <view class="detail-item">
              <text class="di-label">目标</text>
              <text class="di-value">{{ userDetail.calorie_summary.goal || 0 }}kcal</text>
            </view>
          </view>
        </view>
      </scroll-view>
      <view v-else class="loading-state">
        <text>加载中...</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onLoad, onShow } from '@dcloudio/uni-app'
import api from '../../api'
import { useAuthStore } from '../../stores/auth'
import { useDarkMode } from '../../utils/theme'

const authStore = useAuthStore()
const { isDark, initDark } = useDarkMode()
const users = ref([])
const loading = ref(true)

const showDetailSheet = ref(false)
const selectedUser = ref(null)
const userDetail = ref(null)

const BASE_URL = 'https://yoyo678.cc.cd'

const activeUsers = computed(() => {
  return users.value.filter(u => u.height && u.target_weight).length
})

function getInitial(name) {
  if (!name) return '?'
  return name.charAt(0).toUpperCase()
}

function getAvatarUrl(user) {
  const av = user?.avatar
  if (!av) return ''
  if (av.startsWith('http')) return av
  return BASE_URL + av
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours()}:${String(d.getMinutes()).padStart(2, '0')}`
}

async function fetchUsers() {
  loading.value = true
  try {
    const res = await api.get('/admin/users')
    users.value = res.data || []
  } catch (e) {
    uni.showToast({ title: '获取用户列表失败', icon: 'none' })
    users.value = []
  } finally {
    loading.value = false
  }
}

async function viewUserDetail(user) {
  selectedUser.value = user
  showDetailSheet.value = true
  userDetail.value = null
  try {
    const res = await api.get(`/admin/users/${user.id}/dashboard`)
    userDetail.value = res.data
  } catch (e) {
    uni.showToast({ title: '获取用户详情失败', icon: 'none' })
  }
}

function closeDetailSheet() {
  showDetailSheet.value = false
  selectedUser.value = null
  userDetail.value = null
}

onShow(async () => {
  try { uni.hideTabBar({ animation: false }) } catch (e) {}
  initDark()
  uni.setNavigationBarColor({
    frontColor: '#ffffff',
    backgroundColor: isDark.value ? '#1a1a1a' : '#007aff',
  })
})

onLoad(async () => {
  await fetchUsers()
})
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: var(--bg-color);
  padding-bottom: calc(150rpx + env(safe-area-inset-bottom));
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24rpx 32rpx;
  background: var(--card-bg);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 50;
}

.page-title {
  font-size: 40rpx;
  font-weight: 700;
  color: var(--text-primary);
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16rpx;
  padding: 120rpx 32rpx 16rpx;
}

.stat-card {
  background: var(--card-bg);
  border-radius: 24rpx;
  padding: 28rpx;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-icon {
  font-size: 44rpx;
  margin-bottom: 8rpx;
}

.stat-value {
  font-size: 48rpx;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-label {
  font-size: 24rpx;
  color: var(--text-secondary);
  margin-top: 4rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: 600;
  margin: 32rpx 32rpx 16rpx;
  color: var(--text-primary);
  display: block;
}

.user-list {
  margin: 0 32rpx;
  background: var(--card-bg);
  border-radius: 24rpx;
  overflow: hidden;
}

.user-item {
  display: flex;
  align-items: center;
  gap: 20rpx;
  padding: 24rpx 28rpx;
  border-bottom: 2rpx solid var(--border-color);
}

.user-item:last-child {
  border-bottom: none;
}

.user-avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #007aff, #5ac8fa);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32rpx;
  font-weight: 600;
  flex-shrink: 0;
  overflow: hidden;
}

.avatar-img {
  width: 100%;
  height: 100%;
}

.user-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.user-name-row {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.user-name {
  font-size: 30rpx;
  font-weight: 600;
  color: var(--text-primary);
}

.admin-tag {
  font-size: 20rpx;
  color: #ff9500;
  background: #fff8e6;
  padding: 2rpx 12rpx;
  border-radius: 12rpx;
}

.user-meta {
  font-size: 24rpx;
  color: var(--text-secondary);
  margin-top: 4rpx;
}

.arrow {
  font-size: 36rpx;
  color: var(--text-tertiary);
}

.empty-state {
  text-align: center;
  padding: 80rpx 40rpx;
  color: var(--text-tertiary);
  font-size: 28rpx;
}

/* Bottom Sheet */
.bottom-sheet-backdrop {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 200;
}

.bottom-sheet {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: var(--card-bg);
  border-radius: 40rpx 40rpx 0 0;
  padding: 40rpx;
  z-index: 201;
  max-height: 85vh;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from { transform: translateY(100%); }
  to { transform: translateY(0); }
}

.sheet-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32rpx;
}

.sheet-title {
  font-size: 36rpx;
  font-weight: 600;
  color: var(--text-primary);
}

.sheet-close {
  width: 60rpx;
  height: 60rpx;
  border-radius: 50%;
  background: #f5f5f7;
  font-size: 28rpx;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
}

.detail-scroll {
  max-height: 70vh;
}

.detail-section {
  margin-bottom: 32rpx;
}

.detail-label {
  font-size: 28rpx;
  font-weight: 600;
  color: var(--text-primary);
  display: block;
  margin-bottom: 16rpx;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16rpx;
}

.detail-item {
  background: #f5f5f7;
  border-radius: 16rpx;
  padding: 16rpx 20rpx;
}

.di-label {
  font-size: 22rpx;
  color: var(--text-secondary);
  display: block;
}

.di-value {
  font-size: 28rpx;
  font-weight: 600;
  color: var(--text-primary);
  margin-top: 4rpx;
  display: block;
}

.weight-list {
  background: #f5f5f7;
  border-radius: 16rpx;
  overflow: hidden;
}

.weight-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 16rpx 20rpx;
  border-bottom: 2rpx solid #e5e5ea;
}

.weight-row:last-child {
  border-bottom: none;
}

.wr-date {
  font-size: 24rpx;
  color: var(--text-secondary);
  width: 160rpx;
}

.wr-value {
  font-size: 28rpx;
  font-weight: 600;
  color: var(--text-primary);
}

.wr-note {
  font-size: 22rpx;
  color: var(--text-tertiary);
  flex: 1;
  text-align: right;
}

.loading-state {
  text-align: center;
  padding: 80rpx;
  color: var(--text-secondary);
  font-size: 28rpx;
}

</style>
