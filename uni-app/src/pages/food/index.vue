<template>
  <view class="page">
    <!-- Header -->
    <view class="page-header">
      <text class="page-title">饮食记录</text>
      <view class="icon-btn">📊</view>
    </view>

    <!-- Date Navigation -->
    <view class="date-nav">
      <view class="date-arrow" @tap="changeDate(-1)">‹</view>
      <view class="date-display">
        <text class="date-main">{{ formatDateDisplay(currentDate) }}</text>
        <text class="date-sub" v-if="isToday(currentDate)">今天</text>
      </view>
      <view class="date-arrow" @tap="changeDate(1)">›</view>
    </view>

    <!-- Calorie Summary -->
    <view class="card summary-card" v-if="summary">
      <view class="summary-ring-mini">
        <CalorieRingMini :consumed="summary.total_calories || 0" :goal="dailyGoal" :size="100" />
      </view>
      <view class="summary-stats">
        <view class="ss-item">
          <text class="ss-value green">{{ summary.remaining_calories || 0 }}</text>
          <text class="ss-label">剩余可吃</text>
        </view>
        <view class="ss-item">
          <text class="ss-value orange">{{ summary.total_calories || 0 }}</text>
          <text class="ss-label">已摄入</text>
        </view>
        <view class="ss-item">
          <text class="ss-value blue">{{ totalExercise }}</text>
          <text class="ss-label">运动消耗</text>
        </view>
      </view>
    </view>

    <!-- Meal Summary Cards -->
    <view class="meal-summary-row" v-if="summary">
      <view v-for="meal in meals" :key="meal.type" class="meal-summary-card">
        <text class="ms-emoji">{{ meal.emoji }}</text>
        <text class="ms-name">{{ meal.label }}</text>
        <text class="ms-cal">{{ summary.meals?.[meal.type]?.calories || 0 }}</text>
        <text class="ms-unit">kcal</text>
      </view>
    </view>

    <!-- Search Bar -->
    <view class="search-row">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="搜索食物..."
        class="search-input"
        placeholder-class="ph-class"
        :disabled="searching"
        @confirm="doSearch"
      />
      <view class="search-btn" @tap="doSearch" :class="{ disabled: searching }">
        <text>{{ searching ? '...' : '🔍' }}</text>
      </view>
    </view>

    <!-- Category Pills -->
    <scroll-view scroll-x class="category-pills-scroll">
      <view class="category-pills">
        <view
          v-for="cat in categories"
          :key="cat.key"
          class="cat-pill"
          :class="{ active: activeCategory === cat.key }"
          @tap="activeCategory = cat.key"
        >{{ cat.label }}</view>
      </view>
    </scroll-view>

    <!-- Quick Foods -->
    <text class="section-title">常吃食物</text>
    <view class="quick-foods">
      <view
        v-for="food in filteredQuickFoods"
        :key="food.id"
        class="quick-food-item"
        @tap="openAddSheet(food)"
      >
        <text class="qf-emoji">{{ foodEmoji(food.category) }}</text>
        <view class="qf-info">
          <text class="qf-name">{{ food.name }}</text>
          <text class="qf-cal">{{ food.calories }} kcal/100g</text>
        </view>
        <view class="qf-add-btn" @tap.stop="openAddSheet(food)">+</view>
      </view>
      <view v-if="filteredQuickFoods.length === 0" class="empty-state">
        <text>搜索并添加食物后会出现在这里</text>
      </view>
    </view>

    <!-- Search Results -->
    <view v-if="searchResults.length > 0" class="search-results">
      <text class="section-title">搜索结果</text>
      <view
        v-for="food in searchResults"
        :key="food.id"
        class="quick-food-item"
        @tap="openAddSheet(food)"
      >
        <text class="qf-emoji">{{ foodEmoji(food.category) }}</text>
        <view class="qf-info">
          <text class="qf-name">{{ food.name }}</text>
          <view class="qf-cal-row">
            <text class="qf-cal">{{ food.calories }}kcal · P{{ food.protein }} C{{ food.carbs }} F{{ food.fat }}</text>
            <text v-if="food.is_custom" class="custom-tag">自定义</text>
          </view>
        </view>
        <view class="qf-add-btn" @tap.stop="openAddSheet(food)">+</view>
      </view>
    </view>

    <!-- Today's Food Logs Grouped by Meal -->
    <text class="section-title">今日记录</text>
    <view v-for="meal in meals" :key="meal.type" class="meal-group">
      <view class="meal-header">
        <text class="meal-name">{{ meal.emoji }} {{ meal.label }}</text>
        <view class="meal-add-btn" @tap="openAddSheetForMeal(meal.type)">+</view>
      </view>
      <view v-if="getMealLogs(meal.type).length === 0" class="empty-meal">
        <text>点击 + 添加{{ meal.label }}</text>
      </view>
      <view
        v-for="log in getMealLogs(meal.type)"
        :key="log.id"
        class="swipe-container"
      >
        <view class="swipe-delete" @tap="deleteLog(log.id)"><text>删除</text></view>
        <view
          class="log-item swipe-content"
          :style="{ transform: `translateX(-${swipeOffset[log.id] || 0}px)` }"
          @touchstart="onSwipeStart($event, log.id)"
          @touchmove="onSwipeMove($event, log.id)"
          @touchend="onSwipeEnd(log.id)"
        >
          <text class="log-emoji">{{ log.food_emoji || '🍽️' }}</text>
          <view class="log-info">
            <text class="log-name">{{ log.food_name }}</text>
            <text class="log-meta">{{ log.amount }}g · {{ log.protein || 0 }}g蛋白质 · {{ formatTime(log.logged_at) }}</text>
          </view>
          <view class="log-cal-row">
            <text class="log-cal">{{ log.calories }}</text>
            <text class="log-cal-unit">kcal</text>
          </view>
          <view class="log-delete-btn" @tap.stop="deleteLog(log.id)">×</view>
        </view>
      </view>
    </view>

    <!-- Bottom Sheet: Add Food -->
    <view v-if="showAddSheet" class="bottom-sheet-backdrop" @tap="closeAddSheet"></view>
    <view v-if="showAddSheet" class="bottom-sheet">
      <view class="sheet-header">
        <text class="sheet-title">添加食物</text>
        <view class="sheet-close" @tap="closeAddSheet">✕</view>
      </view>

      <!-- Step 1: Search -->
      <view v-if="!selectedFood" class="sheet-search">
        <view class="search-row">
          <input
            v-model="sheetSearchQuery"
            type="text"
            placeholder="搜索食物名称..."
            class="search-input"
            placeholder-class="ph-class"
            :disabled="sheetSearching"
            @confirm="sheetSearch"
          />
          <view class="search-btn" @tap="sheetSearch" :class="{ disabled: sheetSearching }">
            <text>{{ sheetSearching ? '...' : '🔍' }}</text>
          </view>
        </view>

        <scroll-view scroll-y class="sheet-results">
          <view
            v-for="food in sheetResults"
            :key="food.id"
            class="sheet-result-item"
            @tap="selectFood(food)"
          >
            <text class="qf-emoji">{{ foodEmoji(food.category) }}</text>
            <view class="qf-info">
              <text class="qf-name">{{ food.name }}</text>
              <text class="qf-cal">{{ food.calories }} kcal/100g</text>
            </view>
            <text class="select-arrow">›</text>
          </view>
          <view v-if="sheetSearched && sheetResults.length === 0" class="empty-state">
            <text>未找到食物，试试创建自定义食物</text>
          </view>
        </scroll-view>

        <!-- Custom Food Form -->
        <view class="custom-section">
          <view class="custom-title" @tap="showCustomForm = !showCustomForm">
            <text class="custom-title-text">+ 创建自定义食物</text>
            <text class="toggle-icon">{{ showCustomForm ? '−' : '+' }}</text>
          </view>
          <view v-if="showCustomForm" class="custom-form">
            <input v-model="customFood.name" placeholder="食物名称" class="custom-input" placeholder-class="ph-class" />
            <view class="custom-row">
              <input v-model="customFood.calories" type="number" placeholder="热量(kcal/100g)" class="custom-input" placeholder-class="ph-class" />
              <input v-model="customFood.protein" type="number" placeholder="蛋白质(g)" class="custom-input" placeholder-class="ph-class" />
            </view>
            <view class="custom-row">
              <input v-model="customFood.carbs" type="number" placeholder="碳水(g)" class="custom-input" placeholder-class="ph-class" />
              <input v-model="customFood.fat" type="number" placeholder="脂肪(g)" class="custom-input" placeholder-class="ph-class" />
            </view>
            <picker
              :range="categoryOptions"
              range-key="label"
              :value="customCategoryIndex"
              @change="onCategoryChange"
              class="custom-picker"
            >
              <view class="picker-display">{{ customFood.category || '选择分类' }}</view>
            </picker>
            <button class="btn-primary" @tap="createCustomFood">保存自定义食物</button>
          </view>
        </view>
      </view>

      <!-- Step 2: Input grams and save -->
      <view v-else class="sheet-confirm">
        <view class="selected-food-card">
          <text class="sf-emoji">{{ foodEmoji(selectedFood.category) }}</text>
          <view class="sf-info">
            <text class="sf-name">{{ selectedFood.name }}</text>
            <text class="sf-cal">{{ selectedFood.calories }} kcal / 100g</text>
            <text class="sf-nutri">蛋白{{ selectedFood.protein }}g · 碳水{{ selectedFood.carbs }}g · 脂肪{{ selectedFood.fat }}g</text>
          </view>
        </view>

        <view class="amount-section">
          <text class="amount-label">摄入量</text>
          <view class="amount-input-row">
            <view class="amount-btn" @tap="adjustAmount(-50)">−</view>
            <input
              v-model="foodAmount"
              type="number"
              class="amount-input"
              placeholder-class="ph-class"
            />
            <text class="amount-unit">g</text>
            <view class="amount-btn" @tap="adjustAmount(50)">+</view>
          </view>
          <text class="calorie-preview">预计摄入 ≈ {{ Math.round(calcCalories) }} kcal</text>
        </view>

        <view class="meal-select-section">
          <text class="amount-label">餐次</text>
          <view class="meal-pills">
            <view
              v-for="meal in meals"
              :key="meal.type"
              class="meal-pill"
              :class="{ active: selectedMealType === meal.type }"
              @tap="selectedMealType = meal.type"
            >{{ meal.emoji }} {{ meal.label }}</view>
          </view>
        </view>

        <button class="btn-primary" @tap="saveFoodLog" :disabled="saving">
          {{ saving ? '保存中...' : '确认添加' }}
        </button>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { onLoad, onShow } from '@dcloudio/uni-app'
import api from '../../api'
import { useAuthStore } from '../../stores/auth'
import CalorieRingMini from '../../components/CalorieRing.vue'

const authStore = useAuthStore()

const currentDate = ref(new Date().toISOString().split('T')[0])
const summary = ref(null)
const foodLogs = ref([])
const quickFoods = ref([])
const loading = ref(false)

const searchQuery = ref('')
const searchResults = ref([])
const searching = ref(false)
const activeCategory = ref('all')

const showAddSheet = ref(false)
const selectedFood = ref(null)
const foodAmount = ref(100)
const selectedMealType = ref(1)
const saving = ref(false)

const sheetSearchQuery = ref('')
const sheetResults = ref([])
const sheetSearched = ref(false)
const sheetSearching = ref(false)

const showCustomForm = ref(false)
const customFood = ref({
  name: '', calories: '', protein: '', carbs: '', fat: '', category: ''
})
const customCategoryIndex = 0

const swipeOffset = reactive({})
let swipeStartX = 0
let swipeStartOffset = 0
const SWIPE_THRESHOLD = 60
const SWIPE_OPEN = 80

const meals = [
  { type: 0, label: '早餐', emoji: '🍳' },
  { type: 1, label: '午餐', emoji: '🥗' },
  { type: 2, label: '晚餐', emoji: '🍲' },
  { type: 3, label: '加餐', emoji: '🍪' },
]

const categories = [
  { key: 'all', label: '全部' },
  { key: '主食', label: '主食' },
  { key: '肉蛋', label: '肉蛋' },
  { key: '蔬菜', label: '蔬菜' },
  { key: '水果', label: '水果' },
  { key: '饮品', label: '饮品' },
  { key: '零食', label: '零食' },
]

const categoryOptions = categories.slice(1)

const dailyGoal = computed(() => authStore.user?.daily_calorie_goal || 2000)
const totalExercise = ref(0)

const filteredQuickFoods = computed(() => {
  if (activeCategory.value === 'all') return quickFoods.value
  return quickFoods.value.filter(f => f.category === activeCategory.value)
})

const calcCalories = computed(() => {
  if (!selectedFood.value) return 0
  return (selectedFood.value.calories / 100) * (foodAmount.value || 0)
})

function formatDateDisplay(dateStr) {
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}月${d.getDate()}日`
}

function isToday(dateStr) {
  return dateStr === new Date().toISOString().split('T')[0]
}

function changeDate(delta) {
  const d = new Date(currentDate.value)
  d.setDate(d.getDate() + delta)
  currentDate.value = d.toISOString().split('T')[0]
  fetchDayData()
}

function getMealLogs(mealType) {
  return foodLogs.value.filter(l => l.meal_type === mealType)
}

function foodEmoji(category) {
  const map = {
    '主食': '🍚', '肉蛋': '🥩', '蔬菜': '🥦', '水果': '🍎',
    '饮品': '🥤', '零食': '🍪', '': '🍽️'
  }
  return map[category] || '🍽️'
}

function formatTime(timeStr) {
  if (!timeStr) return ''
  const d = new Date(timeStr)
  return `${d.getHours()}:${String(d.getMinutes()).padStart(2, '0')}`
}

function onCategoryChange(e) {
  const idx = e.detail.value
  customFood.value.category = categoryOptions[idx].key
}

async function fetchDayData() {
  loading.value = true
  try {
    const [summaryRes, logsRes] = await Promise.all([
      api.get(`/food-logs/summary?date=${currentDate.value}`),
      api.get(`/food-logs?date=${currentDate.value}`),
    ])
    const rawSummaries = summaryRes.data || []
    const mealsMap = {}
    let totalCal = 0
    let totalProtein = 0
    let totalCarbs = 0
    let totalFat = 0
    for (const s of rawSummaries) {
      mealsMap[s.meal_type] = {
        calories: s.total_calories || 0,
        protein: s.total_protein || 0,
        carbs: s.total_carbs || 0,
        fat: s.total_fat || 0,
        count: s.count || 0,
      }
      totalCal += s.total_calories || 0
      totalProtein += s.total_protein || 0
      totalCarbs += s.total_carbs || 0
      totalFat += s.total_fat || 0
    }
    summary.value = {
      total_calories: totalCal,
      total_protein: totalProtein,
      total_carbs: totalCarbs,
      total_fat: totalFat,
      remaining_calories: Math.max(0, (dailyGoal.value || 2000) - totalCal),
      meals: mealsMap,
    }
    foodLogs.value = logsRes.data || []
    const seen = new Set()
    quickFoods.value = foodLogs.value
      .filter(l => {
        if (seen.has(l.food_name)) return false
        seen.add(l.food_name)
        return true
      })
      .map(l => ({
        id: l.food_id,
        name: l.food_name,
        category: '',
        calories: l.amount > 0 ? Math.round(l.calories / l.amount * 100) : 0,
        protein: l.amount > 0 ? Math.round(l.protein / l.amount * 100) : 0,
        carbs: l.amount > 0 ? Math.round(l.carbs / l.amount * 100) : 0,
        fat: l.amount > 0 ? Math.round(l.fat / l.amount * 100) : 0,
        is_custom: false,
      }))
  } catch (e) {
    summary.value = null
    foodLogs.value = []
  } finally {
    loading.value = false
  }
}

async function doSearch() {
  if (!searchQuery.value.trim() || searching.value) return
  searching.value = true
  searchResults.value = []
  try {
    const res = await api.get(`/foods/search?q=${encodeURIComponent(searchQuery.value)}`)
    searchResults.value = res.data || []
    if (searchResults.value.length === 0) {
      uni.showToast({ title: '未找到相关食物', icon: 'none' })
    }
  } catch (e) {
    const detail = e?.data?.detail || e?.response?.data?.detail
    uni.showToast({ title: '搜索失败: ' + (typeof detail === 'string' ? detail : ''), icon: 'none' })
    searchResults.value = []
  } finally {
    searching.value = false
  }
}

function openAddSheet(food = null, mealType = null) {
  showAddSheet.value = true
  sheetSearchQuery.value = ''
  sheetResults.value = []
  sheetSearched.value = false
  showCustomForm.value = false
  selectedMealType.value = mealType ?? 1
  if (food) {
    selectedFood.value = food
    foodAmount.value = 100
  } else {
    selectedFood.value = null
  }
}

function openAddSheetForMeal(mealType) {
  openAddSheet(null, mealType)
}

function closeAddSheet() {
  showAddSheet.value = false
  selectedFood.value = null
  foodAmount.value = 100
}

async function sheetSearch() {
  if (!sheetSearchQuery.value.trim() || sheetSearching.value) return
  sheetSearching.value = true
  sheetResults.value = []
  try {
    const res = await api.get(`/foods/search?q=${encodeURIComponent(sheetSearchQuery.value)}`)
    sheetResults.value = res.data || []
    sheetSearched.value = true
    if (sheetResults.value.length === 0) {
      uni.showToast({ title: '未找到相关食物', icon: 'none' })
    }
  } catch (e) {
    const detail = e?.data?.detail || e?.response?.data?.detail
    uni.showToast({ title: '搜索失败', icon: 'none' })
    sheetResults.value = []
    sheetSearched.value = true
  } finally {
    sheetSearching.value = false
  }
}

function selectFood(food) {
  selectedFood.value = food
  foodAmount.value = 100
}

function adjustAmount(delta) {
  foodAmount.value = Math.max(10, (foodAmount.value || 0) + delta)
}

async function createCustomFood() {
  if (!customFood.value.name || !customFood.value.calories) {
    uni.showToast({ title: '请填写食物名称和热量', icon: 'none' })
    return
  }
  try {
    await api.post('/foods/custom', {
      name: customFood.value.name,
      category: customFood.value.category || '其他',
      calories: Number(customFood.value.calories),
      protein: Number(customFood.value.protein) || 0,
      carbs: Number(customFood.value.carbs) || 0,
      fat: Number(customFood.value.fat) || 0,
    })
    uni.showToast({ title: '自定义食物创建成功', icon: 'success' })
    const savedName = customFood.value.name
    customFood.value = { name: '', calories: '', protein: '', carbs: '', fat: '', category: '' }
    showCustomForm.value = false
    sheetSearchQuery.value = savedName
    await sheetSearch()
  } catch (e) {
    uni.showToast({ title: '创建失败', icon: 'none' })
  }
}

async function saveFoodLog() {
  if (!selectedFood.value || !foodAmount.value) return
  saving.value = true
  try {
    await api.post('/food-logs', {
      food_id: selectedFood.value.id,
      meal_type: selectedMealType.value,
      amount: foodAmount.value,
    })
    closeAddSheet()
    await fetchDayData()
  } catch (e) {
    uni.showToast({ title: '添加失败，请重试', icon: 'none' })
  } finally {
    saving.value = false
  }
}

async function deleteLog(id) {
  uni.showModal({
    title: '确认删除',
    content: '确定删除这条记录？',
    success: async (res) => {
      if (!res.confirm) return
      try {
        await api.delete(`/food-logs/${id}`)
        delete swipeOffset[id]
        await fetchDayData()
      } catch (e) {
        uni.showToast({ title: '删除失败', icon: 'none' })
      }
    }
  })
}

function onSwipeStart(e, id) {
  swipeStartX = e.touches[0].clientX
  swipeStartOffset = swipeOffset[id] || 0
}

function onSwipeMove(e, id) {
  const delta = swipeStartX - e.touches[0].clientX
  let offset = swipeStartOffset + delta
  if (offset < 0) offset = 0
  if (offset > 120) offset = 120
  swipeOffset[id] = offset
}

function onSwipeEnd(id) {
  if (swipeOffset[id] > SWIPE_THRESHOLD) {
    swipeOffset[id] = SWIPE_OPEN
  } else {
    swipeOffset[id] = 0
  }
}

onLoad(() => {
  fetchDayData()
})

onShow(() => {
  if (!loading.value && foodLogs.value.length > 0) {
    fetchDayData()
  }
})
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #f5f5f7;
  padding-bottom: 40rpx;
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

.date-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24rpx 32rpx;
  background: #fff;
  margin-top: 120rpx;
}

.date-arrow {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48rpx;
  color: #007aff;
}

.date-display {
  text-align: center;
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.date-main {
  font-size: 32rpx;
  font-weight: 600;
  color: #1d1d1f;
}

.date-sub {
  font-size: 24rpx;
  color: #007aff;
}

.card {
  background: #fff;
  border-radius: 32rpx;
  padding: 32rpx;
  margin: 16rpx 32rpx;
}

.summary-card {
  display: flex;
  align-items: center;
  gap: 32rpx;
}

.summary-ring-mini {
  flex-shrink: 0;
  width: 200rpx;
  height: 200rpx;
}

.summary-stats {
  flex: 1;
  display: flex;
  justify-content: space-around;
}

.ss-item {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.ss-value {
  font-size: 36rpx;
  font-weight: 700;
}

.ss-value.green { color: #34c759; }
.ss-value.orange { color: #ff9500; }
.ss-value.blue { color: #007aff; }

.ss-label {
  font-size: 22rpx;
  color: #86868b;
  margin-top: 4rpx;
}

.meal-summary-row {
  display: flex;
  gap: 16rpx;
  padding: 0 32rpx;
  margin-bottom: 16rpx;
}

.meal-summary-card {
  flex: 1;
  background: #fff;
  border-radius: 24rpx;
  padding: 20rpx 12rpx;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.ms-emoji {
  font-size: 36rpx;
}

.ms-name {
  font-size: 22rpx;
  color: #86868b;
  margin-top: 4rpx;
}

.ms-cal {
  font-size: 30rpx;
  font-weight: 600;
  color: #1d1d1f;
  margin-top: 4rpx;
}

.ms-unit {
  font-size: 20rpx;
  color: #aeaeb2;
}

.search-row {
  display: flex;
  gap: 16rpx;
  padding: 0 32rpx;
  margin: 16rpx 0;
}

.search-input {
  flex: 1;
  height: 80rpx;
  background: #fff;
  border-radius: 24rpx;
  padding: 0 28rpx;
  font-size: 28rpx;
  color: #1d1d1f;
}

.ph-class {
  color: #aeaeb2;
}

.search-btn {
  width: 80rpx;
  height: 80rpx;
  background: #007aff;
  border-radius: 24rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32rpx;
  color: #fff;
}

.search-btn.disabled {
  opacity: 0.5;
}

.category-pills-scroll {
  white-space: nowrap;
  margin-bottom: 8rpx;
}

.category-pills {
  display: flex;
  gap: 16rpx;
  padding: 0 32rpx;
}

.cat-pill {
  white-space: nowrap;
  padding: 12rpx 28rpx;
  border-radius: 40rpx;
  font-size: 26rpx;
  color: #86868b;
  background: #fff;
  transition: all 0.2s;
}

.cat-pill.active {
  background: #007aff;
  color: #fff;
  font-weight: 600;
}

.section-title {
  font-size: 32rpx;
  font-weight: 600;
  margin: 32rpx 32rpx 16rpx;
  color: #1d1d1f;
  display: block;
}

.quick-foods {
  margin: 0 32rpx;
  background: #fff;
  border-radius: 32rpx;
  overflow: hidden;
}

.quick-food-item {
  display: flex;
  align-items: center;
  gap: 24rpx;
  padding: 24rpx 32rpx;
  border-bottom: 2rpx solid #f0f0f2;
}

.quick-food-item:last-child {
  border-bottom: none;
}

.qf-emoji {
  font-size: 48rpx;
  width: 72rpx;
  text-align: center;
}

.qf-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.qf-name {
  font-size: 28rpx;
  font-weight: 500;
  color: #1d1d1f;
}

.qf-cal {
  font-size: 24rpx;
  color: #86868b;
  margin-top: 4rpx;
}

.qf-cal-row {
  display: flex;
  align-items: center;
  gap: 8rpx;
  margin-top: 4rpx;
}

.custom-tag {
  font-size: 20rpx;
  color: #007aff;
  background: #eef4ff;
  padding: 2rpx 12rpx;
  border-radius: 12rpx;
}

.qf-add-btn {
  width: 56rpx;
  height: 56rpx;
  border-radius: 50%;
  background: #007aff;
  color: #fff;
  font-size: 40rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

.search-results {
  margin-top: 16rpx;
}

.search-results .quick-food-item {
  background: #fff;
}

.meal-group {
  margin: 0 32rpx 24rpx;
  background: #fff;
  border-radius: 32rpx;
  padding: 28rpx 32rpx;
}

.meal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
  padding-bottom: 16rpx;
  border-bottom: 2rpx solid #f0f0f2;
}

.meal-name {
  font-size: 30rpx;
  font-weight: 600;
  color: #1d1d1f;
}

.meal-add-btn {
  width: 56rpx;
  height: 56rpx;
  border-radius: 50%;
  background: #f0f0f2;
  color: #007aff;
  font-size: 40rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

.empty-meal {
  font-size: 26rpx;
  color: #aeaeb2;
  padding: 16rpx 0;
  text-align: center;
}

.log-item {
  display: flex;
  align-items: center;
  gap: 24rpx;
  padding: 16rpx 32rpx;
  background: #fff;
}

.swipe-container {
  position: relative;
  overflow: hidden;
  margin-bottom: 4rpx;
}

.swipe-delete {
  position: absolute;
  top: 0;
  right: 0;
  width: 160rpx;
  height: 100%;
  background: #ff3b30;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
  font-weight: 600;
}

.swipe-content {
  position: relative;
  background: #fff;
  transition: transform 0.3s ease;
  will-change: transform;
}

.log-emoji {
  font-size: 48rpx;
  width: 72rpx;
  text-align: center;
}

.log-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.log-name {
  font-size: 28rpx;
  font-weight: 500;
  color: #1d1d1f;
}

.log-meta {
  font-size: 24rpx;
  color: #86868b;
  margin-top: 4rpx;
}

.log-cal-row {
  display: flex;
  align-items: baseline;
  gap: 4rpx;
}

.log-cal {
  font-size: 32rpx;
  font-weight: 600;
  color: #ff9500;
}

.log-cal-unit {
  font-size: 22rpx;
  color: #aeaeb2;
}

.log-delete-btn {
  width: 56rpx;
  height: 56rpx;
  border-radius: 50%;
  background: #f0f0f2;
  color: #ff3b30;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36rpx;
  font-weight: 700;
  margin-left: 16rpx;
  flex-shrink: 0;
}

.bottom-sheet-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
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
  margin-bottom: 32rpx;
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

.sheet-results {
  margin-top: 24rpx;
  max-height: 600rpx;
}

.sheet-result-item {
  display: flex;
  align-items: center;
  gap: 24rpx;
  padding: 20rpx 0;
  border-bottom: 2rpx solid #f0f0f2;
}

.select-arrow {
  font-size: 40rpx;
  color: #aeaeb2;
}

.custom-section {
  margin-top: 32rpx;
  border-top: 2rpx solid #f0f0f2;
  padding-top: 24rpx;
}

.custom-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.custom-title-text {
  font-size: 28rpx;
  color: #007aff;
  font-weight: 500;
}

.toggle-icon {
  font-size: 36rpx;
  color: #007aff;
}

.custom-form {
  margin-top: 24rpx;
}

.custom-input {
  width: 100%;
  height: 80rpx;
  background: #f5f5f7;
  border-radius: 20rpx;
  padding: 0 24rpx;
  font-size: 28rpx;
  color: #1d1d1f;
  margin-bottom: 16rpx;
}

.custom-row {
  display: flex;
  gap: 16rpx;
}

.custom-row .custom-input {
  flex: 1;
}

.custom-picker {
  width: 100%;
  margin-bottom: 24rpx;
}

.picker-display {
  width: 100%;
  height: 80rpx;
  background: #f5f5f7;
  border-radius: 20rpx;
  padding: 0 24rpx;
  font-size: 28rpx;
  color: #1d1d1f;
  line-height: 80rpx;
}

.sheet-confirm {
  padding-top: 8rpx;
}

.selected-food-card {
  display: flex;
  gap: 24rpx;
  background: #f5f5f7;
  border-radius: 28rpx;
  padding: 28rpx;
  margin-bottom: 32rpx;
}

.sf-emoji {
  font-size: 72rpx;
  width: 96rpx;
  text-align: center;
}

.sf-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.sf-name {
  font-size: 32rpx;
  font-weight: 600;
  color: #1d1d1f;
}

.sf-cal {
  font-size: 26rpx;
  color: #007aff;
  margin-top: 4rpx;
}

.sf-nutri {
  font-size: 24rpx;
  color: #86868b;
  margin-top: 8rpx;
}

.amount-section {
  margin-bottom: 32rpx;
}

.amount-label {
  font-size: 28rpx;
  color: #1d1d1f;
  font-weight: 500;
  display: block;
  margin-bottom: 16rpx;
}

.amount-input-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.amount-btn {
  width: 80rpx;
  height: 88rpx;
  border-radius: 24rpx;
  background: #f5f5f7;
  font-size: 44rpx;
  color: #007aff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.amount-input {
  flex: 1;
  height: 88rpx;
  background: #f5f5f7;
  border-radius: 24rpx;
  text-align: center;
  font-size: 36rpx;
  font-weight: 600;
  color: #1d1d1f;
}

.amount-unit {
  font-size: 32rpx;
  color: #86868b;
}

.calorie-preview {
  text-align: center;
  font-size: 28rpx;
  color: #ff9500;
  font-weight: 600;
  margin-top: 20rpx;
  display: block;
}

.meal-select-section {
  margin-bottom: 40rpx;
}

.meal-pills {
  display: flex;
  gap: 16rpx;
  flex-wrap: wrap;
}

.meal-pill {
  flex: 1;
  padding: 16rpx 8rpx;
  border-radius: 24rpx;
  font-size: 26rpx;
  color: #86868b;
  background: #f5f5f7;
  text-align: center;
}

.meal-pill.active {
  background: #007aff;
  color: #fff;
  font-weight: 600;
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
</style>
