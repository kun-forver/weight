<template>
  <view class="page">
    <!-- Header -->
    <view class="dash-header">
      <view class="header-left">
        <view class="avatar">{{ userInitial }}</view>
        <view class="greeting">
          <text class="hello">{{ greeting }}，{{ userNickname }}</text>
          <text class="date-text">{{ formattedDate }}</text>
        </view>
      </view>
      <view class="header-right">
        <view class="icon-btn" @tap="goToProfile">⚙️</view>
      </view>
    </view>

    <view v-if="loading" class="loading-overlay">
      <text class="spinner">⏳</text>
    </view>

    <view v-if="data" class="dash-content">
      <!-- Calorie Ring -->
      <view class="calorie-section">
        <CalorieRing
          :consumed="data.calorie_summary?.consumed || 0"
          :goal="data.calorie_summary?.goal || 2000"
        />
      </view>

      <!-- 3 Stat Cards -->
      <view class="stat-row">
        <view class="stat-card stat-green">
          <text class="stat-label">剩余可吃</text>
          <text class="stat-value">{{ data.calorie_summary?.remaining || 0 }}</text>
          <text class="stat-unit">kcal</text>
        </view>
        <view class="stat-card stat-orange">
          <text class="stat-label">已摄入</text>
          <text class="stat-value">{{ data.calorie_summary?.consumed || 0 }}</text>
          <text class="stat-unit">kcal</text>
        </view>
        <view class="stat-card stat-blue">
          <text class="stat-label">运动消耗</text>
          <text class="stat-value">{{ data.calorie_summary?.exercise || 0 }}</text>
          <text class="stat-unit">kcal</text>
        </view>
      </view>

      <!-- Quick Action Grid -->
      <view class="quick-action-grid">
        <view class="action-tile" @tap="goToWeight">
          <text class="tile-icon">⚖️</text>
          <text class="tile-label">记录体重</text>
        </view>
        <view class="action-tile" @tap="goToFood">
          <text class="tile-icon">🍎</text>
          <text class="tile-label">记录饮食</text>
        </view>
        <view class="action-tile" @tap="goToPK">
          <text class="tile-icon">⚔️</text>
          <text class="tile-label">减脂对战</text>
        </view>
        <view class="action-tile" @tap="goToProfile">
          <text class="tile-icon">👤</text>
          <text class="tile-label">个人主页</text>
        </view>
      </view>

      <!-- Nutrition Progress -->
      <view class="card nutrition-card">
        <view class="card-title-row">
          <text class="card-title">营养分析</text>
          <text class="card-subtitle">今日摄入比例</text>
        </view>
        <view class="nutrition-item">
          <view class="nutri-header">
            <text class="nutri-name">🥩 蛋白质</text>
            <text class="nutri-values">{{ nutrition.protein.current }}g / {{ nutrition.protein.target }}g</text>
          </view>
          <view class="progress-bar-bg">
            <view class="progress-bar-fill protein-bar" :style="{ width: progressPct(nutrition.protein.current, nutrition.protein.target) }"></view>
          </view>
        </view>
        <view class="nutrition-item">
          <view class="nutri-header">
            <text class="nutri-name">🍞 碳水化合物</text>
            <text class="nutri-values">{{ nutrition.carbs.current }}g / {{ nutrition.carbs.target }}g</text>
          </view>
          <view class="progress-bar-bg">
            <view class="progress-bar-fill carbs-bar" :style="{ width: progressPct(nutrition.carbs.current, nutrition.carbs.target) }"></view>
          </view>
        </view>
        <view class="nutrition-item">
          <view class="nutri-header">
            <text class="nutri-name">🥑 脂肪</text>
            <text class="nutri-values">{{ nutrition.fat.current }}g / {{ nutrition.fat.target }}g</text>
          </view>
          <view class="progress-bar-bg">
            <view class="progress-bar-fill fat-bar" :style="{ width: progressPct(nutrition.fat.current, nutrition.fat.target) }"></view>
          </view>
        </view>
      </view>

      <!-- Weight Card -->
      <view class="card weight-card" v-if="weightData.current && weightData.current !== '-'">
        <view class="weight-card-bg"></view>
        <view class="weight-card-content">
          <view class="weight-top">
            <view class="weight-left">
              <text class="weight-label">最新体重</text>
              <view class="weight-value-row">
                <text class="weight-value">{{ weightData.current }}</text>
                <text class="weight-unit">kg</text>
              </view>
              <text class="weight-change" :class="weightChangeClass" v-if="weightData.change !== null">
                {{ weightChangeIcon }} {{ Math.abs(weightData.change || 0).toFixed(1) }}kg vs 昨日
              </text>
            </view>
            <view class="weight-right">
              <view class="weight-stat">
                <text class="ws-label">本月减重</text>
                <text class="ws-value">{{ weightData.monthly_loss || 0 }}kg</text>
              </view>
              <view class="weight-stat">
                <text class="ws-label">目标体重</text>
                <text class="ws-value">{{ weightData.target || '-' }}kg</text>
              </view>
            </view>
          </view>
          <!-- Progress to target -->
          <view class="target-progress">
            <text class="tp-label">距目标进度</text>
            <view class="tp-bar-bg">
              <view class="tp-bar-fill" :style="{ width: (weightData.target_progress || 0) + '%' }"></view>
            </view>
            <text class="tp-pct">{{ Math.round(weightData.target_progress || 0) }}%</text>
          </view>
        </view>
      </view>

      <!-- Daily reports -->
      <text class="section-title">今日速报</text>

      <!-- Diet summary report -->
      <view class="card summary-report-card" @tap="goToFood">
        <view class="src-icon">🍎</view>
        <view class="src-info">
          <text class="src-title">今日饮食概览</text>
          <view class="src-desc-row">
            <text class="src-desc">已摄入 </text>
            <text class="src-strong">{{ data.calorie_summary?.consumed || 0 }}</text>
            <text class="src-desc"> kcal，剩余可吃 </text>
            <text class="src-strong">{{ Math.max(0, data.calorie_summary?.remaining || 0) }}</text>
            <text class="src-desc"> kcal</text>
          </view>
        </view>
        <text class="src-arrow">›</text>
      </view>

      <!-- PK summary report -->
      <view v-if="data.pk" class="card summary-report-card" @tap="goToPK">
        <view class="src-icon">⚔️</view>
        <view class="src-info">
          <text class="src-title">对战：{{ data.pk.name }}</text>
          <view class="src-desc-row">
            <text class="src-desc">对战进行中 · 剩余 </text>
            <text class="src-strong">{{ Math.max((data.pk.days_total || 0) - (data.pk.days_elapsed || 0), 0) }}</text>
            <text class="src-desc"> 天</text>
          </view>
        </view>
        <text class="src-arrow">›</text>
      </view>
      <view v-else class="card summary-report-card" @tap="goToPK">
        <view class="src-icon">🎯</view>
        <view class="src-info">
          <text class="src-title">暂无进行中的对战</text>
          <text class="src-desc-alone">点击这里，去找好友发起减脂PK挑战吧！</text>
        </view>
        <text class="src-arrow">›</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onShow, onLoad } from '@dcloudio/uni-app'
import api from '../../api'
import { useAuthStore } from '../../stores/auth'
import CalorieRing from '../../components/CalorieRing.vue'

const authStore = useAuthStore()

const loading = ref(true)
const data = ref(null)
const error = ref(null)

const user = computed(() => {
  const stored = uni.getStorageSync('user')
  return authStore.user || (stored ? (typeof stored === 'string' ? JSON.parse(stored) : stored) : {})
})
const userNickname = computed(() => user.value?.nickname || user.value?.username || '小伙伴')
const userInitial = computed(() => {
  const name = user.value?.nickname || user.value?.username || 'U'
  return name.charAt(0).toUpperCase()
})

const greeting = computed(() => {
  const h = new Date().getHours()
  if (h < 6) return '夜深了'
  if (h < 12) return '早上好'
  if (h < 14) return '中午好'
  if (h < 18) return '下午好'
  return '晚上好'
})

const formattedDate = computed(() => {
  const now = new Date()
  const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  return `${now.getMonth() + 1}月${now.getDate()}日 ${weekdays[now.getDay()]}`
})

const nutrition = computed(() => {
  const n = data.value?.nutrition_breakdown || {}
  return {
    protein: { current: n.protein?.current || 0, target: n.protein?.target || 60 },
    carbs: { current: n.carbs?.current || 0, target: n.carbs?.target || 250 },
    fat: { current: n.fat?.current || 0, target: n.fat?.target || 65 },
  }
})

const weightData = computed(() => {
  const w = data.value?.weight || {}
  const current = w.latest || 0
  const target = w.target_weight || 0
  let target_progress = 0
  if (current > 0 && target > 0) {
    if (current <= target) {
      target_progress = 100
    } else {
      const start = target + 5
      const total = start - target
      const done = start - current
      target_progress = Math.max(0, Math.min(100, (done / total) * 100))
    }
  }
  return {
    current: current || '-',
    change: w.change ?? null,
    target: target || '-',
    monthly_loss: Math.abs(w.change || 0).toFixed(1),
    target_progress: target_progress,
  }
})

const weightChangeClass = computed(() => {
  const change = weightData.value.change || 0
  if (change < 0) return 'change-down'
  if (change > 0) return 'change-up'
  return ''
})

const weightChangeIcon = computed(() => {
  const change = weightData.value.change || 0
  if (change < 0) return '↓'
  if (change > 0) return '↑'
  return '→'
})

function progressPct(current, target) {
  if (!target || target <= 0) return '0%'
  return Math.min((current / target) * 100, 100) + '%'
}

function goToFood() {
  uni.switchTab({ url: '/pages/food/index' })
}

function goToWeight() {
  uni.switchTab({ url: '/pages/weight/index' })
}

function goToPK() {
  uni.switchTab({ url: '/pages/pk/index' })
}

function goToProfile() {
  uni.switchTab({ url: '/pages/profile/index' })
}

async function fetchDashboard() {
  loading.value = true
  try {
    const res = await api.get('/dashboard')
    data.value = res.data
  } catch (e) {
    error.value = e
    data.value = {
      calorie_summary: { consumed: 0, remaining: 2000, exercise: 0, goal: 2000 },
      nutrition_breakdown: {
        protein: { current: 0, target: 60 },
        carbs: { current: 0, target: 250 },
        fat: { current: 0, target: 65 },
      },
      weight: { latest: 0, previous: 0, change: 0, target_weight: 0 },
      pk: null,
    }
  } finally {
    loading.value = false
  }
}

onLoad(async () => {
  if (!authStore.user) {
    try {
      await authStore.fetchUser()
    } catch {
      // will redirect via interceptor
    }
  }
  await fetchDashboard()
})

onShow(async () => {
  if (authStore.user && !loading.value) {
    await fetchDashboard()
  }
})
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #f5f5f7;
  padding-bottom: 40rpx;
}

.dash-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24rpx 32rpx;
  background: #fff;
  position: sticky;
  top: 0;
  z-index: 50;
  border-bottom: 1rpx solid #f0f0f2;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #007aff, #5ac8fa);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36rpx;
  font-weight: 600;
}

.greeting {
  display: flex;
  flex-direction: column;
}

.hello {
  font-size: 32rpx;
  font-weight: 600;
  color: #1d1d1f;
}

.date-text {
  font-size: 24rpx;
  color: #86868b;
  margin-top: 4rpx;
}

.header-right {
  display: flex;
}

.icon-btn {
  width: 72rpx;
  height: 72rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36rpx;
  border-radius: 50%;
  background: #f5f5f7;
}

.loading-overlay {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 80rpx 0;
}

.spinner {
  font-size: 48rpx;
}

.calorie-section {
  display: flex;
  justify-content: center;
  padding: 48rpx 0 32rpx;
  background: #fff;
}

.stat-row {
  display: flex;
  gap: 16rpx;
  padding: 0 32rpx;
  margin-bottom: 24rpx;
}

.stat-card {
  flex: 1;
  background: #fff;
  border-radius: 28rpx;
  padding: 24rpx 16rpx;
  text-align: center;
  position: relative;
  overflow: hidden;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.01);
  border: 2rpx solid #f0f0f2;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 6rpx;
}

.stat-green::before { background: #34c759; }
.stat-orange::before { background: #ff9500; }
.stat-blue::before { background: #007aff; }

.stat-label {
  font-size: 22rpx;
  color: #86868b;
  margin-bottom: 12rpx;
}

.stat-value {
  font-size: 40rpx;
  font-weight: 700;
  color: #1d1d1f;
}

.stat-unit {
  font-size: 20rpx;
  color: #aeaeb2;
  margin-top: 4rpx;
}

.quick-action-grid {
  display: flex;
  gap: 16rpx;
  padding: 0 32rpx;
  margin-bottom: 24rpx;
}

.action-tile {
  flex: 1;
  background: #fff;
  border-radius: 28rpx;
  padding: 24rpx 8rpx;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 3rpx solid #f0f0f2;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.01);
}

.tile-icon {
  font-size: 44rpx;
  margin-bottom: 12rpx;
}

.tile-label {
  font-size: 22rpx;
  color: #1d1d1f;
  font-weight: 600;
}

.card {
  background: #fff;
  border-radius: 32rpx;
  padding: 32rpx;
  margin: 0 32rpx 24rpx;
  border: 3rpx solid #f0f0f2;
}

.card-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 28rpx;
}

.card-title {
  font-size: 30rpx;
  font-weight: 700;
  color: #1d1d1f;
}

.card-subtitle {
  font-size: 22rpx;
  color: #aeaeb2;
}

.nutrition-item {
  margin-bottom: 24rpx;
}

.nutrition-item:last-child {
  margin-bottom: 0;
}

.nutri-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12rpx;
}

.nutri-name {
  font-size: 26rpx;
  color: #1d1d1f;
  font-weight: 500;
}

.nutri-values {
  font-size: 22rpx;
  color: #86868b;
}

.progress-bar-bg {
  width: 100%;
  height: 16rpx;
  background: #f0f0f2;
  border-radius: 8rpx;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  border-radius: 8rpx;
  transition: width 0.6s ease;
}

.protein-bar { background: linear-gradient(90deg, #ff6b6b, #ff9500); }
.carbs-bar { background: linear-gradient(90deg, #ffcc00, #ffd60a); }
.fat-bar { background: linear-gradient(90deg, #5ac8fa, #007aff); }

.weight-card {
  position: relative;
  overflow: hidden;
  padding: 0;
}

.weight-card-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #007aff 0%, #5ac8fa 100%);
  border-radius: 32rpx;
}

.weight-card-content {
  position: relative;
  z-index: 1;
  padding: 32rpx;
}

.weight-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32rpx;
}

.weight-left {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.weight-label {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.85);
  margin-bottom: 8rpx;
}

.weight-value-row {
  display: flex;
  align-items: baseline;
}

.weight-value {
  font-size: 64rpx;
  font-weight: 700;
  color: #fff;
  line-height: 1;
}

.weight-unit {
  font-size: 30rpx;
  font-weight: 400;
  margin-left: 4rpx;
  color: #fff;
}

.weight-change {
  font-size: 24rpx;
  margin-top: 16rpx;
  color: rgba(255, 255, 255, 0.9);
}

.weight-right {
  display: flex;
  gap: 32rpx;
}

.weight-stat {
  text-align: right;
  display: flex;
  flex-direction: column;
}

.ws-label {
  font-size: 20rpx;
  color: rgba(255, 255, 255, 0.75);
  margin-bottom: 8rpx;
}

.ws-value {
  font-size: 32rpx;
  font-weight: 600;
  color: #fff;
}

.target-progress {
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.tp-label {
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.85);
  white-space: nowrap;
}

.tp-bar-bg {
  flex: 1;
  height: 12rpx;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 6rpx;
  overflow: hidden;
}

.tp-bar-fill {
  height: 100%;
  background: #fff;
  border-radius: 6rpx;
  transition: width 0.6s ease;
}

.tp-pct {
  font-size: 22rpx;
  color: #fff;
  font-weight: 600;
  min-width: 64rpx;
  text-align: right;
}

.section-title {
  font-size: 30rpx;
  font-weight: 700;
  color: #1d1d1f;
  padding: 0 32rpx;
  margin-bottom: 16rpx;
  margin-top: 8rpx;
  display: block;
}

.summary-report-card {
  display: flex;
  align-items: center;
  gap: 24rpx;
  padding: 28rpx 32rpx;
}

.src-icon {
  font-size: 52rpx;
  width: 72rpx;
  height: 72rpx;
  background: #f5f5f7;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.src-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.src-title {
  font-size: 28rpx;
  font-weight: 700;
  color: #1d1d1f;
}

.src-desc-row {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  margin-top: 4rpx;
}

.src-desc {
  font-size: 24rpx;
  color: #86868b;
}

.src-strong {
  font-size: 24rpx;
  color: #007aff;
  font-weight: 600;
}

.src-desc-alone {
  font-size: 24rpx;
  color: #86868b;
  margin-top: 4rpx;
}

.src-arrow {
  font-size: 36rpx;
  color: #aeaeb2;
  font-family: monospace;
}
</style>
