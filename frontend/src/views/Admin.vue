<template>
  <div class="page admin-page">
    <!-- Header -->
    <header class="admin-header">
      <div class="header-left">
        <h1 class="page-title">⚙️ 管理后台</h1>
        <p class="admin-user-info">您好，{{ adminUsername }}</p>
      </div>
      <div class="header-right">
        <button class="logout-btn" @click="handleLogout">🚪 退出</button>
      </div>
    </header>

    <!-- Navigation Segmented Control -->
    <div class="segmented-control">
      <button
        class="segment-btn"
        :class="{ active: activeTab === 'list' }"
        @click="activeTab = 'list'"
      >
        成员列表
      </button>
      <button
        class="segment-btn"
        :class="{ active: activeTab === 'add' }"
        @click="activeTab = 'add'"
      >
        添加成员
      </button>
    </div>

    <!-- Main Content -->
    <div class="admin-content">
      <!-- Loading indicator -->
      <div v-if="loading" class="loading-overlay">
        <div class="spinner">⏳</div>
      </div>

      <!-- Tab: List -->
      <div v-if="activeTab === 'list'" class="tab-list-view">
        <!-- Search bar -->
        <div class="search-wrapper">
          <span class="search-icon">🔍</span>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索用户名或昵称"
            class="search-input"
          />
        </div>

        <!-- Mini Stats -->
        <div class="stats-row">
          <div class="stat-mini-card">
            <span class="stat-mini-label">总人数</span>
            <span class="stat-mini-val">{{ stats.total }}</span>
          </div>
          <div class="stat-mini-card">
            <span class="stat-mini-label">管理员</span>
            <span class="stat-mini-val">{{ stats.admins }}</span>
          </div>
        </div>

        <!-- User List -->
        <div v-if="filteredUsers.length === 0" class="empty-state">
          没有找到匹配的成员
        </div>
        <div v-else class="user-list">
          <div
            v-for="u in filteredUsers"
            :key="u.id"
            class="user-item-card"
            @click="viewUserDetails(u)"
          >
            <div class="user-item-left">
              <div class="user-avatar" :class="getRandomBgClass(u.username)">
                {{ getInitial(u.nickname || u.username) }}
              </div>
              <div class="user-info-text">
                <div class="user-nickname-row">
                  <span class="user-nickname">{{ u.nickname || u.username }}</span>
                  <span class="role-badge" :class="u.role">
                    {{ u.role === 'admin' ? '管理员' : '普通用户' }}
                  </span>
                </div>
                <div class="user-sub">{{ u.username }} · {{ u.email }}</div>
              </div>
            </div>
            <div class="user-item-right">
              <span class="reg-date">{{ formatDate(u.created_at) }}</span>
              <span class="arrow-icon">chevron_right</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Tab: Add Member -->
      <div v-if="activeTab === 'add'" class="tab-add-view">
        <div class="card add-card">
          <h2 class="card-section-title">✨ 创建新成员</h2>
          <form @submit.prevent="handleAddMember" class="add-member-form">
            <div class="form-group">
              <label class="form-label">用户名</label>
              <input
                v-model="addForm.username"
                type="text"
                placeholder="6-8位小写字母/数字（首位小写字母）"
                class="form-input"
                required
              />
            </div>

            <div class="form-group">
              <label class="form-label">电子邮箱</label>
              <input
                v-model="addForm.email"
                type="email"
                placeholder="请输入邮箱地址"
                class="form-input"
                required
              />
            </div>

            <div class="form-group">
              <label class="form-label">密码</label>
              <input
                v-model="addForm.password"
                type="password"
                placeholder="至少8位，包含大写/小写/数字/特殊字符中至少两种"
                class="form-input"
                required
              />
            </div>

            <div class="form-group">
              <label class="form-label">昵称</label>
              <input
                v-model="addForm.nickname"
                type="text"
                placeholder="请输入成员昵称"
                class="form-input"
              />
            </div>

            <div class="form-group">
              <label class="form-label">成员角色</label>
              <select v-model="addForm.role" class="form-select">
                <option value="user">普通用户 (User)</option>
                <option value="admin">管理员 (Admin)</option>
              </select>
            </div>

            <hr class="form-divider" />
            <p class="form-subsection-title">身体及目标指标（可选）</p>

            <div class="form-row">
              <div class="form-group half-width">
                <label class="form-label">性别</label>
                <select v-model="addForm.gender" class="form-select">
                  <option :value="null">未指定</option>
                  <option :value="1">男</option>
                  <option :value="0">女</option>
                </select>
              </div>
              <div class="form-group half-width">
                <label class="form-label">年龄</label>
                <input
                  v-model.number="addForm.age"
                  type="number"
                  placeholder="岁"
                  class="form-input"
                  min="1"
                />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group half-width">
                <label class="form-label">身高 (cm)</label>
                <input
                  v-model.number="addForm.height"
                  type="number"
                  step="0.1"
                  placeholder="厘米"
                  class="form-input"
                  min="30"
                />
              </div>
              <div class="form-group half-width">
                <label class="form-label">目标体重 (kg)</label>
                <input
                  v-model.number="addForm.target_weight"
                  type="number"
                  step="0.1"
                  placeholder="公斤"
                  class="form-input"
                  min="10"
                />
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">每日卡路里目标 (kcal)</label>
              <input
                v-model.number="addForm.daily_calorie_goal"
                type="number"
                placeholder="千卡"
                class="form-input"
                min="500"
              />
            </div>

            <p v-if="successMsg" class="success-msg">{{ successMsg }}</p>
            <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>

            <button type="submit" class="btn-primary form-submit-btn" :disabled="submitting">
              {{ submitting ? '创建中...' : '创 建 成 员' }}
            </button>
          </form>
        </div>
      </div>
    </div>

    <!-- Sliding User Details Bottom Sheet / Overlay -->
    <div v-if="selectedUser" class="detail-backdrop" @click="selectedUser = null">
      <div class="detail-sheet" @click.stop>
        <!-- Sheet Header -->
        <header class="sheet-header">
          <div class="sh-left">
            <span class="sh-avatar" :class="getRandomBgClass(selectedUser.username)">
              {{ getInitial(selectedUser.nickname || selectedUser.username) }}
            </span>
            <div class="sh-meta">
              <h3 class="sh-title">{{ selectedUser.nickname || selectedUser.username }}</h3>
              <p class="sh-sub">@{{ selectedUser.username }} · {{ selectedUser.role === 'admin' ? '管理员' : '普通用户' }}</p>
            </div>
          </div>
          <button class="sheet-close" @click="selectedUser = null">✕</button>
        </header>

        <!-- Sheet Scrollable Content -->
        <div class="sheet-body">
          <div v-if="detailsLoading" class="sheet-loading">
            <span>加载数据中...</span>
          </div>
          <div v-else-if="detailsData">
            <!-- Calorie Ring & Daily Stats Section -->
            <div class="details-section">
              <h4 class="section-title-mini">今日饮食汇总</h4>
              <div class="details-calorie-row">
                <div class="ring-container">
                  <CalorieRing
                    :consumed="detailsData.calorie_summary?.consumed || 0"
                    :goal="detailsData.calorie_summary?.goal || 2000"
                    :size="130"
                  />
                </div>
                <div class="calorie-legend-list">
                  <div class="legend-item text-green">
                    <span class="leg-label">剩余可吃</span>
                    <span class="leg-val">{{ detailsData.calorie_summary?.remaining }} <small>kcal</small></span>
                  </div>
                  <div class="legend-item text-orange">
                    <span class="leg-label">今日已摄入</span>
                    <span class="leg-val">{{ detailsData.calorie_summary?.consumed }} <small>kcal</small></span>
                  </div>
                </div>
              </div>

              <!-- Nutrition progress -->
              <div class="nutri-bars-card">
                <div class="nutri-bar-item">
                  <div class="nbi-head">
                    <span>🥩 蛋白质</span>
                    <span>{{ detailsData.nutrition_breakdown?.protein?.current }}g / {{ detailsData.nutrition_breakdown?.protein?.target }}g</span>
                  </div>
                  <div class="nbi-progress-bg">
                    <div class="nbi-progress-fill p-bar" :style="{ width: getPercentageWidth(detailsData.nutrition_breakdown?.protein?.current, detailsData.nutrition_breakdown?.protein?.target) }"></div>
                  </div>
                </div>
                <div class="nutri-bar-item">
                  <div class="nbi-head">
                    <span>🍞 碳水化合物</span>
                    <span>{{ detailsData.nutrition_breakdown?.carbs?.current }}g / {{ detailsData.nutrition_breakdown?.carbs?.target }}g</span>
                  </div>
                  <div class="nbi-progress-bg">
                    <div class="nbi-progress-fill c-bar" :style="{ width: getPercentageWidth(detailsData.nutrition_breakdown?.carbs?.current, detailsData.nutrition_breakdown?.carbs?.target) }"></div>
                  </div>
                </div>
                <div class="nutri-bar-item">
                  <div class="nbi-head">
                    <span>🥑 脂肪</span>
                    <span>{{ detailsData.nutrition_breakdown?.fat?.current }}g / {{ detailsData.nutrition_breakdown?.fat?.target }}g</span>
                  </div>
                  <div class="nbi-progress-bg">
                    <div class="nbi-progress-fill f-bar" :style="{ width: getPercentageWidth(detailsData.nutrition_breakdown?.fat?.current, detailsData.nutrition_breakdown?.fat?.target) }"></div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Current Weight Card -->
            <div class="details-section">
              <h4 class="section-title-mini">当前体重目标</h4>
              <div class="weight-mini-card">
                <div class="wmc-row">
                  <div class="wmc-col">
                    <span class="wmc-lbl">最新体重</span>
                    <span class="wmc-val">{{ detailsData.weight?.latest ? detailsData.weight.latest + ' kg' : '未记录' }}</span>
                  </div>
                  <div class="wmc-col text-right">
                    <span class="wmc-lbl">目标体重</span>
                    <span class="wmc-val">{{ detailsData.weight?.target_weight ? detailsData.weight.target_weight + ' kg' : '-' }}</span>
                  </div>
                </div>
                <!-- Progress to target -->
                <div class="target-progress-w" v-if="detailsData.weight?.latest && detailsData.weight?.target_weight">
                  <div class="tpw-bar-bg">
                    <div class="tpw-bar-fill" :style="{ width: weightTargetProgress + '%' }"></div>
                  </div>
                  <div class="tpw-lbl">距目标进度 {{ Math.round(weightTargetProgress) }}%</div>
                </div>
              </div>
            </div>

            <!-- Today's Meal list -->
            <div class="details-section">
              <h4 class="section-title-mini">今日饮食明细</h4>
              <div class="meals-list">
                <div v-for="m in displayMeals" :key="m.name" class="detail-meal-group">
                  <div class="dmg-head">
                    <span class="dmg-name">{{ m.label }}</span>
                    <span class="dmg-cal">{{ getMealCalories(m.name) }} kcal</span>
                  </div>
                  <div v-if="getMealFoods(m.name).length === 0" class="dmg-empty">
                    暂无记录
                  </div>
                  <div v-for="f in getMealFoods(m.name)" :key="f.id" class="dmg-food-item">
                    <div class="dmg-food-name-col">
                      <span class="dfn">{{ f.food_name }}</span>
                      <span class="dfm">{{ f.amount }}g · 蛋 {{ f.protein || 0 }}g · 碳 {{ f.carbs || 0 }}g · 脂 {{ f.fat || 0 }}g</span>
                    </div>
                    <div class="dmg-food-cal">{{ f.calories }} kcal</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Active PK Battle -->
            <div class="details-section">
              <h4 class="section-title-mini">进行中的 PK 挑战</h4>
              <div v-if="detailsData.pk" class="pk-detail-box">
                <div class="pkdb-title">🏆 {{ detailsData.pk.name }}</div>
                <div class="pkdb-players">
                  <div class="pkdb-player">
                    <span class="pkdb-name">{{ detailsData.pk.user_a?.name }}</span>
                    <span class="pkdb-sc">{{ detailsData.pk.user_a?.score }} 分</span>
                  </div>
                  <span class="pkdb-vs">VS</span>
                  <div class="pkdb-player">
                    <span class="pkdb-name">{{ detailsData.pk.user_b?.name }}</span>
                    <span class="pkdb-sc">{{ detailsData.pk.user_b?.score }} 分</span>
                  </div>
                </div>
              </div>
              <div v-else class="dmg-empty bg-card">
                暂无进行中的减脂 PK
              </div>
            </div>

            <!-- Historical Weight Logs Table -->
            <div class="details-section">
              <h4 class="section-title-mini">历史体重记录 (最近30次)</h4>
              <div v-if="!detailsData.weight_history || detailsData.weight_history.length === 0" class="dmg-empty bg-card">
                暂无历史体重记录
              </div>
              <div v-else class="history-table-container">
                <table class="history-table">
                  <thead>
                    <tr>
                      <th>记录时间</th>
                      <th>体重</th>
                      <th>体脂率</th>
                      <th>肌肉量</th>
                      <th>备注</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="log in detailsData.weight_history" :key="log.id">
                      <td>{{ formatFullDate(log.logged_at) }}</td>
                      <td class="font-bold">{{ log.weight }} kg</td>
                      <td>{{ log.body_fat ? log.body_fat + '%' : '-' }}</td>
                      <td>{{ log.muscle ? log.muscle + ' kg' : '-' }}</td>
                      <td class="history-note">{{ log.note || '-' }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'
import { useAuthStore } from '../stores/auth'
import CalorieRing from '../components/CalorieRing.vue'

const router = useRouter()
const authStore = useAuthStore()

// State
const activeTab = ref('list')
const loading = ref(false)
const users = ref([])
const searchQuery = ref('')

const adminUsername = computed(() => authStore.user?.nickname || authStore.user?.username || '管理员')

// Load list of users
async function fetchUsers() {
  loading.value = true
  try {
    const res = await api.get('/admin/users')
    users.value = res.data
  } catch (e) {
    console.error('Failed to fetch users', e)
  } finally {
    loading.value = false
  }
}

// Compute simple statistics
const stats = computed(() => {
  const list = users.value
  return {
    total: list.length,
    admins: list.filter(u => u.role === 'admin').length,
    users: list.filter(u => u.role === 'user').length,
  }
})

// Filtered user list based on search query
const filteredUsers = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()
  if (!query) return users.value
  return users.value.filter(u => {
    const name = (u.nickname || '').toLowerCase()
    const username = (u.username || '').toLowerCase()
    return name.includes(query) || username.includes(query)
  })
})

// Form for adding member
const addForm = reactive({
  username: '',
  email: '',
  password: '',
  nickname: '',
  role: 'user',
  gender: null,
  age: null,
  height: null,
  target_weight: null,
  daily_calorie_goal: null,
})
const successMsg = ref('')
const errorMsg = ref('')
const submitting = ref(false)

async function handleAddMember() {
  submitting.value = true
  successMsg.value = ''
  errorMsg.value = ''
  try {
    await api.post('/admin/users', { ...addForm })
    successMsg.value = `成员 @${addForm.username} 创建成功！`
    // Reset form fields
    addForm.username = ''
    addForm.email = ''
    addForm.password = ''
    addForm.nickname = ''
    addForm.role = 'user'
    addForm.gender = null
    addForm.age = null
    addForm.height = null
    addForm.target_weight = null
    addForm.daily_calorie_goal = null
    // Refresh users list
    await fetchUsers()
  } catch (e) {
    const detail = e.response?.data?.detail
    if (typeof detail === 'string') {
      errorMsg.value = detail
    } else if (Array.isArray(detail)) {
      errorMsg.value = detail.map(d => d.msg || JSON.stringify(d)).join('; ')
    } else {
      errorMsg.value = '创建成员失败，请检查填写内容'
    }
  } finally {
    submitting.value = false
  }
}

// Detail overlay sheet state
const selectedUser = ref(null)
const detailsLoading = ref(false)
const detailsData = ref(null)

async function viewUserDetails(user) {
  selectedUser.value = user
  detailsLoading.value = true
  detailsData.value = null
  try {
    const res = await api.get(`/admin/users/${user.id}/dashboard`)
    detailsData.value = res.data
  } catch (e) {
    console.error('Failed to load user details', e)
  } finally {
    detailsLoading.value = false
  }
}

// Weight progress computing in sheet
const weightTargetProgress = computed(() => {
  const w = detailsData.value?.weight || {}
  const current = w.latest || 0
  const target = w.target_weight || 0
  if (current <= 0 || target <= 0) return 0
  if (current <= target) return 100
  const start = target + 5 // rough reference start
  const total = start - target
  const done = start - current
  return Math.max(0, Math.min(100, (done / total) * 100))
})

const displayMeals = [
  { name: 'breakfast', label: '🍳 早餐' },
  { name: 'lunch', label: '🥗 午餐' },
  { name: 'dinner', label: '🍲 晚餐' },
  { name: 'snack', label: '🍪 加餐' },
]

function getMealFoods(mealName) {
  return detailsData.value?.meals?.[mealName] || []
}

function getMealCalories(mealName) {
  return getMealFoods(mealName).reduce((sum, f) => sum + (f.calories || 0), 0)
}

function getPercentageWidth(current, target) {
  if (!target || target <= 0) return '0%'
  return Math.min((current / target) * 100, 100) + '%'
}

// Logout
function handleLogout() {
  authStore.logout()
}

// UI Helpers
function getInitial(name) {
  return name ? name.charAt(0).toUpperCase() : 'U'
}

function getRandomBgClass(username) {
  const charCode = (username || 'a').charCodeAt(0)
  const code = charCode % 4
  return `bg-gradient-${code}`
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

function formatFullDate(dateStr) {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}月${d.getDate()}日 ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

onMounted(async () => {
  await fetchUsers()
})
</script>

<style scoped>
.admin-page {
  background: var(--bg-color);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.admin-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: #fff;
  border-bottom: 1px solid var(--border-color);
}

.admin-user-info {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 2px;
}

.logout-btn {
  font-size: 13px;
  font-weight: 600;
  color: #ff3b30;
  padding: 6px 12px;
  background: #fff0f0;
  border-radius: 8px;
  transition: opacity 0.2s;
}

.logout-btn:active {
  opacity: 0.8;
}

/* Segmented Control */
.segmented-control {
  display: flex;
  background: #e5e5ea;
  padding: 2px;
  border-radius: 10px;
  margin: 16px;
}

.segment-btn {
  flex: 1;
  text-align: center;
  padding: 8px 0;
  font-size: 14px;
  font-weight: 600;
  border-radius: 8px;
  color: var(--text-secondary);
  transition: all 0.2s;
  cursor: pointer;
}

.segment-btn.active {
  background: #fff;
  color: #007aff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

/* Admin Content Layout */
.admin-content {
  flex: 1;
  padding: 0 16px 40px;
  overflow-y: auto;
  position: relative;
}

/* Search bar */
.search-wrapper {
  display: flex;
  align-items: center;
  background: #fff;
  border-radius: 12px;
  padding: 0 12px;
  margin-bottom: 12px;
  height: 44px;
  border: 1px solid var(--border-color);
}

.search-icon {
  margin-right: 8px;
  font-size: 16px;
  opacity: 0.6;
}

.search-input {
  flex: 1;
  font-size: 14px;
  color: var(--text-primary);
}

/* Stats mini row */
.stats-row {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.stat-mini-card {
  flex: 1;
  background: #fff;
  border-radius: 12px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.01);
  border: 1px solid #f0f0f2;
}

.stat-mini-label {
  font-size: 11px;
  color: var(--text-secondary);
  margin-bottom: 2px;
}

.stat-mini-val {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
}

/* User Card Items */
.user-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.user-item-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-radius: 14px;
  padding: 12px 14px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.01);
  border: 1.5px solid #f0f0f2;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.user-item-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.03);
}

.user-item-card:active {
  transform: scale(0.98);
}

.user-item-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 700;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}

.user-info-text {
  display: flex;
  flex-direction: column;
}

.user-nickname-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-nickname {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.role-badge {
  font-size: 9px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 6px;
  color: #fff;
  line-height: 1;
}

.role-badge.admin {
  background: linear-gradient(135deg, #ff3b30, #ff9500);
}

.role-badge.user {
  background: linear-gradient(135deg, #007aff, #5ac8fa);
}

.user-sub {
  font-size: 11px;
  color: var(--text-secondary);
  margin-top: 3px;
}

.user-item-right {
  display: flex;
  align-items: center;
  gap: 4px;
}

.reg-date {
  font-size: 11px;
  color: var(--text-tertiary);
}

.arrow-icon {
  font-family: monospace;
  font-size: 12px;
  color: var(--text-tertiary);
}

/* Gradients for Avatars */
.bg-gradient-0 { background: linear-gradient(135deg, #007aff, #5ac8fa); }
.bg-gradient-1 { background: linear-gradient(135deg, #ff9500, #ffcc00); }
.bg-gradient-2 { background: linear-gradient(135deg, #34c759, #5ac8fa); }
.bg-gradient-3 { background: linear-gradient(135deg, #af52de, #ff2d55); }

/* Add Member Form styling */
.add-card {
  padding: 20px 16px;
}

.card-section-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 20px;
  text-align: center;
}

.add-member-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.form-input, .form-select {
  height: 44px;
  background: #f5f5f7;
  border-radius: 10px;
  padding: 0 12px;
  font-size: 14px;
  color: var(--text-primary);
  border: 1px solid transparent;
  transition: all 0.2s;
}

.form-input:focus, .form-select:focus {
  border-color: #007aff;
  background: #fff;
  box-shadow: 0 0 0 2px rgba(0, 122, 255, 0.15);
}

.form-row {
  display: flex;
  gap: 12px;
}

.half-width {
  flex: 1;
}

.form-divider {
  border: 0;
  height: 1px;
  background: var(--border-color);
  margin: 10px 0;
}

.form-subsection-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.form-submit-btn {
  margin-top: 10px;
  box-shadow: 0 4px 14px rgba(0, 122, 255, 0.25);
}

.success-msg {
  color: var(--green);
  font-size: 13px;
  text-align: center;
  font-weight: 500;
}

.error-msg {
  color: var(--red);
  font-size: 13px;
  text-align: center;
  font-weight: 500;
}

/* Detail Modal Sheet Backdrop */
.detail-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
  z-index: 1000;
  display: flex;
  justify-content: center;
  align-items: flex-end;
}

.detail-sheet {
  width: 100%;
  max-width: 375px;
  height: 85vh;
  background: var(--bg-color);
  border-radius: 20px 20px 0 0;
  display: flex;
  flex-direction: column;
  box-shadow: 0 -10px 30px rgba(0, 0, 0, 0.15);
  animation: slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  overflow: hidden;
}

@keyframes slideUp {
  from { transform: translateY(100%); }
  to { transform: translateY(0); }
}

.sheet-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: #fff;
  border-bottom: 1px solid var(--border-color);
}

.sh-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.sh-avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 700;
}

.sh-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
}

.sh-sub {
  font-size: 11px;
  color: var(--text-secondary);
}

.sheet-close {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #e5e5ea;
  color: #86868b;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
}

.sheet-close:active {
  background: #d1d1d6;
}

.sheet-body {
  flex: 1;
  overflow-y: auto;
  padding-bottom: 40px;
}

.sheet-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: var(--text-secondary);
  font-size: 14px;
}

/* Detail Inner Layout */
.details-section {
  display: flex;
  flex-direction: column;
  margin-top: 14px;
}

.section-title-mini {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  margin: 6px 16px 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.details-calorie-row {
  display: flex;
  align-items: center;
  background: #fff;
  margin: 0 16px 10px;
  padding: 16px;
  border-radius: 16px;
  gap: 16px;
}

.ring-container {
  flex-shrink: 0;
}

.calorie-legend-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex: 1;
}

.legend-item {
  display: flex;
  flex-direction: column;
}

.leg-label {
  font-size: 11px;
  color: var(--text-secondary);
}

.leg-val {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

.leg-val small {
  font-size: 11px;
  font-weight: 500;
  color: var(--text-secondary);
}

.text-green .leg-val { color: var(--green); }
.text-orange .leg-val { color: var(--orange); }

.nutri-bars-card {
  background: #fff;
  margin: 0 16px;
  border-radius: 16px;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.nutri-bar-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nbi-head {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-primary);
}

.nbi-progress-bg {
  height: 6px;
  background: #f0f0f2;
  border-radius: 3px;
  overflow: hidden;
}

.nbi-progress-fill {
  height: 100%;
  border-radius: 3px;
}

.p-bar { background: linear-gradient(90deg, #ff6b6b, #ff9500); }
.c-bar { background: linear-gradient(90deg, #ffcc00, #ffd60a); }
.f-bar { background: linear-gradient(90deg, #5ac8fa, #007aff); }

/* Weight Mini Card */
.weight-mini-card {
  background: linear-gradient(135deg, #007aff, #5ac8fa);
  color: #fff;
  border-radius: 16px;
  margin: 0 16px;
  padding: 16px;
}

.wmc-row {
  display: flex;
  justify-content: space-between;
}

.wmc-col {
  display: flex;
  flex-direction: column;
}

.text-right {
  text-align: right;
}

.wmc-lbl {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.75);
}

.wmc-val {
  font-size: 20px;
  font-weight: 700;
}

.target-progress-w {
  margin-top: 14px;
}

.tpw-bar-bg {
  height: 5px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 3px;
  overflow: hidden;
}

.tpw-bar-fill {
  height: 100%;
  background: #fff;
  border-radius: 3px;
}

.tpw-lbl {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.85);
  margin-top: 4px;
  text-align: right;
}

/* Meals detail in sheet */
.meals-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin: 0 16px;
}

.detail-meal-group {
  background: #fff;
  border-radius: 16px;
  padding: 12px 14px;
}

.dmg-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #f0f0f2;
  padding-bottom: 6px;
  margin-bottom: 8px;
}

.dmg-name {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-primary);
}

.dmg-cal {
  font-size: 12px;
  font-weight: 600;
  color: var(--primary);
}

.dmg-empty {
  font-size: 12px;
  color: var(--text-tertiary);
  text-align: center;
  padding: 8px 0;
}

.dmg-empty.bg-card {
  background: #fff;
  margin: 0 16px;
  border-radius: 16px;
  padding: 16px;
}

.dmg-food-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
}

.dmg-food-name-col {
  display: flex;
  flex-direction: column;
}

.dfn {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}

.dfm {
  font-size: 10px;
  color: var(--text-secondary);
  margin-top: 1px;
}

.dmg-food-cal {
  font-size: 13px;
  font-weight: 600;
  color: var(--orange);
}

/* PK mini box */
.pk-detail-box {
  background: #fff;
  margin: 0 16px;
  border-radius: 16px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.pkdb-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary);
}

.pkdb-players {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 4px;
}

.pkdb-player {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.pkdb-player:last-child {
  text-align: right;
}

.pkdb-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.pkdb-sc {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 1px;
}

.pkdb-vs {
  font-size: 12px;
  font-weight: 700;
  color: var(--text-tertiary);
  padding: 0 12px;
}

/* Historical Weight Logs Table */
.history-table-container {
  background: #fff;
  margin: 0 16px;
  border-radius: 16px;
  overflow-x: auto;
  border: 1px solid #f0f0f2;
}

.history-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 11px;
  text-align: left;
}

.history-table th {
  background: #f8f8fa;
  color: var(--text-secondary);
  font-weight: 600;
  padding: 8px 10px;
  border-bottom: 1px solid #e5e5ea;
}

.history-table td {
  padding: 10px;
  border-bottom: 1px solid #f0f0f2;
  color: var(--text-primary);
  white-space: nowrap;
}

.history-table tr:last-child td {
  border-bottom: 0;
}

.font-bold {
  font-weight: 700;
}

.history-note {
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--text-secondary);
}
</style>
