<template>
  <div class="page">
    <!-- Header -->
    <header class="page-header">
      <span class="page-title">PK对战</span>
      <button class="create-btn" @click="openCreateSheet">+ 发起对战</button>
    </header>

    <div v-if="loading" class="loading-text">加载中...</div>

    <!-- Stats Row -->
    <div class="stats-card">
      <div class="stat-item">
        <div class="stat-num win">{{ pkStats.wins }}</div>
        <div class="stat-name">总胜场</div>
      </div>
      <div class="stat-divider"></div>
      <div class="stat-item">
        <div class="stat-num lose">{{ pkStats.losses }}</div>
        <div class="stat-name">总负场</div>
      </div>
      <div class="stat-divider"></div>
      <div class="stat-item">
        <div class="stat-num">{{ winRate }}%</div>
        <div class="stat-name">胜率</div>
      </div>
    </div>

    <!-- Active Battle Card -->
    <div v-if="activeBattle" class="card active-battle-card">
      <div class="battle-header">
        <span class="battle-title">⚔️ {{ activeBattle.name }}</span>
        <span class="battle-status" :class="statusClass(activeBattle.status)">{{ statusText(activeBattle.status) }}</span>
      </div>

      <!-- Battle sides -->
      <div class="battle-arena">
        <div class="battle-side left-side">
          <div class="battle-avatar">{{ getInitial(activeBattle.user_a?.name) }}</div>
          <div class="battle-name">{{ activeBattle.user_a?.name || '我' }}</div>
          <div class="battle-score">{{ activeBattle.user_a?.score || 0 }}</div>
          <div class="battle-pct">{{ activeBattle.user_a?.pct || 0 }}%</div>
        </div>

        <div class="battle-center">
          <div class="vs-text">VS</div>
          <div class="lead-indicator" v-if="activeBattle.leader">
            {{ activeBattle.leader === activeBattle.user_a?.id ? '←' : '→' }}
          </div>
        </div>

        <div class="battle-side right-side">
          <div class="battle-avatar">{{ getInitial(activeBattle.user_b?.name) }}</div>
          <div class="battle-name">{{ activeBattle.user_b?.name || '对手' }}</div>
          <div class="battle-score">{{ activeBattle.user_b?.score || 0 }}</div>
          <div class="battle-pct">{{ activeBattle.user_b?.pct || 0 }}%</div>
        </div>
      </div>

      <!-- Progress Bar -->
      <div class="battle-progress">
        <div class="bp-left" :style="{ width: (activeBattle.user_a?.pct || 0) + '%' }"></div>
        <div class="bp-right" :style="{ width: (activeBattle.user_b?.pct || 0) + '%' }"></div>
      </div>

      <!-- Day Dots -->
      <div class="day-dots-section">
        <div class="day-dots-info">
          <span>第 {{ activeBattle.days_elapsed || 0 }} / {{ activeBattle.days_total || 30 }} 天</span>
          <span class="days-left">剩余 {{ remainingDays }} 天</span>
        </div>
        <div class="day-dots">
          <span
            v-for="i in (activeBattle.days_total || 30)"
            :key="i"
            class="day-dot"
            :class="{ done: i <= (activeBattle.days_elapsed || 0) }"
          ></span>
        </div>
      </div>

      <!-- Reward -->
      <div class="battle-reward">
        <span class="reward-icon">🏆</span>
        <span class="reward-text">{{ activeBattle.reward || '加油挑战！' }}</span>
      </div>

      <!-- Action Buttons -->
      <div class="battle-actions" v-if="activeBattle.status === 'pending'">
        <button class="action-btn accept-btn" @click="acceptBattle(activeBattle.id)">接受对战</button>
      </div>
      <div class="battle-actions" v-else-if="activeBattle.status === 'active'">
        <button class="action-btn checkin-btn" @click="checkIn">每日打卡</button>
      </div>
    </div>

    <div v-else class="card no-battle-card">
      <div class="no-battle-content">
        <div class="no-battle-emoji">🎯</div>
        <div class="no-battle-text">暂无进行中的对战</div>
        <button class="create-btn-large" @click="openCreateSheet">发起对战</button>
      </div>
    </div>

    <!-- History List -->
    <div class="section-title">对战历史</div>
    <div class="history-list">
      <div
        v-for="item in historyList"
        :key="item.id"
        class="history-item"
      >
        <div class="history-result" :class="{ win: item.result === 'win', lose: item.result === 'lose' }">
          <span class="result-emoji">{{ item.result === 'win' ? '🏆' : item.result === 'lose' ? '😢' : '🤝' }}</span>
          <span class="result-text">{{ item.result === 'win' ? '胜' : item.result === 'lose' ? '负' : '平' }}</span>
        </div>
        <div class="history-info">
          <div class="history-name">{{ item.name }}</div>
          <div class="history-meta">
            {{ formatDate(item.start_date) }} - {{ formatDate(item.end_date) }} · vs {{ item.rival_name }}
          </div>
          <div class="history-scores">
            <span class="my-score" :class="item.result">{{ item.my_score }}</span>
            <span class="score-sep">:</span>
            <span class="rival-score">{{ item.rival_score }}</span>
          </div>
        </div>
      </div>
      <div v-if="historyList.length === 0" class="empty-state">暂无对战记录</div>
    </div>

    <BottomNav />

    <!-- Bottom Sheet: Create Battle -->
    <div v-if="showCreateSheet" class="bottom-sheet-backdrop" @click="closeCreateSheet"></div>
    <div v-if="showCreateSheet" class="bottom-sheet">
      <div class="sheet-header">
        <span class="sheet-title">发起对战</span>
        <button class="sheet-close" @click="closeCreateSheet">✕</button>
      </div>
      <div class="create-form">
        <!-- Friend Select -->
        <div class="form-group">
          <label class="form-label">选择对手</label>
          <div class="friend-search-row">
            <input
              v-model="friendSearchQuery"
              placeholder="搜索好友用户名..."
              class="form-input"
              @keyup.enter="searchFriends"
            />
            <button class="search-btn" @click="searchFriends">🔍</button>
          </div>
          <div class="friend-list" v-if="searchResults.length > 0">
            <div
              v-for="f in searchResults"
              :key="f.id"
              class="friend-option"
              :class="{ selected: createForm.friend_id === f.id }"
              @click="selectFriend(f)"
            >
              <div class="friend-avatar">{{ getInitial(f.nickname || f.username) }}</div>
              <div class="friend-name">{{ f.nickname || f.username }}</div>
              <span v-if="createForm.friend_id === f.id" class="check-mark">✓</span>
            </div>
          </div>
          <div v-if="myFriends.length > 0 && !searchResults.length" class="friend-list">
            <div
              v-for="f in myFriends"
              :key="f.friend_id"
              class="friend-option"
              :class="{ selected: createForm.friend_id === f.friend_id }"
              @click="selectFriendFromList(f)"
            >
              <div class="friend-avatar">{{ getInitial(f.friend_name) }}</div>
              <div class="friend-name">{{ f.friend_name }}</div>
              <span v-if="createForm.friend_id === f.friend_id" class="check-mark">✓</span>
            </div>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">对战名称</label>
          <input v-model="createForm.name" placeholder="如 30天减脂挑战" class="form-input" />
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label">开始日期</label>
            <input v-model="createForm.start_date" type="date" class="form-input" />
          </div>
          <div class="form-group">
            <label class="form-label">结束日期</label>
            <input v-model="createForm.end_date" type="date" class="form-input" />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label">我的目标(kg)</label>
            <input v-model.number="createForm.target_a" type="number" step="0.1" placeholder="如 3.0" class="form-input" />
          </div>
          <div class="form-group">
            <label class="form-label">对手目标(kg)</label>
            <input v-model.number="createForm.target_b" type="number" step="0.1" placeholder="如 3.0" class="form-input" />
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">奖励/惩罚</label>
          <input v-model="createForm.reward" placeholder="如 输了请吃饭" class="form-input" />
        </div>

        <button class="btn-primary" @click="createBattle" :disabled="creating">
          {{ creating ? '创建中...' : '发起对战' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../api'
import BottomNav from '../components/BottomNav.vue'

const loading = ref(true)
const activeBattle = ref(null)
const historyList = ref([])
const myFriends = ref([])

const showCreateSheet = ref(false)
const creating = ref(false)
const friendSearchQuery = ref('')
const searchResults = ref([])

const today = new Date().toISOString().split('T')[0]
const defaultEnd = (() => {
  const d = new Date()
  d.setDate(d.getDate() + 30)
  return d.toISOString().split('T')[0]
})()

const createForm = ref({
  friend_id: null,
  name: '',
  start_date: today,
  end_date: defaultEnd,
  target_a: 3.0,
  target_b: 3.0,
  reward: '',
})

const pkStats = computed(() => {
  const wins = historyList.value.filter(h => h.result === 'win').length
  const losses = historyList.value.filter(h => h.result === 'lose').length
  return { wins, losses }
})

const winRate = computed(() => {
  const total = pkStats.value.wins + pkStats.value.losses
  if (total === 0) return 0
  return Math.round((pkStats.value.wins / total) * 100)
})

const remainingDays = computed(() => {
  if (!activeBattle.value) return 0
  const total = activeBattle.value.days_total || 30
  const elapsed = activeBattle.value.days_elapsed || 0
  return Math.max(0, total - elapsed)
})

function getInitial(name) {
  if (!name) return '?'
  return name.charAt(0).toUpperCase()
}

function statusClass(status) {
  const map = { active: 'status-active', pending: 'status-pending', completed: 'status-done' }
  return map[status] || 'status-active'
}

function statusText(status) {
  const map = { active: '进行中', pending: '待开始', completed: '已结束' }
  return map[status] || '进行中'
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}/${d.getDate()}`
}

function openCreateSheet() {
  createForm.value = {
    friend_id: null,
    name: '',
    start_date: today,
    end_date: defaultEnd,
    target_a: 3.0,
    target_b: 3.0,
    reward: '',
  }
  searchResults.value = []
  friendSearchQuery.value = ''
  showCreateSheet.value = true
  fetchMyFriends()
}

function closeCreateSheet() {
  showCreateSheet.value = false
}

async function fetchMyFriends() {
  try {
    const res = await api.get('/friends')
    myFriends.value = (res.data || []).filter(f => f.status === 'accepted')
  } catch (e) {
    myFriends.value = []
  }
}

async function searchFriends() {
  if (!friendSearchQuery.value.trim()) return
  try {
    const res = await api.get(`/friends/search?q=${encodeURIComponent(friendSearchQuery.value)}`)
    searchResults.value = res.data || []
  } catch (e) {
    searchResults.value = []
  }
}

function selectFriend(f) {
  createForm.value.friend_id = f.id
}

function selectFriendFromList(f) {
  createForm.value.friend_id = f.friend_id
}

async function createBattle() {
  if (!createForm.value.friend_id) {
    alert('请选择对手')
    return
  }
  if (!createForm.value.name) {
    alert('请输入对战名称')
    return
  }
  creating.value = true
  try {
    await api.post('/pk', {
      friend_id: createForm.value.friend_id,
      name: createForm.value.name,
      start_date: createForm.value.start_date,
      end_date: createForm.value.end_date,
      target_a: Number(createForm.value.target_a) || 3.0,
      target_b: Number(createForm.value.target_b) || 3.0,
      reward: createForm.value.reward || '加油挑战',
    })
    closeCreateSheet()
    await fetchActiveBattle()
    await fetchHistory()
  } catch (e) {
    alert('创建失败，请重试')
  } finally {
    creating.value = false
  }
}

async function acceptBattle(id) {
  try {
    await api.post(`/pk/${id}/accept`)
    await fetchActiveBattle()
  } catch (e) {
    alert('接受失败')
  }
}

async function checkIn() {
  // Placeholder for check-in - could navigate to food/weight page
  alert('请前往饮食或体重页面完成今日打卡')
}

async function fetchActiveBattle() {
  try {
    const res = await api.get('/pk/active')
    activeBattle.value = res.data[0] || null
  } catch (e) {
    activeBattle.value = null
  }
}

async function fetchHistory() {
  try {
    const res = await api.get('/pk/history')
    historyList.value = res.data || []
  } catch (e) {
    historyList.value = []
  }
}

onMounted(async () => {
  loading.value = true
  await Promise.all([fetchActiveBattle(), fetchHistory()])
  loading.value = false
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

.create-btn {
  padding: 6px 14px;
  background: #007aff;
  color: #fff;
  border-radius: 16px;
  font-size: 13px;
  font-weight: 600;
  border: none;
}

.loading-text {
  text-align: center;
  padding: 20px;
  color: #86868b;
}

.stats-card {
  display: flex;
  align-items: center;
  justify-content: space-around;
  background: #fff;
  border-radius: 16px;
  padding: 18px 16px;
  margin: 8px 16px;
}

.stat-item {
  text-align: center;
  flex: 1;
}

.stat-num {
  font-size: 24px;
  font-weight: 700;
  color: #1d1d1f;
}

.stat-num.win { color: #34c759; }
.stat-num.lose { color: #ff3b30; }

.stat-name {
  font-size: 12px;
  color: #86868b;
  margin-top: 4px;
}

.stat-divider {
  width: 1px;
  height: 30px;
  background: #f0f0f2;
}

.card {
  background: #fff;
  border-radius: 16px;
  padding: 16px;
  margin: 8px 16px;
}

.active-battle-card {
  padding: 18px;
}

.battle-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.battle-title {
  font-size: 17px;
  font-weight: 600;
  color: #1d1d1f;
}

.battle-status {
  font-size: 11px;
  padding: 3px 10px;
  border-radius: 10px;
  font-weight: 500;
}

.status-active { background: #e8f5e9; color: #34c759; }
.status-pending { background: #fff3cd; color: #ff9500; }
.status-done { background: #f0f0f2; color: #86868b; }

.battle-arena {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
}

.battle-side {
  text-align: center;
  flex: 1;
}

.battle-avatar {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: linear-gradient(135deg, #007aff, #5ac8fa);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  font-weight: 600;
  margin: 0 auto 8px;
}

.right-side .battle-avatar {
  background: linear-gradient(135deg, #ff9500, #ff6b6b);
}

.battle-name {
  font-size: 12px;
  color: #86868b;
  margin-bottom: 4px;
}

.battle-score {
  font-size: 24px;
  font-weight: 700;
  color: #1d1d1f;
}

.battle-pct {
  font-size: 13px;
  font-weight: 600;
  color: #007aff;
  margin-top: 2px;
}

.right-side .battle-pct { color: #ff9500; }

.battle-center {
  flex: 0 0 50px;
  text-align: center;
}

.vs-text {
  font-size: 20px;
  font-weight: 800;
  color: #aeaeb2;
}

.lead-indicator {
  font-size: 16px;
  color: #007aff;
  font-weight: 700;
  margin-top: 4px;
}

.battle-progress {
  display: flex;
  height: 8px;
  border-radius: 4px;
  overflow: hidden;
  background: #f0f0f2;
  margin: 8px 0 16px;
}

.bp-left {
  background: linear-gradient(90deg, #007aff, #5ac8fa);
  transition: width 0.6s ease;
}

.bp-right {
  background: linear-gradient(90deg, #ff6b6b, #ff9500);
  transition: width 0.6s ease;
  margin-left: auto;
}

.day-dots-section {
  margin-bottom: 14px;
}

.day-dots-info {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #86868b;
  margin-bottom: 8px;
}

.days-left {
  color: #007aff;
  font-weight: 600;
}

.day-dots {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.day-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #e5e5ea;
}

.day-dot.done {
  background: #34c759;
}

.battle-reward {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fffbf0;
  border-radius: 12px;
  padding: 10px 14px;
  margin-bottom: 14px;
}

.reward-icon {
  font-size: 18px;
}

.reward-text {
  font-size: 14px;
  color: #1d1d1f;
  font-weight: 500;
}

.battle-actions {
  display: flex;
  gap: 10px;
}

.action-btn {
  flex: 1;
  height: 42px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  border: none;
  cursor: pointer;
}

.accept-btn {
  background: #34c759;
  color: #fff;
}

.checkin-btn {
  background: #007aff;
  color: #fff;
}

.no-battle-card {
  text-align: center;
}

.no-battle-content {
  padding: 20px 0;
}

.no-battle-emoji {
  font-size: 40px;
  margin-bottom: 10px;
}

.no-battle-text {
  font-size: 15px;
  color: #86868b;
  margin-bottom: 16px;
}

.create-btn-large {
  padding: 10px 28px;
  background: #007aff;
  color: #fff;
  border-radius: 14px;
  font-size: 15px;
  font-weight: 600;
  border: none;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  margin: 16px 16px 8px;
  color: #1d1d1f;
}

.history-list {
  margin: 0 16px;
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  margin-bottom: 16px;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border-bottom: 1px solid #f0f0f2;
}

.history-item:last-child {
  border-bottom: none;
}

.history-result {
  width: 44px;
  text-align: center;
}

.result-emoji {
  font-size: 22px;
  display: block;
}

.result-text {
  font-size: 11px;
  color: #86868b;
  display: block;
}

.history-result.win .result-text { color: #34c759; }
.history-result.lose .result-text { color: #ff3b30; }

.history-info {
  flex: 1;
}

.history-name {
  font-size: 15px;
  font-weight: 600;
  color: #1d1d1f;
}

.history-meta {
  font-size: 12px;
  color: #86868b;
  margin-top: 2px;
}

.history-scores {
  margin-top: 4px;
  font-size: 15px;
  font-weight: 600;
}

.my-score.win { color: #34c759; }
.my-score.lose { color: #ff3b30; }
.score-sep { color: #aeaeb2; margin: 0 4px; }
.rival-score { color: #86868b; }

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

.create-form {
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

.friend-search-row {
  display: flex;
  gap: 8px;
  margin-bottom: 10px;
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

.friend-list {
  max-height: 160px;
  overflow-y: auto;
}

.friend-option {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 12px;
  background: #f5f5f7;
  margin-bottom: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.friend-option.selected {
  background: #eef4ff;
  border: 1.5px solid #007aff;
}

.friend-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #007aff, #5ac8fa);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  flex-shrink: 0;
}

.friend-name {
  flex: 1;
  font-size: 14px;
  color: #1d1d1f;
}

.check-mark {
  color: #007aff;
  font-size: 18px;
  font-weight: 700;
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
