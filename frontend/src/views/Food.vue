<template>
  <div class="page">
    <!-- Header -->
    <header class="page-header">
      <span class="page-title">饮食记录</span>
      <button class="icon-btn">📊</button>
    </header>

    <!-- Date Navigation -->
    <div class="date-nav">
      <button class="date-arrow" @click="changeDate(-1)">‹</button>
      <div class="date-display">
        <span class="date-main">{{ formatDateDisplay(currentDate) }}</span>
        <span class="date-sub" v-if="isToday(currentDate)">今天</span>
      </div>
      <button class="date-arrow" @click="changeDate(1)">›</button>
    </div>

    <!-- Calorie Summary -->
    <div class="card summary-card" v-if="summary">
      <div class="summary-ring-mini">
        <CalorieRingMini :consumed="summary.total_calories || 0" :goal="dailyGoal" :size="100" />
      </div>
      <div class="summary-stats">
        <div class="ss-item">
          <div class="ss-value green">{{ summary.remaining_calories || 0 }}</div>
          <div class="ss-label">剩余可吃</div>
        </div>
        <div class="ss-item">
          <div class="ss-value orange">{{ summary.total_calories || 0 }}</div>
          <div class="ss-label">已摄入</div>
        </div>
        <div class="ss-item">
          <div class="ss-value blue">{{ totalExercise }}</div>
          <div class="ss-label">运动消耗</div>
        </div>
      </div>
    </div>

    <!-- Meal Summary Cards -->
    <div class="meal-summary-row" v-if="summary">
      <div v-for="meal in meals" :key="meal.type" class="meal-summary-card">
        <div class="ms-emoji">{{ meal.emoji }}</div>
        <div class="ms-name">{{ meal.label }}</div>
        <div class="ms-cal">{{ summary.meals?.[meal.type]?.calories || 0 }}</div>
        <div class="ms-unit">kcal</div>
      </div>
    </div>

    <!-- Search Bar -->
    <div class="search-row">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="搜索食物..."
        class="search-input"
        @keyup.enter="doSearch"
        :disabled="searching"
      />
      <button class="search-btn" @click="doSearch" :disabled="searching">
        {{ searching ? '...' : '🔍' }}
      </button>
    </div>

    <!-- Category Pills -->
    <div class="category-pills">
      <button
        v-for="cat in categories"
        :key="cat.key"
        class="cat-pill"
        :class="{ active: activeCategory === cat.key }"
        @click="activeCategory = cat.key"
      >{{ cat.label }}</button>
    </div>

    <!-- Quick Foods -->
    <div class="section-title">常吃食物</div>
    <div class="quick-foods">
      <div
        v-for="food in filteredQuickFoods"
        :key="food.id"
        class="quick-food-item"
        @click="openAddSheet(food)"
      >
        <div class="qf-emoji">{{ foodEmoji(food.category) }}</div>
        <div class="qf-info">
          <div class="qf-name">{{ food.name }}</div>
          <div class="qf-cal">{{ food.calories }} kcal/100g</div>
        </div>
        <button class="qf-add-btn" @click.stop="openAddSheet(food)">+</button>
      </div>
      <div v-if="filteredQuickFoods.length === 0" class="empty-state">
        搜索并添加食物后会出现在这里
      </div>
    </div>

    <!-- Search Results -->
    <div v-if="searchResults.length > 0" class="search-results">
      <div class="section-title">搜索结果</div>
      <div
        v-for="food in searchResults"
        :key="food.id"
        class="quick-food-item"
        @click="openAddSheet(food)"
      >
        <div class="qf-emoji">{{ foodEmoji(food.category) }}</div>
        <div class="qf-info">
          <div class="qf-name">{{ food.name }}</div>
          <div class="qf-cal">
            {{ food.calories }}kcal · P{{ food.protein }} C{{ food.carbs }} F{{ food.fat }}
            <span v-if="food.is_custom" class="custom-tag">自定义</span>
          </div>
        </div>
        <button class="qf-add-btn" @click.stop="openAddSheet(food)">+</button>
      </div>
    </div>

    <!-- Today's Food Logs Grouped by Meal -->
    <div class="section-title">今日记录</div>
    <div v-for="meal in meals" :key="meal.type" class="meal-group">
      <div class="meal-header">
        <span class="meal-name">{{ meal.emoji }} {{ meal.label }}</span>
        <button class="meal-add-btn" @click="openAddSheetForMeal(meal.type)">+</button>
      </div>
      <div v-if="getMealLogs(meal.type).length === 0" class="empty-meal">
        点击 + 添加{{ meal.label }}
      </div>
      <div
        v-for="log in getMealLogs(meal.type)"
        :key="log.id"
        class="swipe-container"
      >
        <div class="swipe-delete" @click="deleteLog(log.id)">删除</div>
        <div
          class="log-item swipe-content"
          :style="{ transform: `translateX(-${swipeOffset[log.id] || 0}px)` }"
          @touchstart="onSwipeStart($event, log.id)"
          @touchmove="onSwipeMove($event, log.id)"
          @touchend="onSwipeEnd(log.id)"
        >
          <div class="log-emoji">{{ log.food_emoji || '🍽️' }}</div>
          <div class="log-info">
            <div class="log-name">{{ log.food_name }}</div>
            <div class="log-meta">
              {{ log.amount }}g · {{ log.protein || 0 }}g蛋白质 · {{ formatTime(log.logged_at) }}
            </div>
          </div>
          <div class="log-cal">{{ log.calories }}<span class="log-cal-unit">kcal</span></div>
          <button class="log-delete" @click="deleteLog(log.id)">🗑️</button>
        </div>
      </div>
    </div>

    <BottomNav @add="openAddSheet()" />

    <!-- Bottom Sheet: Add Food -->
    <div v-if="showAddSheet" class="bottom-sheet-backdrop" @click="closeAddSheet"></div>
    <div v-if="showAddSheet" class="bottom-sheet">
      <div class="sheet-header">
        <span class="sheet-title">添加食物</span>
        <button class="sheet-close" @click="closeAddSheet">✕</button>
      </div>

      <!-- Step 1: Search -->
      <div v-if="!selectedFood" class="sheet-search">
        <div class="search-row">
          <input
            v-model="sheetSearchQuery"
            type="text"
            placeholder="搜索食物名称..."
            class="search-input"
            @keyup.enter="sheetSearch"
            :disabled="sheetSearching"
          />
          <button class="search-btn" @click="sheetSearch" :disabled="sheetSearching">
            {{ sheetSearching ? '...' : '🔍' }}
          </button>
        </div>

        <div class="sheet-results">
          <div
            v-for="food in sheetResults"
            :key="food.id"
            class="sheet-result-item"
            @click="selectFood(food)"
          >
            <div class="qf-emoji">{{ foodEmoji(food.category) }}</div>
            <div class="qf-info">
              <div class="qf-name">{{ food.name }}</div>
              <div class="qf-cal">{{ food.calories }} kcal/100g</div>
            </div>
            <span class="select-arrow">›</span>
          </div>
          <div v-if="sheetSearched && sheetResults.length === 0" class="empty-state">
            未找到食物，试试创建自定义食物
          </div>
        </div>

        <!-- Custom Food Form -->
        <div class="custom-section">
          <div class="custom-title" @click="showCustomForm = !showCustomForm">
            <span>+ 创建自定义食物</span>
            <span class="toggle-icon">{{ showCustomForm ? '−' : '+' }}</span>
          </div>
          <div v-if="showCustomForm" class="custom-form">
            <input v-model="customFood.name" placeholder="食物名称" class="custom-input" />
            <div class="custom-row">
              <input v-model="customFood.calories" type="number" placeholder="热量(kcal/100g)" class="custom-input" />
              <input v-model="customFood.protein" type="number" placeholder="蛋白质(g)" class="custom-input" />
            </div>
            <div class="custom-row">
              <input v-model="customFood.carbs" type="number" placeholder="碳水(g)" class="custom-input" />
              <input v-model="customFood.fat" type="number" placeholder="脂肪(g)" class="custom-input" />
            </div>
            <select v-model="customFood.category" class="custom-select">
              <option value="">选择分类</option>
              <option v-for="cat in categories.slice(1)" :key="cat.key" :value="cat.key">{{ cat.label }}</option>
            </select>
            <button class="btn-primary" @click="createCustomFood">保存自定义食物</button>
          </div>
        </div>
      </div>

      <!-- Step 2: Input grams and save -->
      <div v-else class="sheet-confirm">
        <div class="selected-food-card">
          <div class="sf-emoji">{{ foodEmoji(selectedFood.category) }}</div>
          <div class="sf-info">
            <div class="sf-name">{{ selectedFood.name }}</div>
            <div class="sf-cal">{{ selectedFood.calories }} kcal / 100g</div>
            <div class="sf-nutri">
              蛋白{{ selectedFood.protein }}g · 碳水{{ selectedFood.carbs }}g · 脂肪{{ selectedFood.fat }}g
            </div>
          </div>
        </div>

        <div class="amount-section">
          <label class="amount-label">摄入量</label>
          <div class="amount-input-row">
            <button class="amount-btn" @click="adjustAmount(-50)">−</button>
            <input
              v-model.number="foodAmount"
              type="number"
              class="amount-input"
              placeholder="100"
            />
            <span class="amount-unit">g</span>
            <button class="amount-btn" @click="adjustAmount(50)">+</button>
          </div>
          <div class="calorie-preview">
            预计摄入 ≈ {{ Math.round(calcCalories) }} kcal
          </div>
        </div>

        <div class="meal-select-section">
          <label class="amount-label">餐次</label>
          <div class="meal-pills">
            <button
              v-for="meal in meals"
              :key="meal.type"
              class="meal-pill"
              :class="{ active: selectedMealType === meal.type }"
              @click="selectedMealType = meal.type"
            >{{ meal.emoji }} {{ meal.label }}</button>
          </div>
        </div>

        <button class="btn-primary" @click="saveFoodLog" :disabled="saving">
          {{ saving ? '保存中...' : '确认添加' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import api from '../api'
import { useAuthStore } from '../stores/auth'
import BottomNav from '../components/BottomNav.vue'
import CalorieRingMini from '../components/CalorieRing.vue'

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

async function fetchDayData() {
  loading.value = true
  try {
    const [summaryRes, logsRes] = await Promise.all([
      api.get(`/food-logs/summary?date=${currentDate.value}`),
      api.get(`/food-logs?date=${currentDate.value}`),
    ])
    // Backend returns a list of per-meal summaries; transform to object
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
    // Build quick foods from recent logs
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
      alert('未找到相关食物，可尝试点击下方加号添加“自定义食物”')
    }
  } catch (e) {
    const detail = e.response?.data?.detail
    alert('搜索失败: ' + (typeof detail === 'string' ? detail : e.message))
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
      alert('未找到相关食物，可尝试点击下方“创建自定义食物”')
    }
  } catch (e) {
    const detail = e.response?.data?.detail
    alert('搜索失败: ' + (typeof detail === 'string' ? detail : e.message))
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
    alert('请填写食物名称和热量')
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
    alert('自定义食物创建成功')
    customFood.value = { name: '', calories: '', protein: '', carbs: '', fat: '', category: '' }
    showCustomForm.value = false
    // Auto search for it
    sheetSearchQuery.value = customFood.value.name
    await sheetSearch()
  } catch (e) {
    alert('创建失败')
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
    alert('添加失败，请重试')
  } finally {
    saving.value = false
  }
}

async function deleteLog(id) {
  if (!confirm('确定删除这条记录？')) return
  try {
    await api.delete(`/food-logs/${id}`)
    delete swipeOffset[id]
    await fetchDayData()
  } catch (e) {
    alert('删除失败')
  }
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

onMounted(() => {
  fetchDayData()
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
}

.date-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  background: #fff;
}

.date-arrow {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: #007aff;
  background: none;
  border: none;
}

.date-display {
  text-align: center;
}

.date-main {
  font-size: 16px;
  font-weight: 600;
  color: #1d1d1f;
}

.date-sub {
  font-size: 12px;
  color: #007aff;
  margin-left: 6px;
}

.card {
  background: #fff;
  border-radius: 16px;
  padding: 16px;
  margin: 8px 16px;
}

.summary-card {
  display: flex;
  align-items: center;
  gap: 16px;
}

.summary-ring-mini {
  flex-shrink: 0;
  width: 100px;
  height: 100px;
}

.summary-ring-mini :deep(.calorie-ring) {
  width: 100px;
  height: 100px;
}

.summary-ring-mini :deep(svg) {
  width: 100px !important;
  height: 100px !important;
}

.summary-ring-mini :deep(.consumed-value) {
  font-size: 20px;
  font-weight: 700;
  line-height: 1.1;
}

.summary-ring-mini :deep(.consumed-label) {
  font-size: 9px;
  margin-top: 1px;
}

.summary-ring-mini :deep(.goal-text) {
  display: none;
}

.summary-stats {
  flex: 1;
  display: flex;
  justify-content: space-around;
}

.ss-item {
  text-align: center;
}

.ss-value {
  font-size: 18px;
  font-weight: 700;
}

.ss-value.green { color: #34c759; }
.ss-value.orange { color: #ff9500; }
.ss-value.blue { color: #007aff; }

.ss-label {
  font-size: 11px;
  color: #86868b;
  margin-top: 2px;
}

.meal-summary-row {
  display: flex;
  gap: 8px;
  padding: 0 16px;
  margin-bottom: 8px;
}

.meal-summary-card {
  flex: 1;
  background: #fff;
  border-radius: 12px;
  padding: 10px 6px;
  text-align: center;
}

.ms-emoji {
  font-size: 18px;
}

.ms-name {
  font-size: 11px;
  color: #86868b;
  margin-top: 2px;
}

.ms-cal {
  font-size: 15px;
  font-weight: 600;
  color: #1d1d1f;
  margin-top: 2px;
}

.ms-unit {
  font-size: 10px;
  color: #aeaeb2;
}

.search-row {
  display: flex;
  gap: 8px;
  padding: 0 16px;
  margin: 8px 0;
}

.search-input {
  flex: 1;
  height: 40px;
  background: #fff;
  border-radius: 12px;
  padding: 0 14px;
  font-size: 14px;
  color: #1d1d1f;
  border: none;
  outline: none;
}

.search-input::placeholder {
  color: #aeaeb2;
}

.search-btn {
  width: 40px;
  height: 40px;
  background: #007aff;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  border: none;
  color: #fff;
}

.category-pills {
  display: flex;
  gap: 8px;
  padding: 0 16px;
  overflow-x: auto;
  margin-bottom: 4px;
}

.cat-pill {
  white-space: nowrap;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  color: #86868b;
  background: #fff;
  border: none;
  transition: all 0.2s;
}

.cat-pill.active {
  background: #007aff;
  color: #fff;
  font-weight: 600;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  margin: 16px 16px 8px;
  color: #1d1d1f;
}

.quick-foods {
  margin: 0 16px;
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
}

.quick-food-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f2;
  cursor: pointer;
}

.quick-food-item:last-child {
  border-bottom: none;
}

.qf-emoji {
  font-size: 24px;
  width: 36px;
  text-align: center;
}

.qf-info {
  flex: 1;
}

.qf-name {
  font-size: 14px;
  font-weight: 500;
  color: #1d1d1f;
}

.qf-cal {
  font-size: 12px;
  color: #86868b;
  margin-top: 2px;
}

.custom-tag {
  display: inline-block;
  font-size: 10px;
  color: #007aff;
  background: #eef4ff;
  padding: 1px 6px;
  border-radius: 6px;
  margin-left: 4px;
}

.qf-add-btn {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #007aff;
  color: #fff;
  font-size: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  line-height: 1;
}

.search-results {
  margin-top: 8px;
}

.search-results .quick-food-item {
  background: #fff;
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
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f0f2;
}

.meal-name {
  font-size: 15px;
  font-weight: 600;
  color: #1d1d1f;
}

.meal-add-btn {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #f0f0f2;
  color: #007aff;
  font-size: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
}

.empty-meal {
  font-size: 13px;
  color: #aeaeb2;
  padding: 8px 0;
  text-align: center;
}

.log-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
  background: #fff;
  transition: none;
}

.swipe-container {
  position: relative;
  overflow: hidden;
  margin-bottom: 2px;
}

.swipe-delete {
  position: absolute;
  top: 0;
  right: 0;
  width: 80px;
  height: 100%;
  background: #ff3b30;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}

.swipe-content {
  position: relative;
  background: #fff;
  transition: transform 0.3s ease;
  will-change: transform;
}

.log-emoji {
  font-size: 24px;
  width: 36px;
  text-align: center;
}

.log-info {
  flex: 1;
}

.log-name {
  font-size: 14px;
  font-weight: 500;
  color: #1d1d1f;
}

.log-meta {
  font-size: 12px;
  color: #86868b;
  margin-top: 2px;
}

.log-cal {
  font-size: 16px;
  font-weight: 600;
  color: #ff9500;
}

.log-cal-unit {
  font-size: 11px;
  color: #aeaeb2;
}

.log-delete {
  font-size: 16px;
  background: none;
  border: none;
  padding: 4px;
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
  margin-bottom: 16px;
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

.sheet-results {
  margin-top: 12px;
}

.sheet-result-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f2;
  cursor: pointer;
}

.select-arrow {
  font-size: 20px;
  color: #aeaeb2;
}

.custom-section {
  margin-top: 16px;
  border-top: 1px solid #f0f0f2;
  padding-top: 12px;
}

.custom-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  color: #007aff;
  font-weight: 500;
  cursor: pointer;
}

.toggle-icon {
  font-size: 18px;
}

.custom-form {
  margin-top: 12px;
}

.custom-input {
  width: 100%;
  height: 40px;
  background: #f5f5f7;
  border-radius: 10px;
  padding: 0 12px;
  font-size: 14px;
  color: #1d1d1f;
  border: none;
  margin-bottom: 8px;
}

.custom-row {
  display: flex;
  gap: 8px;
}

.custom-row .custom-input {
  flex: 1;
}

.custom-select {
  width: 100%;
  height: 40px;
  background: #f5f5f7;
  border-radius: 10px;
  padding: 0 12px;
  font-size: 14px;
  color: #1d1d1f;
  border: none;
  margin-bottom: 12px;
}

.sheet-confirm {
  padding-top: 4px;
}

.selected-food-card {
  display: flex;
  gap: 12px;
  background: #f5f5f7;
  border-radius: 14px;
  padding: 14px;
  margin-bottom: 16px;
}

.sf-emoji {
  font-size: 36px;
  width: 48px;
  text-align: center;
}

.sf-info {
  flex: 1;
}

.sf-name {
  font-size: 16px;
  font-weight: 600;
  color: #1d1d1f;
}

.sf-cal {
  font-size: 13px;
  color: #007aff;
  margin-top: 2px;
}

.sf-nutri {
  font-size: 12px;
  color: #86868b;
  margin-top: 4px;
}

.amount-section {
  margin-bottom: 16px;
}

.amount-label {
  font-size: 14px;
  color: #1d1d1f;
  font-weight: 500;
  display: block;
  margin-bottom: 8px;
}

.amount-input-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.amount-btn {
  width: 40px;
  height: 44px;
  border-radius: 12px;
  background: #f5f5f7;
  font-size: 22px;
  color: #007aff;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
}

.amount-input {
  flex: 1;
  height: 44px;
  background: #f5f5f7;
  border-radius: 12px;
  text-align: center;
  font-size: 18px;
  font-weight: 600;
  color: #1d1d1f;
  border: none;
  outline: none;
}

.amount-unit {
  font-size: 16px;
  color: #86868b;
}

.calorie-preview {
  text-align: center;
  font-size: 14px;
  color: #ff9500;
  font-weight: 600;
  margin-top: 10px;
}

.meal-select-section {
  margin-bottom: 20px;
}

.meal-pills {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.meal-pill {
  flex: 1;
  padding: 8px 4px;
  border-radius: 12px;
  font-size: 13px;
  color: #86868b;
  background: #f5f5f7;
  border: none;
  transition: all 0.2s;
}

.meal-pill.active {
  background: #007aff;
  color: #fff;
  font-weight: 600;
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
}

.btn-primary:active {
  opacity: 0.85;
}

.btn-primary:disabled {
  opacity: 0.5;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #aeaeb2;
  font-size: 14px;
}
</style>
