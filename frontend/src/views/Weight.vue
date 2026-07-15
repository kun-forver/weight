<template>
  <div class="page">
    <!-- Header -->
    <header class="page-header">
      <span class="page-title">体重记录</span>
      <button class="icon-btn">📊</button>
    </header>

    <div v-if="loading" class="loading-text">加载中...</div>

    <!-- Big Weight Card -->
    <div class="card weight-main-card" v-if="latestWeight">
      <div class="weight-card-bg"></div>
      <div class="weight-card-content">
        <div class="wmc-top">
          <div class="wmc-left">
            <div class="wmc-label">当前体重</div>
            <div class="wmc-value">
              {{ latestWeight.weight || 0 }}<span class="wmc-unit">kg</span>
            </div>
            <div class="wmc-change" :class="{ 'down': weightChange < 0, 'up': weightChange > 0 }">
              <span class="change-arrow">{{ weightChange < 0 ? '↓' : weightChange > 0 ? '↑' : '→' }}</span>
              {{ Math.abs(weightChange).toFixed(1) }}kg vs 昨日
            </div>
          </div>
          <div class="wmc-right">
            <div class="wmc-stat">
              <div class="wmc-stat-label">目标</div>
              <div class="wmc-stat-value">{{ targetWeight || '未设置' }}<span v-if="targetWeight">kg</span></div>
            </div>
            <div class="wmc-progress-circle">
              <svg width="56" height="56">
                <circle cx="28" cy="28" r="24" fill="none" stroke="rgba(255,255,255,0.3)" stroke-width="5" />
                <circle
                  cx="28" cy="28" r="24" fill="none" stroke="#fff" stroke-width="5"
                  stroke-linecap="round"
                  :stroke-dasharray="150.8"
                  :stroke-dashoffset="150.8 * (1 - (goalProgress / 100))"
                  :transform="'rotate(-90 28 28)'"
                  style="transition: stroke-dashoffset 0.6s ease"
                />
              </svg>
              <div class="progress-pct">{{ Math.round(goalProgress) }}%</div>
            </div>
          </div>
        </div>
        <button class="record-btn" @click="openRecordSheet">+ 记录体重</button>
      </div>
    </div>

    <!-- Range Tabs -->
    <div class="range-tabs">
      <button
        v-for="r in ranges"
        :key="r.key"
        class="range-tab"
        :class="{ active: activeRange === r.key }"
        @click="changeRange(r.key)"
      >{{ r.label }}</button>
    </div>

    <!-- Bar Chart -->
    <div class="card chart-card">
      <div class="chart-header">
        <span class="chart-title">体重趋势</span>
        <span class="chart-subtitle">{{ rangeLabel }}</span>
      </div>
      <div class="bar-chart">
        <div class="chart-y-labels">
          <span>{{ maxWeight.toFixed(1) }}</span>
          <span>{{ ((maxWeight + minWeight) / 2).toFixed(1) }}</span>
          <span>{{ minWeight.toFixed(1) }}</span>
        </div>
        <div class="chart-bars">
          <div
            v-for="(item, i) in chartData"
            :key="i"
            class="chart-bar-wrapper"
          >
            <div class="chart-bar" :style="{ height: barHeightValue(item.weight) + 'px' }"></div>
            <div class="chart-bar-label">{{ item.label }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 4 Stat Cards -->
    <div class="stat-grid">
      <div class="stat-card">
        <div class="stat-icon">📉</div>
        <div class="stat-value">{{ monthlyLoss }}<span class="stat-unit">kg</span></div>
        <div class="stat-label">本月减重</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">⚖️</div>
        <div class="stat-value">{{ latestWeight?.weight || 0 }}<span class="stat-unit">kg</span></div>
        <div class="stat-label">当前体重</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📅</div>
        <div class="stat-value">{{ monthStartWeight }}<span class="stat-unit">kg</span></div>
        <div class="stat-label">月初体重</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📏</div>
        <div class="stat-value">{{ bmi }}</div>
        <div class="stat-label">BMI</div>
      </div>
    </div>

    <!-- Calendar Grid -->
    <div class="card calendar-card">
      <div class="calendar-header">
        <span class="cal-title">打卡日历</span>
        <span class="cal-count">本月已记录 {{ recordedDays }} 天</span>
      </div>
      <div class="calendar-grid">
        <div class="cal-weekdays">
          <span v-for="w in weekdays" :key="w">{{ w }}</span>
        </div>
        <div class="cal-days">
          <div
            v-for="(day, i) in calendarDays"
            :key="i"
            class="cal-day"
            :class="{ recorded: day.recorded, other: !day.currentMonth }"
          >
            <span class="day-num">{{ day.day || '' }}</span>
            <span v-if="day.recorded" class="day-dot"></span>
          </div>
        </div>
      </div>
    </div>

    <!-- Body Journal List -->
    <div class="section-title">体重日志</div>
    <div class="journal-list">
      <div
        v-for="item in weightRecords"
        :key="item.id"
        class="journal-item"
      >
        <div class="journal-date">
          <div class="jd-day">{{ formatDay(item.logged_at) }}</div>
          <div class="jd-month">{{ formatMonth(item.logged_at) }}</div>
        </div>
        <div class="journal-content">
          <div class="journal-weight">
            {{ item.weight }}kg
            <span v-if="item.body_fat" class="journal-tag">体脂 {{ item.body_fat }}%</span>
            <span v-if="item.muscle" class="journal-tag">肌肉 {{ item.muscle }}kg</span>
          </div>
          <div class="journal-note" v-if="item.note">{{ item.note }}</div>
        </div>
        <div class="journal-trend" v-if="item.trend">
          <span :class="item.trend < 0 ? 'trend-down' : 'trend-up'">
            {{ item.trend < 0 ? '↓' : '↑' }} {{ Math.abs(item.trend).toFixed(1) }}
          </span>
        </div>
      </div>
      <div v-if="weightRecords.length === 0" class="empty-state">暂无体重记录</div>
    </div>

    <BottomNav @add="openRecordSheet" />

    <!-- Bottom Sheet: Record Weight -->
    <div v-if="showRecordSheet" class="bottom-sheet-backdrop" @click="closeRecordSheet"></div>
    <div v-if="showRecordSheet" class="bottom-sheet">
      <div class="sheet-header">
        <span class="sheet-title">记录体重</span>
        <button class="sheet-close" @click="closeRecordSheet">✕</button>
      </div>
      <div class="record-form">
        <div class="form-group">
          <label class="form-label">体重 (kg) *</label>
          <input
            v-model.number="recordForm.weight"
            type="number"
            step="0.1"
            placeholder="如 65.5"
            class="form-input"
            autofocus
          />
        </div>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">体脂率 (%)</label>
            <input
              v-model.number="recordForm.body_fat"
              type="number"
              step="0.1"
              placeholder="如 22.5"
              class="form-input"
            />
          </div>
          <div class="form-group">
            <label class="form-label">肌肉量 (kg)</label>
            <input
              v-model.number="recordForm.muscle"
              type="number"
              step="0.1"
              placeholder="如 28.0"
              class="form-input"
            />
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">备注</label>
          <textarea
            v-model="recordForm.note"
            placeholder="如 今天跑步了5公里"
            class="form-textarea"
            rows="2"
          ></textarea>
        </div>
        <button class="btn-primary" @click="saveWeight" :disabled="saving">
          {{ saving ? '保存中...' : '保存记录' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../api'
import { useAuthStore } from '../stores/auth'
import BottomNav from '../components/BottomNav.vue'

const authStore = useAuthStore()

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

  // Previous month tail
  const prevLastDay = new Date(year, month, 0).getDate()
  const days = []
  for (let i = startWeekday - 1; i >= 0; i--) {
    days.push({ day: prevLastDay - i, currentMonth: false, recorded: false })
  }
  // Current month
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
  // Next month head
  while (days.length % 7 !== 0) {
    days.push({ day: days.length - daysInMonth - startWeekday + 1, currentMonth: false, recorded: false })
  }
  return days
})

function barHeightValue(weight) {
  if (!weight) return 0
  const range = maxWeight.value - minWeight.value
  if (range <= 0) return 40
  const h = ((weight - minWeight.value) / range) * 120
  return Math.max(20, h)
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
    // Calculate trend (change from previous record)
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
    alert('请输入体重')
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
    alert('保存失败，请重试')
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  if (!authStore.user) {
    try { await authStore.fetchUser() } catch {}
  }
  await Promise.all([fetchWeights(), fetchLatestWeight(), fetchTodayWeight()])
})
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: #fff;
  position: sticky;
  top: 0;
  z-index: 50;
}

.page-title {
  font-size: 20px;
  font-weight: 700;
  color: #1d1d1f;
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
  border: none;
}

.loading-text {
  text-align: center;
  padding: 20px;
  color: #86868b;
}

.card {
  background: #fff;
  border-radius: 16px;
  padding: 16px;
  margin: 8px 16px;
}

.weight-main-card {
  position: relative;
  overflow: hidden;
  padding: 0;
}

.weight-card-bg {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: linear-gradient(135deg, #007aff 0%, #5ac8fa 100%);
  border-radius: 16px;
}

.weight-card-content {
  position: relative;
  z-index: 1;
  padding: 20px;
  color: #fff;
}

.wmc-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.wmc-left {
  flex: 1;
}

.wmc-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 6px;
}

.wmc-value {
  font-size: 40px;
  font-weight: 700;
  color: #fff;
  line-height: 1;
}

.wmc-unit {
  font-size: 16px;
  font-weight: 400;
  margin-left: 4px;
}

.wmc-change {
  font-size: 13px;
  margin-top: 8px;
  color: rgba(255, 255, 255, 0.9);
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
  gap: 10px;
}

.wmc-stat {
  text-align: right;
}

.wmc-stat-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.7);
}

.wmc-stat-value {
  font-size: 18px;
  font-weight: 600;
  color: #fff;
}

.wmc-stat-value span {
  font-size: 12px;
  font-weight: 400;
  margin-left: 2px;
}

.wmc-progress-circle {
  position: relative;
  width: 56px;
  height: 56px;
}

.progress-pct {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 12px;
  font-weight: 700;
  color: #fff;
}

.record-btn {
  width: 100%;
  height: 44px;
  background: rgba(255, 255, 255, 0.2);
  border: 1.5px solid rgba(255, 255, 255, 0.5);
  border-radius: 14px;
  color: #fff;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.record-btn:active {
  background: rgba(255, 255, 255, 0.3);
}

.range-tabs {
  display: flex;
  gap: 8px;
  padding: 0 16px;
  margin: 12px 0 8px;
}

.range-tab {
  flex: 1;
  height: 36px;
  border-radius: 12px;
  background: #fff;
  font-size: 14px;
  color: #86868b;
  border: none;
  transition: all 0.2s;
}

.range-tab.active {
  background: #007aff;
  color: #fff;
  font-weight: 600;
}

.chart-card {
  padding: 16px 20px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

.chart-title {
  font-size: 16px;
  font-weight: 600;
  color: #1d1d1f;
}

.chart-subtitle {
  font-size: 12px;
  color: #86868b;
}

.bar-chart {
  display: flex;
  gap: 10px;
  height: 160px;
}

.chart-y-labels {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  font-size: 10px;
  color: #aeaeb2;
  padding-right: 6px;
  border-right: 1px solid #f0f0f2;
}

.chart-bars {
  flex: 1;
  display: flex;
  align-items: flex-end;
  gap: 4px;
  overflow-x: auto;
  padding-bottom: 20px;
  position: relative;
}

.chart-bar-wrapper {
  flex: 0 0 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
  height: 100%;
  position: relative;
}

.chart-bar {
  width: 16px;
  background: linear-gradient(180deg, rgba(0, 122, 255, 0.15) 0%, #007aff 100%);
  border-radius: 8px 8px 0 0;
  min-height: 10px;
  transition: height 0.4s cubic-bezier(0.25, 0.8, 0.25, 1), background 0.2s, box-shadow 0.2s;
}

.chart-bar:hover {
  background: linear-gradient(180deg, #5ac8fa 0%, #007aff 100%);
  box-shadow: 0 4px 12px rgba(0, 122, 255, 0.3);
}

.chart-bar-label {
  position: absolute;
  bottom: 0;
  font-size: 9px;
  color: #aeaeb2;
  white-space: nowrap;
}

.stat-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  padding: 0 16px;
  margin: 8px 0;
}

.stat-card {
  background: #fff;
  border-radius: 14px;
  padding: 14px;
  text-align: center;
}

.stat-icon {
  font-size: 22px;
  margin-bottom: 6px;
}

.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: #1d1d1f;
}

.stat-unit {
  font-size: 12px;
  font-weight: 400;
  color: #86868b;
  margin-left: 2px;
}

.stat-label {
  font-size: 12px;
  color: #86868b;
  margin-top: 2px;
}

.calendar-card {
  padding: 16px;
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.cal-title {
  font-size: 16px;
  font-weight: 600;
  color: #1d1d1f;
}

.cal-count {
  font-size: 12px;
  color: #007aff;
}

.calendar-grid {
  margin-top: 4px;
}

.cal-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  margin-bottom: 6px;
}

.cal-weekdays span {
  text-align: center;
  font-size: 11px;
  color: #86868b;
  font-weight: 500;
}

.cal-days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}

.cal-day {
  aspect-ratio: 1;
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
  font-size: 13px;
  color: #1d1d1f;
}

.cal-day.recorded .day-num {
  color: #007aff;
  font-weight: 600;
}

.day-dot {
  width: 5px;
  height: 5px;
  background: #34c759;
  border-radius: 50%;
  margin-top: 2px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  margin: 16px 16px 8px;
  color: #1d1d1f;
}

.journal-list {
  margin: 0 16px;
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  margin-bottom: 16px;
}

.journal-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f2;
}

.journal-item:last-child {
  border-bottom: none;
}

.journal-date {
  flex-shrink: 0;
  text-align: center;
  width: 48px;
}

.jd-day {
  font-size: 20px;
  font-weight: 700;
  color: #1d1d1f;
}

.jd-month {
  font-size: 11px;
  color: #86868b;
}

.journal-content {
  flex: 1;
}

.journal-weight {
  font-size: 15px;
  font-weight: 600;
  color: #1d1d1f;
}

.journal-tag {
  display: inline-block;
  font-size: 11px;
  color: #86868b;
  background: #f5f5f7;
  padding: 1px 6px;
  border-radius: 6px;
  margin-left: 6px;
  font-weight: 400;
}

.journal-note {
  font-size: 12px;
  color: #86868b;
  margin-top: 4px;
}

.journal-trend {
  font-size: 14px;
  font-weight: 600;
}

.trend-down { color: #34c759; }
.trend-up { color: #ff3b30; }

.bottom-sheet-backdrop {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 200;
}

.bottom-sheet {
  position: fixed;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 375px;
  max-width: 100%;
  background: #fff;
  border-radius: 20px 20px 0 0;
  padding: 20px;
  z-index: 201;
  max-height: 85vh;
  overflow-y: auto;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from { transform: translate(-50%, 100%); }
  to { transform: translate(-50%, 0); }
}

.sheet-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.sheet-title {
  font-size: 18px;
  font-weight: 600;
  color: #1d1d1f;
}

.sheet-close {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #f5f5f7;
  font-size: 14px;
  color: #86868b;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
}

.record-form {
  padding-top: 4px;
}

.form-group {
  margin-bottom: 14px;
}

.form-row {
  display: flex;
  gap: 12px;
}

.form-row .form-group {
  flex: 1;
}

.form-label {
  font-size: 14px;
  color: #1d1d1f;
  font-weight: 500;
  display: block;
  margin-bottom: 6px;
}

.form-input {
  width: 100%;
  height: 44px;
  background: #f5f5f7;
  border-radius: 12px;
  padding: 0 14px;
  font-size: 16px;
  color: #1d1d1f;
  border: none;
  outline: none;
}

.form-textarea {
  width: 100%;
  background: #f5f5f7;
  border-radius: 12px;
  padding: 10px 14px;
  font-size: 14px;
  color: #1d1d1f;
  border: none;
  outline: none;
  resize: none;
  font-family: inherit;
}

.btn-primary {
  width: 100%;
  height: 50px;
  background: #007aff;
  color: #fff;
  border-radius: 14px;
  font-size: 17px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  margin-top: 4px;
}

.btn-primary:active { opacity: 0.85; }
.btn-primary:disabled { opacity: 0.5; }

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #aeaeb2;
  font-size: 14px;
}
</style>
