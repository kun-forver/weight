<template>
  <div class="page">
    <!-- Header -->
    <header class="dash-header">
      <div class="header-left">
        <div class="avatar">{{ userInitial }}</div>
        <div class="greeting">
          <div class="hello">{{ greeting }}，{{ userNickname }}</div>
          <div class="date-text">{{ formattedDate }}</div>
        </div>
      </div>
      <div class="header-right">
        <button class="icon-btn" @click="goToProfile">⚙️</button>
      </div>
    </header>

    <div v-if="loading" class="loading-overlay">
      <div class="spinner">⏳</div>
    </div>

    <div v-if="data" class="dash-content">
      <!-- Calorie Ring -->
      <div class="calorie-section">
        <CalorieRing
          :consumed="data.calorie_summary?.consumed || 0"
          :goal="data.calorie_summary?.goal || 2000"
        />
      </div>

      <!-- 3 Stat Cards -->
      <div class="stat-row">
        <div class="stat-card stat-green">
          <div class="stat-label">剩余可吃</div>
          <div class="stat-value">{{ data.calorie_summary?.remaining || 0 }}</div>
          <div class="stat-unit">kcal</div>
        </div>
        <div class="stat-card stat-orange">
          <div class="stat-label">已摄入</div>
          <div class="stat-value">{{ data.calorie_summary?.consumed || 0 }}</div>
          <div class="stat-unit">kcal</div>
        </div>
        <div class="stat-card stat-blue">
          <div class="stat-label">运动消耗</div>
          <div class="stat-value">{{ data.calorie_summary?.exercise || 0 }}</div>
          <div class="stat-unit">kcal</div>
        </div>
      </div>

      <!-- Quick Action Grid -->
      <div class="quick-action-grid">
        <router-link to="/weight" class="action-tile">
          <span class="tile-icon">⚖️</span>
          <span class="tile-label">记录体重</span>
        </router-link>
        <router-link to="/food" class="action-tile">
          <span class="tile-icon">🍎</span>
          <span class="tile-label">记录饮食</span>
        </router-link>
        <router-link to="/pk" class="action-tile">
          <span class="tile-icon">⚔️</span>
          <span class="tile-label">减脂对战</span>
        </router-link>
        <router-link to="/profile" class="action-tile">
          <span class="tile-icon">👤</span>
          <span class="tile-label">个人主页</span>
        </router-link>
      </div>

      <!-- Nutrition Progress -->
      <div class="card nutrition-card">
        <div class="card-title-row">
          <span class="card-title">营养分析</span>
          <span class="card-subtitle">今日摄入比例</span>
        </div>
        <div class="nutrition-item">
          <div class="nutri-header">
            <span class="nutri-name">🥩 蛋白质</span>
            <span class="nutri-values">{{ nutrition.protein.current }}g / {{ nutrition.protein.target }}g</span>
          </div>
          <div class="progress-bar-bg">
            <div class="progress-bar-fill protein-bar" :style="{ width: progressPct(nutrition.protein.current, nutrition.protein.target) }"></div>
          </div>
        </div>
        <div class="nutrition-item">
          <div class="nutri-header">
            <span class="nutri-name">🍞 碳水化合物</span>
            <span class="nutri-values">{{ nutrition.carbs.current }}g / {{ nutrition.carbs.target }}g</span>
          </div>
          <div class="progress-bar-bg">
            <div class="progress-bar-fill carbs-bar" :style="{ width: progressPct(nutrition.carbs.current, nutrition.carbs.target) }"></div>
          </div>
        </div>
        <div class="nutrition-item">
          <div class="nutri-header">
            <span class="nutri-name">🥑 脂肪</span>
            <span class="nutri-values">{{ nutrition.fat.current }}g / {{ nutrition.fat.target }}g</span>
          </div>
          <div class="progress-bar-bg">
            <div class="progress-bar-fill fat-bar" :style="{ width: progressPct(nutrition.fat.current, nutrition.fat.target) }"></div>
          </div>
        </div>
      </div>

      <!-- Weight Card -->
      <div class="card weight-card" v-if="weightData.current">
        <div class="weight-card-bg"></div>
        <div class="weight-card-content">
          <div class="weight-top">
            <div class="weight-left">
              <div class="weight-label">最新体重</div>
              <div class="weight-value">
                {{ weightData.current }}<span class="weight-unit">kg</span>
              </div>
              <div class="weight-change" :class="weightChangeClass" v-if="weightData.change !== null">
                {{ weightChangeIcon }} {{ Math.abs(weightData.change || 0).toFixed(1) }}kg vs 昨日
              </div>
            </div>
            <div class="weight-right">
              <div class="weight-stat">
                <div class="ws-label">本月减重</div>
                <div class="ws-value">{{ weightData.monthly_loss || 0 }}kg</div>
              </div>
              <div class="weight-stat">
                <div class="ws-label">目标体重</div>
                <div class="ws-value">{{ weightData.target || '-' }}kg</div>
              </div>
            </div>
          </div>
          <!-- Progress to target -->
          <div class="target-progress">
            <div class="tp-label">距目标进度</div>
            <div class="tp-bar-bg">
              <div class="tp-bar-fill" :style="{ width: (weightData.target_progress || 0) + '%' }"></div>
            </div>
            <div class="tp-pct">{{ Math.round(weightData.target_progress || 0) }}%</div>
          </div>
        </div>
      </div>

      <!-- Daily reports -->
      <div class="section-title">今日速报</div>

      <!-- Diet summary report -->
      <div class="card summary-report-card" @click="goToFood">
        <div class="src-icon">🍎</div>
        <div class="src-info">
          <div class="src-title">今日饮食概览</div>
          <div class="src-desc">
            已摄入 <strong>{{ data.calorie_summary?.consumed || 0 }}</strong> kcal，剩余可吃 <strong>{{ Math.max(0, data.calorie_summary?.remaining || 0) }}</strong> kcal
          </div>
        </div>
        <span class="src-arrow">›</span>
      </div>

      <!-- PK summary report -->
      <div v-if="data.pk" class="card summary-report-card" @click="goToPK">
        <div class="src-icon">⚔️</div>
        <div class="src-info">
          <div class="src-title">对战：{{ data.pk.name }}</div>
          <div class="src-desc">
            对战进行中 · 剩余 <strong>{{ Math.max((data.pk.days_total || 0) - (data.pk.days_elapsed || 0), 0) }}</strong> 天
          </div>
        </div>
        <span class="src-arrow">›</span>
      </div>
      <div v-else class="card summary-report-card" @click="goToPK">
        <div class="src-icon">🎯</div>
        <div class="src-info">
          <div class="src-title">暂无进行中的对战</div>
          <div class="src-desc">点击这里，去找好友发起减脂PK挑战吧！</div>
        </div>
        <span class="src-arrow">›</span>
      </div>
    </div>

    <BottomNav @add="goToFood" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'
import { useAuthStore } from '../stores/auth'
import CalorieRing from '../components/CalorieRing.vue'
import BottomNav from '../components/BottomNav.vue'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const data = ref(null)
const error = ref(null)

const user = computed(() => authStore.user || JSON.parse(localStorage.getItem('user') || '{}'))
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
  router.push('/food')
}

function goToPK() {
  router.push('/pk')
}

function goToProfile() {
  router.push('/profile')
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

onMounted(async () => {
  if (!authStore.user) {
    try {
      await authStore.fetchUser()
    } catch {
      // will redirect via interceptor
    }
  }
  await fetchDashboard()
})
</script>

<style scoped>
.dash-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: #fff;
  position: sticky;
  top: 0;
  z-index: 50;
  border-bottom: 1px solid var(--border-color);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #007aff, #5ac8fa);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 600;
}

.greeting .hello {
  font-size: 16px;
  font-weight: 600;
  color: #1d1d1f;
}

.greeting .date-text {
  font-size: 12px;
  color: #86868b;
  margin-top: 2px;
}

.header-right {
  display: flex;
}

.icon-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  border-radius: 50%;
  background: #f5f5f7;
  transition: background 0.2s;
}

.icon-btn:active {
  background: #e5e5ea;
}

.calorie-section {
  display: flex;
  justify-content: center;
  padding: 24px 0 16px;
  background: #fff;
}

.stat-row {
  display: flex;
  gap: 10px;
  padding: 0 16px;
  margin-bottom: 14px;
}

.stat-card {
  flex: 1;
  background: #fff;
  border-radius: 14px;
  padding: 14px 10px;
  text-align: center;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.01);
  border: 1px solid #f0f0f2;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
}

.stat-green::before { background: #34c759; }
.stat-orange::before { background: #ff9500; }
.stat-blue::before { background: #007aff; }

.stat-label {
  font-size: 11px;
  color: #86868b;
  margin-bottom: 6px;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: #1d1d1f;
}

.stat-unit {
  font-size: 10px;
  color: #aeaeb2;
  margin-top: 2px;
}

/* Quick action grid */
.quick-action-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  padding: 0 16px;
  margin-bottom: 14px;
}

.action-tile {
  background: #fff;
  border-radius: 14px;
  padding: 12px 6px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 1.5px solid #f0f0f2;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.01);
  text-decoration: none;
  transition: transform 0.2s, box-shadow 0.2s;
}

.action-tile:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.03);
}

.action-tile:active {
  transform: scale(0.95);
}

.tile-icon {
  font-size: 22px;
  margin-bottom: 6px;
}

.tile-label {
  font-size: 11px;
  color: #1d1d1f;
  font-weight: 600;
}

.card {
  background: #fff;
  border-radius: 16px;
  padding: 16px;
  margin: 0 16px 14px;
  border: 1.5px solid #f0f0f2;
}

.card-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.card-title {
  font-size: 15px;
  font-weight: 700;
  color: #1d1d1f;
}

.card-subtitle {
  font-size: 11px;
  color: #aeaeb2;
}

.nutrition-item {
  margin-bottom: 12px;
}

.nutrition-item:last-child {
  margin-bottom: 0;
}

.nutri-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.nutri-name {
  font-size: 13px;
  color: #1d1d1f;
  font-weight: 500;
}

.nutri-values {
  font-size: 11px;
  color: #86868b;
}

.progress-bar-bg {
  width: 100%;
  height: 8px;
  background: #f0f0f2;
  border-radius: 4px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  border-radius: 4px;
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
  border-radius: 16px;
}

.weight-card-content {
  position: relative;
  z-index: 1;
  padding: 16px;
  color: #fff;
}

.weight-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.weight-left {
  flex: 1;
}

.weight-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.85);
  margin-bottom: 4px;
}

.weight-value {
  font-size: 32px;
  font-weight: 700;
  color: #fff;
  line-height: 1;
}

.weight-unit {
  font-size: 15px;
  font-weight: 400;
  margin-left: 2px;
}

.weight-change {
  font-size: 12px;
  margin-top: 8px;
  color: rgba(255, 255, 255, 0.9);
}

.weight-right {
  display: flex;
  gap: 16px;
}

.weight-stat {
  text-align: right;
}

.ws-label {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.75);
  margin-bottom: 4px;
}

.ws-value {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
}

.target-progress {
  display: flex;
  align-items: center;
  gap: 10px;
}

.tp-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.85);
  white-space: nowrap;
}

.tp-bar-bg {
  flex: 1;
  height: 6px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 3px;
  overflow: hidden;
}

.tp-bar-fill {
  height: 100%;
  background: #fff;
  border-radius: 3px;
  transition: width 0.6s ease;
}

.tp-pct {
  font-size: 11px;
  color: #fff;
  font-weight: 600;
  min-width: 32px;
  text-align: right;
}

/* Redesigned Summary report card */
.summary-report-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.summary-report-card:active {
  background-color: #f5f5f7;
}

.src-icon {
  font-size: 26px;
  width: 36px;
  height: 36px;
  background: #f5f5f7;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.src-info {
  flex: 1;
}

.src-title {
  font-size: 14px;
  font-weight: 700;
  color: #1d1d1f;
}

.src-desc {
  font-size: 12px;
  color: #86868b;
  margin-top: 2px;
}

.src-desc strong {
  color: #007aff;
  font-weight: 600;
}

.src-arrow {
  font-size: 18px;
  color: #aeaeb2;
  font-family: monospace;
}
</style>
