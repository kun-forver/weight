<template>
  <div class="page">
    <!-- Blue Gradient Header -->
    <div class="profile-header">
      <div class="header-top">
        <div class="avatar-large" @click="triggerAvatarUpload">
          <img v-if="user.avatar" :src="user.avatar" class="avatar-img" alt="头像" />
          <span v-else>{{ userInitial }}</span>
          <span class="avatar-edit-hint">📷</span>
        </div>
        <input type="file" ref="avatarInput" accept="image/jpeg,image/png,image/gif,image/webp" style="display:none" @change="handleAvatarUpload" />
        <div class="user-info">
          <div class="user-name">{{ userNickname }}</div>
          <div class="user-tags">
            <span class="tag" v-if="user.gender">{{ genderText }}</span>
            <span class="tag" v-if="user.height">{{ user.height }}cm</span>
            <span class="tag" v-if="user.age">{{ user.age }}岁</span>
          </div>
        </div>
        <button class="edit-btn" @click="openEditSheet">编辑</button>
      </div>

      <!-- 4 Stat Mini Cards -->
      <div class="mini-stats">
        <div class="mini-stat">
          <div class="ms-value">{{ latestWeight?.weight || '-' }}<span class="ms-unit">kg</span></div>
          <div class="ms-label">当前体重</div>
        </div>
        <div class="mini-stat">
          <div class="ms-value">{{ user.target_weight || '-' }}<span class="ms-unit">kg</span></div>
          <div class="ms-label">目标</div>
        </div>
        <div class="mini-stat">
          <div class="ms-value">{{ monthlyLoss }}<span class="ms-unit">kg</span></div>
          <div class="ms-label">本月减重</div>
        </div>
        <div class="mini-stat">
          <div class="ms-value">{{ streakDays }}</div>
          <div class="ms-label">连续打卡</div>
        </div>
      </div>
    </div>

    <!-- Body Data Section -->
    <div class="section-title">身体数据</div>
    <div class="card body-data-card">
      <div class="bd-item" @click="openEditSheet">
        <span class="bd-label">身高</span>
        <span class="bd-value">{{ user.height || '-' }}<span class="bd-unit">cm</span></span>
      </div>
      <div class="bd-item">
        <span class="bd-label">体重</span>
        <span class="bd-value">{{ latestWeight?.weight || '-' }}<span class="bd-unit">kg</span></span>
      </div>
      <div class="bd-item">
        <span class="bd-label">体脂率</span>
        <span class="bd-value">{{ bodyFat }}<span class="bd-unit" v-if="bodyFat !== '-'">%</span></span>
      </div>
      <div class="bd-item">
        <span class="bd-label">肌肉量</span>
        <span class="bd-value">{{ muscleMass }}<span class="bd-unit" v-if="muscleMass !== '-'">kg</span></span>
      </div>
      <div class="bd-item">
        <span class="bd-label">BMI</span>
        <span class="bd-value" :class="bmiClass">{{ bmi }}</span>
      </div>
    </div>

    <!-- Goals Section -->
    <div class="section-title">目标设置</div>
    <div class="card goals-card">
      <div class="goal-row">
        <div class="goal-info">
          <div class="goal-label">目标体重</div>
          <div class="goal-value">{{ user.target_weight || '未设置' }}<span v-if="user.target_weight">kg</span></div>
        </div>
        <button class="goal-edit-btn" @click="openEditSheet">修改</button>
      </div>
      <div class="goal-progress-section">
        <div class="goal-progress-bar">
          <div class="goal-progress-fill" :style="{ width: goalProgressPct + '%' }"></div>
        </div>
        <div class="goal-progress-text">
          已完成 {{ Math.round(goalProgressPct) }}%
          <span class="goal-remain" v-if="remainingWeight > 0">
            · 还需减重 {{ remainingWeight.toFixed(1) }}kg
          </span>
        </div>
      </div>
      <div class="goal-row">
        <div class="goal-info">
          <div class="goal-label">每日热量目标</div>
          <div class="goal-value">{{ user.daily_calorie_goal || 2000 }}<span>kcal</span></div>
        </div>
        <button class="goal-edit-btn" @click="openEditSheet">修改</button>
      </div>
    </div>

    <!-- Friends Section -->
    <div class="section-title-row">
      <span class="section-title">好友列表</span>
      <button class="add-friend-btn" @click="openFriendSheet">+ 添加好友</button>
    </div>
    <div class="card friends-card">
      <div v-for="friend in friends" :key="friend.id" class="friend-item">
        <div class="friend-avatar">{{ getInitial(friend.friend_name) }}</div>
        <div class="friend-info">
          <div class="friend-name">{{ friend.friend_name }}</div>
          <div class="friend-status" :class="friendStatusClass(friend.status)">{{ friendStatusText(friend.status) }}</div>
        </div>
        <button
          v-if="friend.status === 'pending'"
          class="friend-action-btn accept"
          @click="acceptFriend(friend.id)"
        >接受</button>
        <router-link
          v-else-if="friend.status === 'accepted'"
          to="/pk"
          class="friend-action-btn battle"
        >对战</router-link>
      </div>
      <div v-if="friends.length === 0" class="empty-state">还没有好友，快去添加吧</div>
    </div>

    <!-- Settings -->
    <div class="section-title">设置</div>
    <div class="card settings-card">
      <div class="setting-item">
        <span class="setting-label">🔔 推送通知</span>
        <label class="switch">
          <input type="checkbox" v-model="settings.notifications" />
          <span class="slider"></span>
        </label>
      </div>
      <div class="setting-item">
        <span class="setting-label">🌙 深色模式</span>
        <label class="switch">
          <input type="checkbox" v-model="settings.darkMode" />
          <span class="slider"></span>
        </label>
      </div>
      <div class="setting-item clickable" @click="exportData">
        <span class="setting-label">📤 导出数据</span>
        <span class="setting-arrow">›</span>
      </div>
      <div class="setting-item logout" @click="handleLogout">
        <span class="setting-label">🚪 退出登录</span>
      </div>
    </div>

    <div class="app-info">
      <div class="app-version">减脂PK v1.0.0</div>
    </div>

    <BottomNav />

    <!-- Bottom Sheet: Edit Profile -->
    <div v-if="showEditSheet" class="bottom-sheet-backdrop" @click="closeEditSheet"></div>
    <div v-if="showEditSheet" class="bottom-sheet">
      <div class="sheet-header">
        <span class="sheet-title">编辑资料</span>
        <button class="sheet-close" @click="closeEditSheet">✕</button>
      </div>
      <div class="edit-form">
        <div class="form-group">
          <label class="form-label">昵称</label>
          <input v-model="editForm.nickname" placeholder="请输入昵称" class="form-input" />
        </div>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">性别</label>
            <select v-model.number="editForm.gender" class="form-input">
              <option :value="null">未设置</option>
              <option :value="1">男</option>
              <option :value="0">女</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">年龄</label>
            <input v-model.number="editForm.age" type="number" placeholder="如 25" class="form-input" />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">身高(cm)</label>
            <input v-model.number="editForm.height" type="number" placeholder="如 170" class="form-input" />
          </div>
          <div class="form-group">
            <label class="form-label">体重(kg)</label>
            <input v-model.number="editForm.weight" type="number" step="0.1" placeholder="如 70.0" class="form-input" />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">目标体重(kg)</label>
            <input v-model.number="editForm.target_weight" type="number" step="0.1" placeholder="如 60.0" class="form-input" />
          </div>
          <div class="form-group">
            <label class="form-label">每日热量(kcal)</label>
            <input v-model.number="editForm.daily_calorie_goal" type="number" placeholder="如 1800" class="form-input" />
          </div>
        </div>
        <button class="btn-primary" @click="saveProfile" :disabled="saving">
          {{ saving ? '保存中...' : '保存' }}
        </button>
      </div>
    </div>

    <!-- Bottom Sheet: Add Friend -->
    <div v-if="showFriendSheet" class="bottom-sheet-backdrop" @click="closeFriendSheet"></div>
    <div v-if="showFriendSheet" class="bottom-sheet">
      <div class="sheet-header">
        <span class="sheet-title">添加好友</span>
        <button class="sheet-close" @click="closeFriendSheet">✕</button>
      </div>
      <div class="friend-search-section">
        <div class="friend-search-row">
          <input
            v-model="friendSearchQuery"
            placeholder="输入用户名搜索..."
            class="form-input"
            @keyup.enter="searchUsers"
          />
          <button class="search-btn" @click="searchUsers">🔍</button>
        </div>
        <div class="search-results-list">
          <div
            v-for="u in searchUsersResults"
            :key="u.id"
            class="search-user-item"
          >
            <div class="search-user-avatar">{{ getInitial(u.nickname || u.username) }}</div>
            <div class="search-user-info">
              <div class="search-user-name">{{ u.nickname || u.username }}</div>
              <div class="search-user-username">@{{ u.username }}</div>
            </div>
            <button class="add-btn" @click="sendFriendRequest(u.username)">+ 添加</button>
          </div>
          <div v-if="friendSearched && searchUsersResults.length === 0" class="empty-state">
            未找到用户
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'
import { useAuthStore } from '../stores/auth'
import BottomNav from '../components/BottomNav.vue'

const router = useRouter()
const authStore = useAuthStore()

const user = computed(() => authStore.user || {})
const latestWeight = ref(null)
const friends = ref([])
const saving = ref(false)
const showEditSheet = ref(false)
const showFriendSheet = ref(false)
const friendSearchQuery = ref('')
const searchUsersResults = ref([])
const friendSearched = ref(false)
const avatarInput = ref(null)

const settings = reactive({
  notifications: true,
  darkMode: false,
})

const editForm = ref({
  nickname: '',
  gender: null,
  height: '',
  age: '',
  weight: '',
  target_weight: '',
  daily_calorie_goal: '',
})

const userNickname = computed(() => user.value?.nickname || user.value?.username || '用户')
const userInitial = computed(() => {
  const name = user.value?.nickname || user.value?.username || 'U'
  return name.charAt(0).toUpperCase()
})

const genderText = computed(() => {
  if (user.value?.gender === 1) return '男'
  if (user.value?.gender === 0) return '女'
  return ''
})

const monthlyLoss = computed(() => {
  // This would come from the weight data; using a placeholder for now
  return '0.0'
})

const streakDays = computed(() => {
  // Placeholder - could calculate from food logs or weight logs
  return 0
})

const bmi = computed(() => {
  const weight = latestWeight.value?.weight
  const height = user.value?.height
  if (weight && height) {
    return (weight / Math.pow(height / 100, 2)).toFixed(1)
  }
  return '-'
})

const bmiClass = computed(() => {
  const v = parseFloat(bmi.value)
  if (isNaN(v)) return ''
  if (v < 18.5) return 'bmi-low'
  if (v < 24) return 'bmi-normal'
  if (v < 28) return 'bmi-high'
  return 'bmi-very-high'
})

const bodyFat = computed(() => {
  const weight = latestWeight.value?.weight
  const height = user.value?.height
  const age = user.value?.age
  const gender = user.value?.gender
  if (weight && height && age && gender !== null && gender !== undefined) {
    const bmiVal = weight / Math.pow(height / 100, 2)
    // BMI-based body fat estimation: 1.2*BMI + 0.23*age - 10.8*gender - 5.4
    const bf = 1.2 * bmiVal + 0.23 * age - 10.8 * gender - 5.4
    return Math.max(0, bf).toFixed(1)
  }
  return '-'
})

const muscleMass = computed(() => {
  const weight = latestWeight.value?.weight
  const bf = parseFloat(bodyFat.value)
  if (weight && !isNaN(bf)) {
    // Lean body mass = weight * (1 - bodyfat%)
    return (weight * (1 - bf / 100)).toFixed(1)
  }
  return '-'
})

const goalProgressPct = computed(() => {
  const target = user.value?.target_weight
  const current = latestWeight.value?.weight
  if (!target || !current) return 0
  const startWeight = current + 5 // assume started 5kg heavier
  const total = startWeight - target
  if (total <= 0) return 100
  const done = startWeight - current
  return Math.max(0, Math.min(100, (done / total) * 100))
})

const remainingWeight = computed(() => {
  const target = user.value?.target_weight
  const current = latestWeight.value?.weight
  if (!target || !current) return 0
  return Math.max(0, current - target)
})

function getInitial(name) {
  if (!name) return '?'
  return name.charAt(0).toUpperCase()
}

function triggerAvatarUpload() {
  avatarInput.value?.click()
}

async function handleAvatarUpload(e) {
  const file = e.target.files?.[0]
  if (!file) return
  if (file.size > 10 * 1024 * 1024) {
    alert('图片大小不能超过 10MB')
    return
  }
  const formData = new FormData()
  formData.append('file', file)
  try {
    const res = await api.post('/auth/avatar', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    authStore.user = res.data
    localStorage.setItem('user', JSON.stringify(res.data))
  } catch (e) {
    alert('头像上传失败')
  } finally {
    avatarInput.value.value = ''
  }
}

function friendStatusClass(status) {
  const map = { accepted: 'status-accepted', pending: 'status-pending' }
  return map[status] || 'status-pending'
}

function friendStatusText(status) {
  const map = { accepted: '已添加', pending: '待确认' }
  return map[status] || status
}

function openEditSheet() {
  editForm.value = {
    nickname: user.value?.nickname || '',
    gender: user.value?.gender ?? null,
    height: user.value?.height || '',
    age: user.value?.age || '',
    weight: latestWeight.value?.weight || '',
    target_weight: user.value?.target_weight || '',
    daily_calorie_goal: user.value?.daily_calorie_goal || '',
  }
  showEditSheet.value = true
}

function closeEditSheet() {
  showEditSheet.value = false
}

async function saveProfile() {
  saving.value = true
  try {
    const data = {}
    if (editForm.value.nickname) data.nickname = editForm.value.nickname
    if (editForm.value.gender !== null) data.gender = editForm.value.gender
    if (editForm.value.height) data.height = Number(editForm.value.height)
    if (editForm.value.age) data.age = Number(editForm.value.age)
    if (editForm.value.target_weight) data.target_weight = Number(editForm.value.target_weight)
    if (editForm.value.daily_calorie_goal) data.daily_calorie_goal = Number(editForm.value.daily_calorie_goal)
    await authStore.updateProfile(data)
    // Save weight separately via weights API
    if (editForm.value.weight) {
      await api.post('/weights', { weight: Number(editForm.value.weight) })
    }
    await fetchLatestWeight()
    closeEditSheet()
  } catch (e) {
    alert('保存失败，请重试')
  } finally {
    saving.value = false
  }
}

function openFriendSheet() {
  friendSearchQuery.value = ''
  searchUsersResults.value = []
  friendSearched.value = false
  showFriendSheet.value = true
}

function closeFriendSheet() {
  showFriendSheet.value = false
}

async function searchUsers() {
  if (!friendSearchQuery.value.trim()) return
  try {
    const res = await api.get(`/friends/search?q=${encodeURIComponent(friendSearchQuery.value)}`)
    searchUsersResults.value = res.data || []
    friendSearched.value = true
  } catch (e) {
    searchUsersResults.value = []
    friendSearched.value = true
  }
}

async function sendFriendRequest(username) {
  try {
    await api.post('/friends/request', { friend_username: username })
    alert('好友请求已发送')
    closeFriendSheet()
    await fetchFriends()
  } catch (e) {
    alert('发送失败，请重试')
  }
}

async function acceptFriend(friendshipId) {
  try {
    await api.post('/friends/accept', { friendship_id: friendshipId })
    await fetchFriends()
  } catch (e) {
    alert('操作失败')
  }
}

async function fetchFriends() {
  try {
    const res = await api.get('/friends')
    friends.value = res.data || []
  } catch (e) {
    friends.value = []
  }
}

async function fetchLatestWeight() {
  try {
    const res = await api.get('/weights/latest')
    latestWeight.value = res.data
  } catch (e) {
    latestWeight.value = null
  }
}

function exportData() {
  alert('数据导出功能开发中...')
}

function handleLogout() {
  if (confirm('确定退出登录吗？')) {
    authStore.logout()
    router.push('/login')
  }
}

onMounted(async () => {
  if (!authStore.user) {
    try { await authStore.fetchUser() } catch {}
  }
  await Promise.all([fetchFriends(), fetchLatestWeight()])
})
</script>

<style scoped>
.profile-header {
  background: linear-gradient(135deg, #007aff 0%, #5ac8fa 100%);
  padding: 20px 20px 24px;
  color: #fff;
  border-radius: 0 0 24px 24px;
  margin-bottom: 8px;
}

.header-top {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 20px;
}

.avatar-large {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.25);
  border: 2.5px solid rgba(255, 255, 255, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  font-weight: 700;
  color: #fff;
  flex-shrink: 0;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-edit-hint {
  position: absolute;
  bottom: 2px;
  right: 2px;
  font-size: 16px;
  background: rgba(0, 0, 0, 0.4);
  border-radius: 50%;
  width: 22px;
  height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-info {
  flex: 1;
}

.user-name {
  font-size: 20px;
  font-weight: 700;
  color: #fff;
}

.user-tags {
  display: flex;
  gap: 6px;
  margin-top: 6px;
  flex-wrap: wrap;
}

.tag {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.9);
  background: rgba(255, 255, 255, 0.2);
  padding: 2px 8px;
  border-radius: 8px;
}

.edit-btn {
  padding: 6px 14px;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.4);
  border-radius: 12px;
  color: #fff;
  font-size: 13px;
  font-weight: 500;
}

.mini-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}

.mini-stat {
  text-align: center;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  padding: 10px 4px;
}

.ms-value {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
}

.ms-unit {
  font-size: 11px;
  font-weight: 400;
  margin-left: 1px;
}

.ms-label {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.8);
  margin-top: 2px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  margin: 16px 16px 8px;
  color: #1d1d1f;
}

.section-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 16px 16px 8px;
}

.section-title-row .section-title {
  margin: 0;
}

.add-friend-btn {
  padding: 4px 12px;
  background: #007aff;
  color: #fff;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 500;
  border: none;
}

.card {
  background: #fff;
  border-radius: 16px;
  margin: 0 16px 8px;
  overflow: hidden;
}

.body-data-card {
  padding: 4px 16px;
}

.bd-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f2;
  cursor: pointer;
}

.bd-item:last-child {
  border-bottom: none;
}

.bd-label {
  font-size: 14px;
  color: #86868b;
}

.bd-value {
  font-size: 16px;
  font-weight: 600;
  color: #1d1d1f;
}

.bd-unit {
  font-size: 12px;
  font-weight: 400;
  color: #86868b;
  margin-left: 2px;
}

.bmi-low { color: #007aff; }
.bmi-normal { color: #34c759; }
.bmi-high { color: #ff9500; }
.bmi-very-high { color: #ff3b30; }

.goals-card {
  padding: 16px;
}

.goal-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.goal-info {
  flex: 1;
}

.goal-label {
  font-size: 13px;
  color: #86868b;
  margin-bottom: 2px;
}

.goal-value {
  font-size: 18px;
  font-weight: 700;
  color: #1d1d1f;
}

.goal-value span {
  font-size: 13px;
  font-weight: 400;
  color: #86868b;
  margin-left: 2px;
}

.goal-edit-btn {
  padding: 6px 14px;
  background: #f0f0f2;
  border-radius: 10px;
  color: #007aff;
  font-size: 13px;
  font-weight: 500;
  border: none;
}

.goal-progress-section {
  margin: 12px 0;
  padding: 12px 0;
  border-top: 1px solid #f0f0f2;
  border-bottom: 1px solid #f0f0f2;
}

.goal-progress-bar {
  height: 8px;
  background: #f0f0f2;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 6px;
}

.goal-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #007aff, #5ac8fa);
  border-radius: 4px;
  transition: width 0.6s ease;
}

.goal-progress-text {
  font-size: 12px;
  color: #86868b;
}

.goal-remain {
  color: #007aff;
}

.friends-card {
  padding: 4px 16px;
}

.friend-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f2;
}

.friend-item:last-child {
  border-bottom: none;
}

.friend-avatar {
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
  flex-shrink: 0;
}

.friend-info {
  flex: 1;
}

.friend-name {
  font-size: 15px;
  font-weight: 500;
  color: #1d1d1f;
}

.friend-status {
  font-size: 12px;
  margin-top: 2px;
}

.status-accepted { color: #34c759; }
.status-pending { color: #ff9500; }

.friend-action-btn {
  padding: 6px 16px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  border: none;
  text-decoration: none;
  display: flex;
  align-items: center;
}

.friend-action-btn.accept {
  background: #34c759;
  color: #fff;
}

.friend-action-btn.battle {
  background: #007aff;
  color: #fff;
}

.settings-card {
  padding: 4px 16px;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 0;
  border-bottom: 1px solid #f0f0f2;
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-item.clickable {
  cursor: pointer;
}

.setting-item.logout {
  color: #ff3b30;
}

.setting-label {
  font-size: 15px;
  color: #1d1d1f;
}

.setting-item.logout .setting-label {
  color: #ff3b30;
}

.setting-arrow {
  font-size: 20px;
  color: #aeaeb2;
}

.switch {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 26px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0; left: 0; right: 0; bottom: 0;
  background: #e5e5ea;
  border-radius: 13px;
  transition: 0.3s;
}

.slider::before {
  position: absolute;
  content: "";
  height: 22px;
  width: 22px;
  left: 2px;
  bottom: 2px;
  background: #fff;
  border-radius: 50%;
  transition: 0.3s;
}

.switch input:checked + .slider {
  background: #34c759;
}

.switch input:checked + .slider::before {
  transform: translateX(18px);
}

.app-info {
  text-align: center;
  padding: 20px;
}

.app-version {
  font-size: 13px;
  color: #aeaeb2;
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

.edit-form {
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
  font-size: 15px;
  color: #1d1d1f;
  border: none;
  outline: none;
}

select.form-input {
  appearance: auto;
  cursor: pointer;
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

.friend-search-section {
  padding-top: 4px;
}

.friend-search-row {
  display: flex;
  gap: 8px;
  margin-bottom: 14px;
}

.friend-search-row .form-input {
  flex: 1;
}

.search-btn {
  width: 44px;
  height: 44px;
  background: #007aff;
  border-radius: 12px;
  color: #fff;
  font-size: 16px;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
}

.search-results-list {
  max-height: 300px;
  overflow-y: auto;
}

.search-user-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f2;
}

.search-user-avatar {
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

.search-user-info {
  flex: 1;
}

.search-user-name {
  font-size: 15px;
  font-weight: 500;
  color: #1d1d1f;
}

.search-user-username {
  font-size: 12px;
  color: #86868b;
  margin-top: 2px;
}

.add-btn {
  padding: 6px 14px;
  background: #007aff;
  color: #fff;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  border: none;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #aeaeb2;
  font-size: 14px;
}
</style>
