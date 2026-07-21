<template>
  <view class="page" :class="{ 'dark-mode': isDark }">
    <!-- Header -->
    <view class="page-header">
      <text class="page-title">体重记录</text>
      <view class="icon-btn">📊</view>
    </view>

    <view v-if="loading" class="loading-text"><text>加载中...</text></view>

    <!-- Big Weight Card -->
    <view class="card weight-main-card" v-if="latestWeight">
      <view class="weight-card-bg"></view>
      <view class="weight-card-content">
        <view class="wmc-top">
          <view class="wmc-left">
            <text class="wmc-label">当前体重</text>
            <view class="wmc-value-row">
              <text class="wmc-value">{{ latestWeight.weight || 0 }}</text>
              <text class="wmc-unit">kg</text>
            </view>
            <view class="wmc-change" :class="{ 'down': weightChange < 0, 'up': weightChange > 0 }">
              <text class="change-arrow">{{ weightChange < 0 ? '↓' : weightChange > 0 ? '↑' : '→' }}</text>
              <text> {{ Math.abs(weightChange).toFixed(1) }}kg vs 昨日</text>
            </view>
          </view>
          <view class="wmc-right">
            <view class="wmc-stat">
              <text class="wmc-stat-label">目标</text>
              <text class="wmc-stat-value" v-if="targetWeight">{{ targetWeight }}kg</text>
              <text class="wmc-stat-value" v-else>未设置</text>
            </view>
            <view class="wmc-progress-circle">
              <view class="progress-ring-bg">
                <text class="progress-pct">{{ Math.round(goalProgress) }}%</text>
              </view>
            </view>
          </view>
        </view>
        <button class="record-btn" @tap="openRecordSheet">+ 记录体重</button>
      </view>
    </view>

    <!-- Range Tabs -->
    <view class="range-tabs">
      <view
        v-for="r in ranges"
        :key="r.key"
        class="range-tab"
        :class="{ active: activeRange === r.key }"
        @tap="changeRange(r.key)"
      >{{ r.label }}</view>
    </view>

    <!-- Bar Chart -->
    <view class="card chart-card">
      <view class="chart-header">
        <text class="chart-title">体重趋势</text>
        <text class="chart-subtitle">{{ rangeLabel }}</text>
      </view>
      <view class="bar-chart">
        <view class="chart-y-labels">
          <text class="y-label">{{ maxWeight.toFixed(1) }}</text>
          <text class="y-label">{{ ((maxWeight + minWeight) / 2).toFixed(1) }}</text>
          <text class="y-label">{{ minWeight.toFixed(1) }}</text>
        </view>
        <scroll-view scroll-x class="chart-bars-scroll">
          <view class="chart-bars">
            <view
              v-for="(item, i) in chartData"
              :key="i"
              class="chart-bar-wrapper"
            >
              <view class="chart-bar" :style="{ height: barHeightValue(item.weight) + 'rpx' }"></view>
              <text class="chart-bar-label">{{ item.label }}</text>
            </view>
          </view>
        </scroll-view>
      </view>
    </view>

    <!-- 4 Stat Cards -->
    <view class="stat-grid">
      <view class="stat-card">
        <text class="stat-icon">📉</text>
        <view class="stat-value-row">
          <text class="stat-value">{{ monthlyLoss }}</text>
          <text class="stat-unit">kg</text>
        </view>
        <text class="stat-label">本月减重</text>
      </view>
      <view class="stat-card">
        <text class="stat-icon">⚖️</text>
        <view class="stat-value-row">
          <text class="stat-value">{{ latestWeight?.weight || 0 }}</text>
          <text class="stat-unit">kg</text>
        </view>
        <text class="stat-label">当前体重</text>
      </view>
      <view class="stat-card">
        <text class="stat-icon">📅</text>
        <view class="stat-value-row">
          <text class="stat-value">{{ monthStartWeight }}</text>
          <text class="stat-unit">kg</text>
        </view>
        <text class="stat-label">月初体重</text>
      </view>
      <view class="stat-card">
        <text class="stat-icon">📏</text>
        <view class="stat-value-row">
          <text class="stat-value">{{ bmi }}</text>
        </view>
        <text class="stat-label">BMI</text>
      </view>
    </view>

    <!-- Calendar Grid -->
    <view class="card calendar-card">
      <view class="calendar-header">
        <text class="cal-title">打卡日历</text>
        <text class="cal-count">本月已记录 {{ recordedDays }} 天</text>
      </view>
      <view class="calendar-grid">
        <view class="cal-weekdays">
          <text v-for="w in weekdays" :key="w" class="cal-weekday">{{ w }}</text>
        </view>
        <view class="cal-days">
          <view
            v-for="(day, i) in calendarDays"
            :key="i"
            class="cal-day"
            :class="{ recorded: day.recorded, other: !day.currentMonth }"
          >
            <text class="day-num">{{ day.day || '' }}</text>
            <view v-if="day.recorded" class="day-dot"></view>
          </view>
        </view>
      </view>
    </view>

    <!-- Body Journal List -->
    <text class="section-title">体重日志</text>
    <view class="journal-grid">
      <view
        v-for="item in weightRecords"
        :key="item.id"
        class="journal-card"
      >
        <view class="jc-top">
          <view class="jc-date">
            <text class="jd-day">{{ formatDay(item.logged_at) }}</text>
            <text class="jd-month">{{ formatMonth(item.logged_at) }}</text>
          </view>
          <view class="jc-trend" v-if="item.trend">
            <text :class="item.trend < 0 ? 'trend-down' : 'trend-up'">
              {{ item.trend < 0 ? '↓' : '↑' }} {{ Math.abs(item.trend).toFixed(1) }}
            </text>
          </view>
        </view>
        <text class="jc-weight">{{ item.weight }}<text class="jc-unit">kg</text></text>
        <view class="jc-tags">
          <text v-if="item.body_fat" class="journal-tag">体脂 {{ item.body_fat }}%</text>
          <text v-if="item.muscle" class="journal-tag">肌肉 {{ item.muscle }}kg</text>
        </view>
        <text class="jc-note" v-if="item.note">{{ item.note }}</text>
      </view>
      <view v-if="weightRecords.length === 0" class="empty-state full-width">
        <text>暂无体重记录</text>
      </view>
    </view>

    <!-- Bottom Sheet: Record Weight -->
    <view v-if="showRecordSheet" class="bottom-sheet-backdrop" @tap="closeRecordSheet"></view>
    <view v-if="showRecordSheet" class="bottom-sheet">
      <view class="sheet-header">
        <text class="sheet-title">记录体重</text>
        <view class="sheet-close" @tap="closeRecordSheet">✕</view>
      </view>
      <view class="record-form">
        <view class="form-group">
          <text class="form-label">体重 (kg) *</text>
          <input
            v-model="recordForm.weight"
            type="digit"
            placeholder="如 65.5"
            class="form-input"
            placeholder-class="ph-class"
          />
        </view>
        <view class="form-row">
          <view class="form-group">
            <text class="form-label">体脂率 (%)</text>
            <input
              v-model="recordForm.body_fat"
              type="digit"
              placeholder="如 22.5"
              class="form-input"
              placeholder-class="ph-class"
            />
          </view>
          <view class="form-group">
            <text class="form-label">肌肉量 (kg)</text>
            <input
              v-model="recordForm.muscle"
              type="digit"
              placeholder="如 28.0"
              class="form-input"
              placeholder-class="ph-class"
            />
          </view>
        </view>
        <view class="form-group">
          <text class="form-label">备注</text>
          <textarea
            v-model="recordForm.note"
            placeholder="如 今天跑步了5公里"
            class="form-textarea"
            placeholder-class="ph-class"
            :maxlength="200"
          ></textarea>
        </view>
        <button class="btn-primary" @tap="saveWeight" :disabled="saving">
          {{ saving ? '保存中...' : '保存记录' }}
        </button>
      </view>
    </view>
    <custom-tabbar :current="2" />
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onLoad, onShow } from '@dcloudio/uni-app'
import api from '../../api'
import { useAuthStore } from '../../stores/auth'
import { useDarkMode } from '../../utils/theme'
import CustomTabbar from '../../components/custom-tabbar/index.vue'

const authStore = useAuthStore()
const { isDark, initDark } = useDarkMode()

const loading = ref(true)
const weightRecords = ref([])
const latestWeight = ref(null)
const todayWeight = ref(null)
const activeRange = ref('30d')
const saving = ref(false)
const showRecordSheet = ref(false)

const recordForm = ref({
  weight: '',
  body_fat: '',
  muscle: '',
  note: '',
})

const ranges = [
  { key: '7d', label: '7天' },
  { key: '30d', label: '30天' },
  { key: 'all', label: '全部' },
]

const weekdays = ['日', '一', '二', '三', '四', '五', '六']

const targetWeight = computed(() => authStore.user?.target_weight || null)
const userHeight = computed(() => authStore.user?.height || 0)

const weightChange = computed(() => {
  if (weightRecords.value.length >= 2) {
    const latest = weightRecords.value[0].weight
    const prev = weightRecords.value[1].weight
    return latest - prev
  }
  return 0
})

const chartData = computed(() => {
  const data = weightRecords.value.slice(0, 30).reverse()
  return data.map(item => ({
    weight: item.weight,
    label: formatChartLabel(item.logged_at),
  }))
})

const maxWeight = computed(() => {
  const weights = chartData.value.map(d => d.weight).filter(Boolean)
  return weights.length ? Math.max(...weights) + 1 : 1
})

const minWeight = computed(() => {
  const weights = chartData.value.map(d => d.weight).filter(Boolean)
  return weights.length ? Math.min(...weights) - 1 : 0
})

const rangeLabel = computed(() => {
  const r = ranges.find(r => r.key === activeRange.value)
  return r ? r.label : ''
})

const monthlyLoss = computed(() => {
  if (!weightRecords.value.length) return 0
  const now = new Date()
  const monthStart = weightRecords.value.find(r => {
    const d = new Date(r.logged_at)
    return d.getMonth() === now.getMonth() && d.getDate() <= 5
  })
  if (monthStart && latestWeight.value) {
    return Math.max(0, (monthStart.weight - latestWeight.value.weight)).toFixed(1)
  }
  return '0.0'
})

const monthStartWeight = computed(() => {
  if (!weightRecords.value.length) return '0.0'
  const now = new Date()
  const monthStart = weightRecords.value.find(r => {
    const d = new Date(r.logged_at)
    return d.getMonth() === now.getMonth() && d.getDate() <= 5
  })
  return monthStart ? monthStart.weight.toFixed(1) : weightRecords.value[weightRecords.value.length - 1].weight.toFixed(1)
})

const bmi = computed(() => {
  const weight = latestWeight.value?.weight
  const height = userHeight.value
  if (weight && height) {
    return (weight / Math.pow(height / 100, 2)).toFixed(1)
  }
  return '-'
})

const goalProgress = computed(() => {
  if (!targetWeight.value || !latestWeight.value) return 0
  const startWeight = parseFloat(monthStartWeight.value) || latestWeight.value.weight
  const total = startWeight - targetWeight.value
  if (total <= 0) return 100
  const done = startWeight - latestWeight.value.weight
  return Math.max(0, Math.min(100, (done / total) * 100))
})

const recordedDays = computed(() => {
  const now = new Date()
  return weightRecords.value.filter(r => {
    const d = new Date(r.logged_at)
    return d.getMonth() === now.getMonth()
  }).length
})

const calendarDays = computed(() => {
  const now = new Date()
  const year = now.getFullYear()
  const month = now.getMonth()
  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)
  const startWeekday = firstDay.getDay()
  const daysInMonth = lastDay.getDate()

  const prevLastDay = new Date(year, month, 0).getDate()
  const days = []
  for (let i = startWeekday - 1; i >= 0; i--) {
    days.push({ day: prevLastDay - i, currentMonth: false, recorded: false })
  }
  const recordedDates = new Set(
    weightRecords.value
      .filter(r => {
        const d = new Date(r.logged_at)
        return d.getMonth() === month && d.getFullYear() === year
      })
      .map(r => new Date(r.logged_at).getDate())
  )
  for (let d = 1; d <= daysInMonth; d++) {
    days.push({ day: d, currentMonth: true, recorded: recordedDates.has(d) })
  }
  while (days.length % 7 !== 0) {
    days.push({ day: days.length - daysInMonth - startWeekday + 1, currentMonth: false, recorded: false })
  }
  return days
})

function barHeightValue(weight) {
  if (!weight) return 0
  const range = maxWeight.value - minWeight.value
  if (range <= 0) return 80
  const h = ((weight - minWeight.value) / range) * 240
  return Math.max(40, h)
}

function formatChartLabel(dateStr) {
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}/${d.getDate()}`
}

function formatDay(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.getDate()
}

function formatMonth(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}月`
}

function changeRange(range) {
  activeRange.value = range
  fetchWeights()
}

function openRecordSheet() {
  recordForm.value = { weight: '', body_fat: '', muscle: '', note: '' }
  showRecordSheet.value = true
}

function closeRecordSheet() {
  showRecordSheet.value = false
}

async function fetchWeights() {
  loading.value = true
  try {
    const res = await api.get(`/weights?range=${activeRange.value}`)
    weightRecords.value = res.data || []
    weightRecords.value.forEach((item, i, arr) => {
      if (i < arr.length - 1) {
        item.trend = item.weight - arr[i + 1].weight
      }
    })
  } catch (e) {
    weightRecords.value = []
  } finally {
    loading.value = false
  }
}

async function fetchLatestWeight() {
  try {
    const res = await api.get('/weights/latest')
    latestWeight.value = res.data
  } catch (e) {
    latestWeight.value = { weight: 0 }
  }
}

async function fetchTodayWeight() {
  try {
    const res = await api.get('/weights/today')
    todayWeight.value = res.data
    if (res.data?.weight) {
      recordForm.value.weight = res.data.weight
      recordForm.value.body_fat = res.data.body_fat || ''
      recordForm.value.muscle = res.data.muscle || ''
    }
  } catch (e) {
    todayWeight.value = null
  }
}

async function saveWeight() {
  if (!recordForm.value.weight) {
    uni.showToast({ title: '请输入体重', icon: 'none' })
    return
  }
  saving.value = true
  try {
    await api.post('/weights', {
      weight: Number(recordForm.value.weight),
      body_fat: recordForm.value.body_fat ? Number(recordForm.value.body_fat) : undefined,
      muscle: recordForm.value.muscle ? Number(recordForm.value.muscle) : undefined,
      note: recordForm.value.note || undefined,
    })
    closeRecordSheet()
    await Promise.all([fetchWeights(), fetchLatestWeight(), fetchTodayWeight()])
  } catch (e) {
    uni.showToast({ title: '保存失败，请重试', icon: 'none' })
  } finally {
    saving.value = false
  }
}

onLoad(async () => {
  if (!authStore.user) {
    try { await authStore.fetchUser() } catch {}
  }
  await Promise.all([fetchWeights(), fetchLatestWeight(), fetchTodayWeight()])
})

onShow(async () => {
  try { uni.hideTabBar({ animation: false }) } catch (e) {}
  initDark()
  if (!loading.value && weightRecords.value.length > 0) {
    await Promise.all([fetchWeights(), fetchLatestWeight(), fetchTodayWeight()])
  }
})
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #f5f5f7;
  padding-bottom: calc(150rpx + env(safe-area-inset-bottom));
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24rpx 32rpx;
  background: #fff;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 50;
}

.page-title {
  font-size: 40rpx;
  font-weight: 700;
  color: #1d1d1f;
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

.loading-text {
  text-align: center;
  padding: 40rpx;
  color: #86868b;
  margin-top: 120rpx;
  font-size: 28rpx;
}

.card {
  background: #fff;
  border-radius: 32rpx;
  padding: 32rpx;
  margin: 16rpx 32rpx;
}

.weight-main-card {
  position: relative;
  overflow: hidden;
  padding: 0;
  margin-top: 136rpx;
}

.weight-card-bg {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: linear-gradient(135deg, #007aff 0%, #5ac8fa 100%);
  border-radius: 32rpx;
}

.weight-card-content {
  position: relative;
  z-index: 1;
  padding: 40rpx;
  color: #fff;
}

.wmc-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 40rpx;
}

.wmc-left {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.wmc-label {
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 12rpx;
}

.wmc-value-row {
  display: flex;
  align-items: baseline;
}

.wmc-value {
  font-size: 80rpx;
  font-weight: 700;
  color: #fff;
  line-height: 1;
}

.wmc-unit {
  font-size: 32rpx;
  font-weight: 400;
  margin-left: 8rpx;
  color: #fff;
}

.wmc-change {
  font-size: 26rpx;
  margin-top: 16rpx;
  color: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
}

.change-arrow {
  font-weight: 600;
}

.wmc-change.down { color: #d4f5d4; }
.wmc-change.up { color: #ffd4d4; }

.wmc-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 20rpx;
}

.wmc-stat {
  text-align: right;
  display: flex;
  flex-direction: column;
}

.wmc-stat-label {
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.7);
}

.wmc-stat-value {
  font-size: 36rpx;
  font-weight: 600;
  color: #fff;
  margin-top: 4rpx;
}

.wmc-progress-circle {
  position: relative;
  width: 112rpx;
  height: 112rpx;
}

.progress-ring-bg {
  width: 112rpx;
  height: 112rpx;
  border-radius: 50%;
  border: 6rpx solid rgba(255, 255, 255, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
}

.progress-pct {
  font-size: 24rpx;
  font-weight: 700;
  color: #fff;
}

.record-btn {
  width: 100%;
  height: 88rpx;
  background: rgba(255, 255, 255, 0.2);
  border: 3rpx solid rgba(255, 255, 255, 0.5);
  border-radius: 28rpx;
  color: #fff;
  font-size: 30rpx;
  font-weight: 600;
  line-height: 88rpx;
}

.range-tabs {
  display: flex;
  gap: 16rpx;
  padding: 0 32rpx;
  margin: 24rpx 0 16rpx;
}

.range-tab {
  flex: 1;
  height: 72rpx;
  border-radius: 24rpx;
  background: #fff;
  font-size: 28rpx;
  color: #86868b;
  text-align: center;
  line-height: 72rpx;
}

.range-tab.active {
  background: #007aff;
  color: #fff;
  font-weight: 600;
}

.chart-card {
  padding: 32rpx 40rpx;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28rpx;
}

.chart-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #1d1d1f;
}

.chart-subtitle {
  font-size: 24rpx;
  color: #86868b;
}

.bar-chart {
  display: flex;
  gap: 20rpx;
  height: 340rpx;
}

.chart-y-labels {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  font-size: 20rpx;
  color: #aeaeb2;
  padding-right: 12rpx;
  border-right: 2rpx solid #f0f0f2;
  height: 300rpx;
}

.y-label {
  font-size: 20rpx;
  color: #aeaeb2;
}

.chart-bars-scroll {
  flex: 1;
  white-space: nowrap;
}

.chart-bars {
  display: flex;
  align-items: flex-end;
  gap: 8rpx;
  padding-bottom: 40rpx;
  height: 300rpx;
}

.chart-bar-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
  height: 100%;
  position: relative;
  min-width: 40rpx;
}

.chart-bar {
  width: 32rpx;
  background: linear-gradient(180deg, rgba(0, 122, 255, 0.15) 0%, #007aff 100%);
  border-radius: 16rpx 16rpx 0 0;
  min-height: 20rpx;
  transition: height 0.4s ease;
}

.chart-bar-label {
  position: absolute;
  bottom: 0;
  font-size: 18rpx;
  color: #aeaeb2;
  white-space: nowrap;
}

.stat-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16rpx;
  padding: 0 32rpx;
  margin: 16rpx 0;
}

.stat-card {
  background: #fff;
  border-radius: 28rpx;
  padding: 28rpx;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-icon {
  font-size: 44rpx;
  margin-bottom: 12rpx;
}

.stat-value-row {
  display: flex;
  align-items: baseline;
  gap: 4rpx;
}

.stat-value {
  font-size: 44rpx;
  font-weight: 700;
  color: #1d1d1f;
}

.stat-unit {
  font-size: 24rpx;
  font-weight: 400;
  color: #86868b;
}

.stat-label {
  font-size: 24rpx;
  color: #86868b;
  margin-top: 4rpx;
}

.calendar-card {
  padding: 32rpx;
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24rpx;
}

.cal-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #1d1d1f;
}

.cal-count {
  font-size: 24rpx;
  color: #007aff;
}

.calendar-grid {
  margin-top: 8rpx;
}

.cal-weekdays {
  display: flex;
  margin-bottom: 12rpx;
}

.cal-weekday {
  flex: 1;
  text-align: center;
  font-size: 22rpx;
  color: #86868b;
  font-weight: 500;
}

.cal-days {
  display: flex;
  flex-wrap: wrap;
  gap: 8rpx;
}

.cal-day {
  width: calc((100% - 48rpx) / 7);
  height: 80rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
}

.cal-day.other {
  opacity: 0.3;
}

.day-num {
  font-size: 26rpx;
  color: #1d1d1f;
}

.cal-day.recorded .day-num {
  color: #007aff;
  font-weight: 600;
}

.day-dot {
  width: 10rpx;
  height: 10rpx;
  background: #34c759;
  border-radius: 50%;
  margin-top: 4rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: 600;
  margin: 32rpx 32rpx 16rpx;
  color: #1d1d1f;
  display: block;
}

.journal-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16rpx;
  margin: 0 32rpx;
  margin-bottom: 32rpx;
}

.journal-card {
  background: #fff;
  border-radius: 24rpx;
  padding: 24rpx;
  display: flex;
  flex-direction: column;
}

.jc-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12rpx;
}

.jc-date {
  display: flex;
  align-items: baseline;
  gap: 6rpx;
}

.jd-day {
  font-size: 36rpx;
  font-weight: 700;
  color: #1d1d1f;
}

.jd-month {
  font-size: 22rpx;
  color: #86868b;
}

.jc-trend {
  font-size: 24rpx;
  font-weight: 600;
}

.jc-weight {
  font-size: 44rpx;
  font-weight: 700;
  color: #1d1d1f;
  line-height: 1.1;
}

.jc-unit {
  font-size: 24rpx;
  font-weight: 400;
  color: #86868b;
  margin-left: 4rpx;
}

.jc-tags {
  display: flex;
  gap: 8rpx;
  flex-wrap: wrap;
  margin-top: 12rpx;
}

.journal-tag {
  font-size: 20rpx;
  color: #86868b;
  background: #f5f5f7;
  padding: 4rpx 12rpx;
  border-radius: 12rpx;
  font-weight: 400;
}

.jc-note {
  font-size: 22rpx;
  color: #aeaeb2;
  margin-top: 12rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.trend-down { color: #34c759; }
.trend-up { color: #ff3b30; }

.full-width {
  width: 100%;
}

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
  background: #fff;
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
  margin-bottom: 40rpx;
}

.sheet-title {
  font-size: 36rpx;
  font-weight: 600;
  color: #1d1d1f;
}

.sheet-close {
  width: 60rpx;
  height: 60rpx;
  border-radius: 50%;
  background: #f5f5f7;
  font-size: 28rpx;
  color: #86868b;
  display: flex;
  align-items: center;
  justify-content: center;
}

.record-form {
  padding-top: 8rpx;
}

.form-group {
  margin-bottom: 28rpx;
}

.form-row {
  display: flex;
  gap: 24rpx;
}

.form-row .form-group {
  flex: 1;
}

.form-label {
  font-size: 28rpx;
  color: #1d1d1f;
  font-weight: 500;
  display: block;
  margin-bottom: 12rpx;
}

.form-input {
  width: 100%;
  height: 88rpx;
  background: #f5f5f7;
  border-radius: 24rpx;
  padding: 0 28rpx;
  font-size: 32rpx;
  color: #1d1d1f;
}

.ph-class {
  color: #aeaeb2;
}

.form-textarea {
  width: 100%;
  background: #f5f5f7;
  border-radius: 24rpx;
  padding: 20rpx 28rpx;
  font-size: 28rpx;
  color: #1d1d1f;
  min-height: 120rpx;
}

.btn-primary {
  width: 100%;
  height: 100rpx;
  background: #007aff;
  color: #fff;
  border-radius: 28rpx;
  font-size: 34rpx;
  font-weight: 600;
  border: none;
  margin-top: 8rpx;
  line-height: 100rpx;
}

.btn-primary[disabled] {
  opacity: 0.5;
  background: #007aff;
  color: #fff;
}

.empty-state {
  text-align: center;
  padding: 80rpx 40rpx;
  color: #aeaeb2;
  font-size: 28rpx;
}

/* Dark Mode */
.dark-mode {
  background: #1a1a1a;
}
.dark-mode .page-header {
  background: #1a1a1a;
}
.dark-mode .page-title {
  color: #f5f5f7;
}
.dark-mode .icon-btn {
  background: #2c2c2e;
}
.dark-mode .card {
  background: #2c2c2e;
}
.dark-mode .weight-main-card .weight-card-content {
  color: #f5f5f7;
}
.dark-mode .range-tab {
  background: #2c2c2e;
  color: #98989d;
}
.dark-mode .chart-card {
  background: #2c2c2e;
}
.dark-mode .chart-title {
  color: #f5f5f7;
}
.dark-mode .chart-subtitle {
  color: #98989d;
}
.dark-mode .stat-card {
  background: #2c2c2e;
}
.dark-mode .stat-value {
  color: #f5f5f7;
}
.dark-mode .stat-label {
  color: #98989d;
}
.dark-mode .calendar-card {
  background: #2c2c2e;
}
.dark-mode .cal-title {
  color: #f5f5f7;
}
.dark-mode .cal-weekday {
  color: #98989d;
}
.dark-mode .day-num {
  color: #f5f5f7;
}
.dark-mode .section-title {
  color: #f5f5f7;
}
.dark-mode .journal-card {
  background: #2c2c2e;
}
.dark-mode .jd-day {
  color: #f5f5f7;
}
.dark-mode .jd-month {
  color: #98989d;
}
.dark-mode .jc-weight {
  color: #f5f5f7;
}
.dark-mode .jc-unit {
  color: #98989d;
}
.dark-mode .journal-tag {
  background: #38383a;
  color: #98989d;
}
.dark-mode .jc-note {
  color: #636366;
}
.dark-mode .bottom-sheet {
  background: #2c2c2e;
}
.dark-mode .sheet-title {
  color: #f5f5f7;
}
.dark-mode .sheet-close {
  background: #38383a;
  color: #98989d;
}
.dark-mode .form-label {
  color: #f5f5f7;
}
.dark-mode .form-input {
  background: #38383a;
  color: #f5f5f7;
}
.dark-mode .form-textarea {
  background: #38383a;
  color: #f5f5f7;
}
.dark-mode .ph-class {
  color: #636366;
}
.dark-mode .loading-text {
  color: #98989d;
}
.dark-mode .y-label {
  color: #636366;
}
.dark-mode .chart-bar-label {
  color: #636366;
}
</style>
