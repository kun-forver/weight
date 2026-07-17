<template>
  <view class="page">
    <!-- Header -->
    <view class="page-header">
      <text class="page-title">PK对战</text>
      <view class="create-btn" @tap="openCreateSheet">+ 发起对战</view>
    </view>

    <view v-if="loading" class="loading-text"><text>加载中...</text></view>

    <!-- Stats Row -->
    <view class="stats-card">
      <view class="stat-item">
        <text class="stat-num win">{{ pkStats.wins }}</text>
        <text class="stat-name">总胜场</text>
      </view>
      <view class="stat-divider"></view>
      <view class="stat-item">
        <text class="stat-num lose">{{ pkStats.losses }}</text>
        <text class="stat-name">总负场</text>
      </view>
      <view class="stat-divider"></view>
      <view class="stat-item">
        <text class="stat-num">{{ winRate }}%</text>
        <text class="stat-name">胜率</text>
      </view>
    </view>

    <!-- Active Battle Card -->
    <view v-if="activeBattle" class="card active-battle-card">
      <view class="battle-header">
        <text class="battle-title">⚔️ {{ activeBattle.name }}</text>
        <text class="battle-status" :class="statusClass(activeBattle.status)">{{ statusText(activeBattle.status) }}</text>
      </view>

      <!-- Battle sides -->
      <view class="battle-arena">
        <view class="battle-side left-side">
          <view class="battle-avatar">{{ getInitial(activeBattle.user_a?.name) }}</view>
          <text class="battle-name">{{ activeBattle.user_a?.name || '我' }}</text>
          <text class="battle-score">{{ activeBattle.user_a?.score || 0 }}</text>
          <text class="battle-pct">{{ activeBattle.user_a?.pct || 0 }}%</text>
        </view>

        <view class="battle-center">
          <text class="vs-text">VS</text>
          <text class="lead-indicator" v-if="activeBattle.leader">{{ activeBattle.leader === activeBattle.user_a?.id ? '←' : '→' }}</text>
        </view>

        <view class="battle-side right-side">
          <view class="battle-avatar">{{ getInitial(activeBattle.user_b?.name) }}</view>
          <text class="battle-name">{{ activeBattle.user_b?.name || '对手' }}</text>
          <text class="battle-score">{{ activeBattle.user_b?.score || 0 }}</text>
          <text class="battle-pct">{{ activeBattle.user_b?.pct || 0 }}%</text>
        </view>
      </view>

      <!-- Progress Bar -->
      <view class="battle-progress">
        <view class="bp-left" :style="{ width: (activeBattle.user_a?.pct || 0) + '%' }"></view>
        <view class="bp-right" :style="{ width: (activeBattle.user_b?.pct || 0) + '%' }"></view>
      </view>

      <!-- Day Dots -->
      <view class="day-dots-section">
        <view class="day-dots-info">
          <text>第 {{ activeBattle.days_elapsed || 0 }} / {{ activeBattle.days_total || 30 }} 天</text>
          <text class="days-left">剩余 {{ remainingDays }} 天</text>
        </view>
        <view class="day-dots">
          <view
            v-for="i in (activeBattle.days_total || 30)"
            :key="i"
            class="day-dot"
            :class="{ done: i <= (activeBattle.days_elapsed || 0) }"
          ></view>
        </view>
      </view>

      <!-- Reward -->
      <view class="battle-reward">
        <text class="reward-icon">🏆</text>
        <text class="reward-text">{{ activeBattle.reward || '加油挑战！' }}</text>
      </view>

      <!-- Action Buttons -->
      <view class="battle-actions" v-if="activeBattle.status === 'pending'">
        <button class="action-btn accept-btn" @tap="acceptBattle(activeBattle.id)">接受对战</button>
      </view>
      <view class="battle-actions" v-else-if="activeBattle.status === 'active'">
        <button class="action-btn checkin-btn" @tap="checkIn">每日打卡</button>
      </view>
    </view>

    <view v-else class="card no-battle-card">
      <view class="no-battle-content">
        <text class="no-battle-emoji">🎯</text>
        <text class="no-battle-text">暂无进行中的对战</text>
        <button class="create-btn-large" @tap="openCreateSheet">发起对战</button>
      </view>
    </view>

    <!-- History List -->
    <text class="section-title">对战历史</text>
    <view class="history-list">
      <view
        v-for="item in historyList"
        :key="item.id"
        class="history-item"
      >
        <view class="history-result" :class="{ win: item.result === 'win', lose: item.result === 'lose' }">
          <text class="result-emoji">{{ item.result === 'win' ? '🏆' : item.result === 'lose' ? '😢' : '🤝' }}</text>
          <text class="result-text">{{ item.result === 'win' ? '胜' : item.result === 'lose' ? '负' : '平' }}</text>
        </view>
        <view class="history-info">
          <text class="history-name">{{ item.name }}</text>
          <text class="history-meta">{{ formatDate(item.start_date) }} - {{ formatDate(item.end_date) }} · vs {{ item.rival_name }}</text>
          <view class="history-scores">
            <text class="my-score" :class="item.result">{{ item.my_score }}</text>
            <text class="score-sep">:</text>
            <text class="rival-score">{{ item.rival_score }}</text>
          </view>
        </view>
      </view>
      <view v-if="historyList.length === 0" class="empty-state">
        <text>暂无对战记录</text>
      </view>
    </view>

    <!-- Bottom Sheet: Create Battle -->
    <view v-if="showCreateSheet" class="bottom-sheet-backdrop" @tap="closeCreateSheet"></view>
    <view v-if="showCreateSheet" class="bottom-sheet">
      <view class="sheet-header">
        <text class="sheet-title">发起对战</text>
        <view class="sheet-close" @tap="closeCreateSheet">✕</view>
      </view>
      <scroll-view scroll-y class="create-form-scroll">
        <view class="create-form">
          <!-- Friend Select -->
          <view class="form-group">
            <text class="form-label">选择对手</text>
            <view class="friend-search-row">
              <input
                v-model="friendSearchQuery"
                placeholder="搜索好友用户名..."
                class="form-input"
                placeholder-class="ph-class"
                @confirm="searchFriends"
              />
              <view class="search-btn" @tap="searchFriends"><text>🔍</text></view>
            </view>
            <view class="friend-list" v-if="searchResults.length > 0">
              <view
                v-for="f in searchResults"
                :key="f.id"
                class="friend-option"
                :class="{ selected: createForm.friend_id === f.id }"
                @tap="selectFriend(f)"
              >
                <view class="friend-avatar"><text>{{ getInitial(f.nickname || f.username) }}</text></view>
                <text class="friend-name">{{ f.nickname || f.username }}</text>
                <text v-if="createForm.friend_id === f.id" class="check-mark">✓</text>
              </view>
            </view>
            <view v-if="myFriends.length > 0 && !searchResults.length" class="friend-list">
              <view
                v-for="f in myFriends"
                :key="f.friend_id"
                class="friend-option"
                :class="{ selected: createForm.friend_id === f.friend_id }"
                @tap="selectFriendFromList(f)"
              >
                <view class="friend-avatar"><text>{{ getInitial(f.friend_name) }}</text></view>
                <text class="friend-name">{{ f.friend_name }}</text>
                <text v-if="createForm.friend_id === f.friend_id" class="check-mark">✓</text>
              </view>
            </view>
          </view>

          <view class="form-group">
            <text class="form-label">对战名称</text>
            <input v-model="createForm.name" placeholder="如 30天减脂挑战" class="form-input" placeholder-class="ph-class" />
          </view>

          <view class="form-row">
            <view class="form-group">
              <text class="form-label">开始日期</text>
              <picker mode="date" :value="createForm.start_date" @change="onStartDateChange">
                <view class="date-picker-display">{{ createForm.start_date || '选择日期' }}</view>
              </picker>
            </view>
            <view class="form-group">
              <text class="form-label">结束日期</text>
              <picker mode="date" :value="createForm.end_date" @change="onEndDateChange">
                <view class="date-picker-display">{{ createForm.end_date || '选择日期' }}</view>
              </picker>
            </view>
          </view>

          <view class="form-row">
            <view class="form-group">
              <text class="form-label">我的目标(kg)</text>
              <input v-model="createForm.target_a" type="digit" placeholder="如 3.0" class="form-input" placeholder-class="ph-class" />
            </view>
            <view class="form-group">
              <text class="form-label">对手目标(kg)</text>
              <input v-model="createForm.target_b" type="digit" placeholder="如 3.0" class="form-input" placeholder-class="ph-class" />
            </view>
          </view>

          <view class="form-group">
            <text class="form-label">奖励/惩罚</text>
            <input v-model="createForm.reward" placeholder="如 输了请吃饭" class="form-input" placeholder-class="ph-class" />
          </view>

          <button class="btn-primary" @tap="createBattle" :disabled="creating">
            {{ creating ? '创建中...' : '发起对战' }}
          </button>
        </view>
      </scroll-view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onLoad, onShow } from '@dcloudio/uni-app'
import api from '../../api'

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
  target_a: '3.0',
  target_b: '3.0',
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

function onStartDateChange(e) {
  createForm.value.start_date = e.detail.value
}

function onEndDateChange(e) {
  createForm.value.end_date = e.detail.value
}

function openCreateSheet() {
  createForm.value = {
    friend_id: null,
    name: '',
    start_date: today,
    end_date: defaultEnd,
    target_a: '3.0',
    target_b: '3.0',
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
    uni.showToast({ title: '请选择对手', icon: 'none' })
    return
  }
  if (!createForm.value.name) {
    uni.showToast({ title: '请输入对战名称', icon: 'none' })
    return
  }
  creating.value = true
  try {
    await api.post('/pk', {
      user_b: createForm.value.friend_id,
      name: createForm.value.name,
      end_date: createForm.value.end_date,
      target_a: Number(createForm.value.target_a) || 3.0,
      target_b: Number(createForm.value.target_b) || 3.0,
      reward: createForm.value.reward || '加油挑战',
    })
    closeCreateSheet()
    await fetchActiveBattle()
    await fetchHistory()
  } catch (e) {
    uni.showToast({ title: '创建失败，请重试', icon: 'none' })
  } finally {
    creating.value = false
  }
}

async function acceptBattle(id) {
  try {
    await api.post(`/pk/${id}/accept`)
    await fetchActiveBattle()
  } catch (e) {
    uni.showToast({ title: '接受失败', icon: 'none' })
  }
}

async function checkIn() {
  uni.showModal({
    title: '每日打卡',
    content: '请前往饮食或体重页面完成今日打卡',
    showCancel: false
  })
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

onLoad(async () => {
  loading.value = true
  await Promise.all([fetchActiveBattle(), fetchHistory()])
  loading.value = false
})

onShow(async () => {
  if (!loading.value) {
    await Promise.all([fetchActiveBattle(), fetchHistory()])
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

.create-btn {
  padding: 12rpx 28rpx;
  background: #007aff;
  color: #fff;
  border-radius: 32rpx;
  font-size: 26rpx;
  font-weight: 600;
}

.loading-text {
  text-align: center;
  padding: 40rpx;
  color: #86868b;
  margin-top: 120rpx;
  font-size: 28rpx;
}

.stats-card {
  display: flex;
  align-items: center;
  justify-content: space-around;
  background: #fff;
  border-radius: 32rpx;
  padding: 36rpx 32rpx;
  margin: 136rpx 32rpx 16rpx;
}

.stat-item {
  text-align: center;
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-num {
  font-size: 48rpx;
  font-weight: 700;
  color: #1d1d1f;
}

.stat-num.win { color: #34c759; }
.stat-num.lose { color: #ff3b30; }

.stat-name {
  font-size: 24rpx;
  color: #86868b;
  margin-top: 8rpx;
}

.stat-divider {
  width: 2rpx;
  height: 60rpx;
  background: #f0f0f2;
}

.card {
  background: #fff;
  border-radius: 32rpx;
  padding: 32rpx;
  margin: 16rpx 32rpx;
}

.active-battle-card {
  padding: 36rpx;
}

.battle-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32rpx;
}

.battle-title {
  font-size: 34rpx;
  font-weight: 600;
  color: #1d1d1f;
}

.battle-status {
  font-size: 22rpx;
  padding: 6rpx 20rpx;
  border-radius: 20rpx;
  font-weight: 500;
}

.status-active { background: #e8f5e9; color: #34c759; }
.status-pending { background: #fff3cd; color: #ff9500; }
.status-done { background: #f0f0f2; color: #86868b; }

.battle-arena {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24rpx 0;
}

.battle-side {
  text-align: center;
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.battle-avatar {
  width: 104rpx;
  height: 104rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #007aff, #5ac8fa);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 44rpx;
  font-weight: 600;
  margin-bottom: 16rpx;
}

.right-side .battle-avatar {
  background: linear-gradient(135deg, #ff9500, #ff6b6b);
}

.battle-name {
  font-size: 24rpx;
  color: #86868b;
  margin-bottom: 8rpx;
}

.battle-score {
  font-size: 48rpx;
  font-weight: 700;
  color: #1d1d1f;
}

.battle-pct {
  font-size: 26rpx;
  font-weight: 600;
  color: #007aff;
  margin-top: 4rpx;
}

.right-side .battle-pct { color: #ff9500; }

.battle-center {
  flex: 0 0 100rpx;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.vs-text {
  font-size: 40rpx;
  font-weight: 800;
  color: #aeaeb2;
}

.lead-indicator {
  font-size: 32rpx;
  color: #007aff;
  font-weight: 700;
  margin-top: 8rpx;
}

.battle-progress {
  display: flex;
  height: 16rpx;
  border-radius: 8rpx;
  overflow: hidden;
  background: #f0f0f2;
  margin: 16rpx 0 32rpx;
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
  margin-bottom: 28rpx;
}

.day-dots-info {
  display: flex;
  justify-content: space-between;
  font-size: 24rpx;
  color: #86868b;
  margin-bottom: 16rpx;
}

.days-left {
  color: #007aff;
  font-weight: 600;
}

.day-dots {
  display: flex;
  flex-wrap: wrap;
  gap: 8rpx;
}

.day-dot {
  width: 24rpx;
  height: 24rpx;
  border-radius: 50%;
  background: #e5e5ea;
}

.day-dot.done {
  background: #34c759;
}

.battle-reward {
  display: flex;
  align-items: center;
  gap: 16rpx;
  background: #fffbf0;
  border-radius: 24rpx;
  padding: 20rpx 28rpx;
  margin-bottom: 28rpx;
}

.reward-icon {
  font-size: 36rpx;
}

.reward-text {
  font-size: 28rpx;
  color: #1d1d1f;
  font-weight: 500;
}

.battle-actions {
  display: flex;
  gap: 20rpx;
}

.action-btn {
  flex: 1;
  height: 88rpx;
  border-radius: 24rpx;
  font-size: 30rpx;
  font-weight: 600;
  border: none;
  line-height: 88rpx;
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
  padding: 40rpx 0;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.no-battle-emoji {
  font-size: 80rpx;
  margin-bottom: 20rpx;
}

.no-battle-text {
  font-size: 30rpx;
  color: #86868b;
  margin-bottom: 32rpx;
}

.create-btn-large {
  padding: 20rpx 56rpx;
  background: #007aff;
  color: #fff;
  border-radius: 28rpx;
  font-size: 30rpx;
  font-weight: 600;
  border: none;
  line-height: 1.5;
}

.section-title {
  font-size: 32rpx;
  font-weight: 600;
  margin: 32rpx 32rpx 16rpx;
  color: #1d1d1f;
  display: block;
}

.history-list {
  margin: 0 32rpx;
  background: #fff;
  border-radius: 32rpx;
  overflow: hidden;
  margin-bottom: 32rpx;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 24rpx;
  padding: 28rpx 32rpx;
  border-bottom: 2rpx solid #f0f0f2;
}

.history-item:last-child {
  border-bottom: none;
}

.history-result {
  width: 88rpx;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.result-emoji {
  font-size: 44rpx;
}

.result-text {
  font-size: 22rpx;
  color: #86868b;
  margin-top: 4rpx;
}

.history-result.win .result-text { color: #34c759; }
.history-result.lose .result-text { color: #ff3b30; }

.history-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.history-name {
  font-size: 30rpx;
  font-weight: 600;
  color: #1d1d1f;
}

.history-meta {
  font-size: 24rpx;
  color: #86868b;
  margin-top: 4rpx;
}

.history-scores {
  margin-top: 8rpx;
  display: flex;
  align-items: baseline;
  gap: 8rpx;
}

.my-score {
  font-size: 30rpx;
  font-weight: 600;
  color: #1d1d1f;
}

.my-score.win { color: #34c759; }
.my-score.lose { color: #ff3b30; }

.score-sep { color: #aeaeb2; }
.rival-score { color: #86868b; font-size: 30rpx; font-weight: 600; }

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

.create-form-scroll {
  max-height: 1000rpx;
}

.create-form {
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
  font-size: 30rpx;
  color: #1d1d1f;
}

.ph-class {
  color: #aeaeb2;
}

.date-picker-display {
  width: 100%;
  height: 88rpx;
  background: #f5f5f7;
  border-radius: 24rpx;
  padding: 0 28rpx;
  font-size: 30rpx;
  color: #1d1d1f;
  line-height: 88rpx;
}

.friend-search-row {
  display: flex;
  gap: 16rpx;
  margin-bottom: 20rpx;
}

.friend-search-row .form-input {
  flex: 1;
}

.search-btn {
  width: 88rpx;
  height: 88rpx;
  background: #007aff;
  border-radius: 24rpx;
  color: #fff;
  font-size: 32rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.friend-list {
  max-height: 320rpx;
  overflow: hidden;
}

.friend-option {
  display: flex;
  align-items: center;
  gap: 20rpx;
  padding: 20rpx 24rpx;
  border-radius: 24rpx;
  background: #f5f5f7;
  margin-bottom: 12rpx;
}

.friend-option.selected {
  background: #eef4ff;
  border: 3rpx solid #007aff;
}

.friend-avatar {
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #007aff, #5ac8fa);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
  font-weight: 600;
  flex-shrink: 0;
}

.friend-name {
  flex: 1;
  font-size: 28rpx;
  color: #1d1d1f;
}

.check-mark {
  color: #007aff;
  font-size: 36rpx;
  font-weight: 700;
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
</style>
