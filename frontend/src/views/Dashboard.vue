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
        <button class="icon-btn">🔔</button>
        <button class="icon-btn">⚙️</button>
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

      <!-- Nutrition Progress -->
      <div class="card nutrition-card">
        <div class="card-title-row">
          <span class="card-title">营养素</span>
          <span class="card-subtitle">今日摄入</span>
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
              <div class="weight-label">当前体重</div>
              <div class="weight-value">
                {{ weightData.current }}<span class="weight-unit">kg</span>
              </div>
              <div class="weight-change" :class="weightChangeClass">
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
          <!-- Mini bar chart -->
          <div class="mini-chart">
            <div
              v-for="(val, i) in weightTrend"
              :key="i"
              class="mini-bar"
              :style="{ height: barHeight(val) }"
            ></div>
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

      <!-- Today's Food Logs -->
      <div class="section-title">今日饮食</div>
      <div v-for="meal in meals" :key="meal.type" class="meal-group">
        <div class="meal-header">
          <span class="meal-name">{{ meal.label }}</span>
          <span class="meal-cal">{{ mealTotalCalories(meal.type) }} kcal</span>
        </div>
        <div v-if="getMealFoods(meal.type).length === 0" class="empty-meal">
          暂无记录
        </div>
        <div
          v-for="item in getMealFoods(meal.type)"
          :key="item.id"
          class="food-item"
        >
          <div class="food-emoji">{{ item.emoji || '🍽️' }}</div>
          <div class="food-info">
            <div class="food-name">{{ item.food_name }}</div>
            <div class="food-meta">{{ item.protein || 0 }}g蛋白质 · {{ formatTime(item.logged_at) }}</div>
          </div>
          <div class="food-calories">
            <div class="fc-value">{{ item.calories }}</div>
            <div class="fc-unit">kcal</div>
          </div>
        </div>
      </div>

      <!-- PK Battle Card -->
      <div v-if="data.pk" class="card pk-card">
        <div class="pk-header">
          <span class="pk-title">⚔️ {{ data.pk.name }}</span>
          <span class="pk-status-badge" :class="pkStatusClass(data.pk.status)">{{ pkStatusText(data.pk.status) }}</span>
        </div>
        <div class="pk-battle">
          <div class="pk-side pk-left">
            <div class="pk-avatar">{{ getInitial(data.pk.user_a?.name) }}</div>
            <div class="pk-name">{{ data.pk.user_a?.name || '我' }}</div>
            <div class="pk-score">{{ data.pk.user_a?.score || 0 }}</div>
            <div class="pk-pct">{{ data.pk.user_a?.pct || 0 }}%</div>
          </div>
          <div class="pk-center">
            <div class="pk-vs">VS</div>
            <div class="pk-lead" v-if="data.pk.leader">
              {{ data.pk.leader === data.pk.user_a?.id ? '← 领先' : '领先 →' }}
            </div>
          </div>
          <div class="pk-side pk-right">
            <div class="pk-avatar">{{ getInitial(data.pk.user_b?.name) }}</div>
            <div class="pk-name">{{ data.pk.user_b?.name || '对手' }}</div>
            <div class="pk-score">{{ data.pk.user_b?.score || 0 }}</div>
            <div class="pk-pct">{{ data.pk.user_b?.pct || 0 }}%</div>
          </div>
        </div>
        <!-- Progress bar -->
        <div class="pk-progress-section">
          <div class="pk-progress-bar">
            <div class="pk-progress-left" :style="{ width: (data.pk.user_a?.pct || 0) + '%' }"></div>
            <div class="pk-progress-right" :style="{ width: (data.pk.user_b?.pct || 0) + '%' }"></div>
          </div>
        </div>
        <!-- Info row -->
        <div class="pk-info-row">
          <div class="pk-info-item">
            <span class="pi-icon">📅</span>
            <span>剩余 {{ Math.max((data.pk.days_total || 0) - (data.pk.days_elapsed || 0), 0) }} 天</span>
          </div>
          <div class="pk-info-item">
            <span class="pi-icon">🏆</span>
            <span>{{ data.pk.reward || '加油挑战' }}</span>
          </div>
        </div>
      </div>

      <div v-else class="card pk-empty-card">
        <div class="pk-empty-content">
          <div class="pk-empty-emoji">🎯</div>
          <div class="pk-empty-text">还没有进行中的对战</div>
          <router-link to="/pk" class="pk-empty-btn">发起对战</router-link>
        </div>
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
const userNickname = computed(() => user.value?.nickname || '小伙伴')
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
  const n = data.value?.nutrition || {}
  return {
    protein: { current: n.protein?.current || 0, target: n.protein?.target || 60 },
    carbs: { current: n.carbs?.current || 0, target: n.carbs?.target || 250 },
    fat: { current: n.fat?.current || 0, target: n.fat?.target || 65 },
  }
})

const weightData = computed(() => data.value?.weight || {})
const weightTrend = computed(() => {
  const trend = weightData.value.trend || []
  if (trend.length === 0) return []
  return trend.slice(-7)
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

const meals = [
  { type: 0, label: '🍳 早餐' },
  { type: 1, label: '🥗 午餐' },
  { type: 2, label: '🍲 晚餐' },
  { type: 3, label: '🍪 加餐' },
]

function getMealFoods(mealType) {
  const logs = data.value?.food_logs || []
  return logs.filter(f => f.meal_type === mealType)
}

function mealTotalCalories(mealType) {
  return getMealFoods(mealType).reduce((sum, f) => sum + (f.calories || 0), 0)
}

function progressPct(current, target) {
  if (!target || target <= 0) return '0%'
  return Math.min((current / target) * 100, 100) + '%'
}

function barHeight(val) {
  const trend = weightTrend.value
  const max = Math.max(...trend, 1)
  const min = Math.min(...trend, 0)
  const range = max - min || 1
  const h = ((val - min) / range) * 100
  return Math.max(h, 15) + 'px'
}

function getInitial(name) {
  if (!name) return '?'
  return name.charAt(0).toUpperCase()
}

function formatTime(timeStr) {
  if (!timeStr) return ''
  const d = new Date(timeStr)
  return `${d.getHours()}:${String(d.getMinutes()).padStart(2, '0')}`
}

function pkStatusClass(status) {
  const map = { active: 'status-active', pending: 'status-pending', completed: 'status-done' }
  return map[status] || 'status-active'
}

function pkStatusText(status) {
  const map = { active: '进行中', pending: '待开始', completed: '已结束' }
  return map[status] || '进行中'
}

function goToFood() {
  router.push('/food')
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
      nutrition: {
        protein: { current: 0, target: 60 },
        carbs: { current: 0, target: 250 },
        fat: { current: 0, target: 65 },
      },
      weight: { current: 0, change: 0, trend: [], monthly_loss: 0, target: 0, target_progress: 0 },
      food_logs: [],
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
  gap: 8px;
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
  margin-bottom: 8px;
}

.stat-card {
  flex: 1;
  background: #fff;
  border-radius: 14px;
  padding: 14px 10px;
  text-align: center;
  position: relative;
  overflow: hidden;
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
  font-size: 12px;
  color: #86868b;
  margin-bottom: 6px;
}

.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: #1d1d1f;
}

.stat-unit {
  font-size: 11px;
  color: #aeaeb2;
  margin-top: 2px;
}

.card {
  background: #fff;
  border-radius: 16px;
  padding: 16px;
  margin: 8px 16px;
}

.card-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #1d1d1f;
}

.card-subtitle {
  font-size: 12px;
  color: #aeaeb2;
}

.nutrition-item {
  margin-bottom: 14px;
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
  font-size: 14px;
  color: #1d1d1f;
  font-weight: 500;
}

.nutri-values {
  font-size: 12px;
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
  padding: 20px;
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
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 4px;
}

.weight-value {
  font-size: 36px;
  font-weight: 700;
  color: #fff;
  line-height: 1;
}

.weight-unit {
  font-size: 16px;
  font-weight: 400;
  margin-left: 4px;
}

.weight-change {
  font-size: 13px;
  margin-top: 8px;
  color: rgba(255, 255, 255, 0.9);
}

.weight-right {
  display: flex;
  gap: 20px;
}

.weight-stat {
  text-align: right;
}

.ws-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 4px;
}

.ws-value {
  font-size: 18px;
  font-weight: 600;
  color: #fff;
}

.mini-chart {
  display: flex;
  align-items: flex-end;
  gap: 6px;
  height: 60px;
  margin-bottom: 14px;
  padding: 0 4px;
}

.mini-bar {
  flex: 1;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 4px 4px 0 0;
  min-height: 15px;
  transition: height 0.4s ease;
}

.mini-bar:last-child {
  background: rgba(255, 255, 255, 0.9);
}

.target-progress {
  display: flex;
  align-items: center;
  gap: 10px;
}

.tp-label {
  font-size: 12px;
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
  font-size: 12px;
  color: #fff;
  font-weight: 600;
  min-width: 36px;
  text-align: right;
}

.meal-group {
  margin: 0 16px 12px;
  background: #fff;
  border-radius: 16px;
  padding: 14px 16px;
}

.meal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f0f2;
}

.meal-name {
  font-size: 15px;
  font-weight: 600;
  color: #1d1d1f;
}

.meal-cal {
  font-size: 13px;
  color: #007aff;
  font-weight: 600;
}

.empty-meal {
  font-size: 13px;
  color: #aeaeb2;
  padding: 8px 0;
  text-align: center;
}

.food-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
}

.food-emoji {
  font-size: 26px;
  width: 40px;
  text-align: center;
}

.food-info {
  flex: 1;
}

.food-name {
  font-size: 14px;
  font-weight: 500;
  color: #1d1d1f;
}

.food-meta {
  font-size: 12px;
  color: #86868b;
  margin-top: 2px;
}

.food-calories {
  text-align: right;
}

.fc-value {
  font-size: 16px;
  font-weight: 600;
  color: #ff9500;
}

.fc-unit {
  font-size: 11px;
  color: #aeaeb2;
}

.pk-card {
  margin-top: 8px;
}

.pk-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.pk-title {
  font-size: 16px;
  font-weight: 600;
  color: #1d1d1f;
}

.pk-status-badge {
  font-size: 11px;
  padding: 3px 10px;
  border-radius: 10px;
  font-weight: 500;
}

.status-active {
  background: #e8f5e9;
  color: #34c759;
}

.status-pending {
  background: #fff3cd;
  color: #ff9500;
}

.status-done {
  background: #f0f0f2;
  color: #86868b;
}

.pk-battle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 0;
}

.pk-side {
  text-align: center;
  flex: 1;
}

.pk-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #007aff, #5ac8fa);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 600;
  margin: 0 auto 6px;
}

.pk-right .pk-avatar {
  background: linear-gradient(135deg, #ff9500, #ff6b6b);
}

.pk-name {
  font-size: 12px;
  color: #86868b;
}

.pk-score {
  font-size: 22px;
  font-weight: 700;
  color: #1d1d1f;
  margin-top: 2px;
}

.pk-pct {
  font-size: 12px;
  color: #007aff;
  font-weight: 600;
}

.pk-right .pk-pct {
  color: #ff9500;
}

.pk-center {
  flex: 0 0 60px;
  text-align: center;
}

.pk-vs {
  font-size: 18px;
  font-weight: 800;
  color: #aeaeb2;
}

.pk-lead {
  font-size: 10px;
  color: #86868b;
  margin-top: 4px;
}

.pk-progress-section {
  margin: 12px 0;
}

.pk-progress-bar {
  display: flex;
  height: 8px;
  border-radius: 4px;
  overflow: hidden;
  background: #f0f0f2;
}

.pk-progress-left {
  background: linear-gradient(90deg, #007aff, #5ac8fa);
  transition: width 0.6s ease;
}

.pk-progress-right {
  background: linear-gradient(90deg, #ff6b6b, #ff9500);
  transition: width 0.6s ease;
  margin-left: auto;
}

.pk-info-row {
  display: flex;
  justify-content: space-around;
  padding-top: 8px;
}

.pk-info-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 13px;
  color: #86868b;
}

.pi-icon {
  font-size: 14px;
}

.pk-empty-card {
  text-align: center;
}

.pk-empty-content {
  padding: 10px 0;
}

.pk-empty-emoji {
  font-size: 36px;
  margin-bottom: 8px;
}

.pk-empty-text {
  font-size: 14px;
  color: #86868b;
  margin-bottom: 12px;
}

.pk-empty-btn {
  display: inline-block;
  padding: 8px 24px;
  background: #007aff;
  color: #fff;
  border-radius: 14px;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
}

.spinner {
  font-size: 32px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.change-down { color: #e8f5e9; }
.change-up { color: #ffeaea; }
</style>
