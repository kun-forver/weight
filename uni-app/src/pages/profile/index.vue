<template>
  <view class="page">
    <!-- Blue Gradient Header -->
    <view class="profile-header">
      <view class="header-top">
        <button class="avatar-large" open-type="chooseAvatar" @chooseavatar="onChooseAvatar">
          <text class="avatar-text-fallback">{{ userInitial }}</text>
          <image v-if="avatarUrl" :src="avatarUrl" class="avatar-img" mode="aspectFill" />
          <view class="avatar-edit-hint"><text>📷</text></view>
        </button>
        <view class="user-info">
          <text class="user-name">{{ userNickname }}</text>
          <view class="user-tags">
            <text class="tag" v-if="user.gender !== null && user.gender !== undefined">{{ genderText }}</text>
            <text class="tag" v-if="user.height">{{ user.height }}cm</text>
            <text class="tag" v-if="user.age">{{ user.age }}岁</text>
          </view>
        </view>
        <view class="edit-btn" @tap="openEditSheet"><text>编辑</text></view>
      </view>

      <!-- 4 Stat Mini Cards -->
      <view class="mini-stats">
        <view class="mini-stat">
          <view class="ms-value-row">
            <text class="ms-value">{{ latestWeight?.weight || '-' }}</text>
            <text class="ms-unit">kg</text>
          </view>
          <text class="ms-label">当前体重</text>
        </view>
        <view class="mini-stat">
          <view class="ms-value-row">
            <text class="ms-value">{{ user.target_weight || '-' }}</text>
            <text class="ms-unit">kg</text>
          </view>
          <text class="ms-label">目标</text>
        </view>
        <view class="mini-stat">
          <view class="ms-value-row">
            <text class="ms-value">{{ monthlyLoss }}</text>
            <text class="ms-unit">kg</text>
          </view>
          <text class="ms-label">本月减重</text>
        </view>
        <view class="mini-stat">
          <view class="ms-value-row">
            <text class="ms-value">{{ streakDays }}</text>
          </view>
          <text class="ms-label">连续打卡</text>
        </view>
      </view>
    </view>

    <!-- Body Data Section -->
    <text class="section-title">身体数据</text>
    <view class="card body-data-card">
      <view class="bd-item" @tap="openEditSheet">
        <text class="bd-label">身高</text>
        <view class="bd-value-row">
          <text class="bd-value">{{ user.height || '-' }}</text>
          <text class="bd-unit" v-if="user.height">cm</text>
        </view>
      </view>
      <view class="bd-item">
        <text class="bd-label">体重</text>
        <view class="bd-value-row">
          <text class="bd-value">{{ latestWeight?.weight || '-' }}</text>
          <text class="bd-unit" v-if="latestWeight?.weight">kg</text>
        </view>
      </view>
      <view class="bd-item">
        <text class="bd-label">体脂率</text>
        <view class="bd-value-row">
          <text class="bd-value">{{ bodyFat }}</text>
          <text class="bd-unit" v-if="bodyFat !== '-'">%</text>
        </view>
      </view>
      <view class="bd-item">
        <text class="bd-label">肌肉量</text>
        <view class="bd-value-row">
          <text class="bd-value">{{ muscleMass }}</text>
          <text class="bd-unit" v-if="muscleMass !== '-'">kg</text>
        </view>
      </view>
      <view class="bd-item">
        <text class="bd-label">BMI</text>
        <text class="bd-value" :class="bmiClass">{{ bmi }}</text>
      </view>
    </view>

    <!-- Goals Section -->
    <text class="section-title">目标设置</text>
    <view class="card goals-card">
      <view class="goal-row">
        <view class="goal-info">
          <text class="goal-label">目标体重</text>
          <view class="goal-value-row">
            <text class="goal-value">{{ user.target_weight || '未设置' }}</text>
            <text class="goal-value-unit" v-if="user.target_weight">kg</text>
          </view>
        </view>
        <view class="goal-edit-btn" @tap="openEditSheet"><text>修改</text></view>
      </view>
      <view class="goal-progress-section">
        <view class="goal-progress-bar">
          <view class="goal-progress-fill" :style="{ width: goalProgressPct + '%' }"></view>
        </view>
        <view class="goal-progress-text-row">
          <text class="goal-progress-text">已完成 {{ Math.round(goalProgressPct) }}%</text>
          <text class="goal-remain" v-if="remainingWeight > 0">· 还需减重 {{ remainingWeight.toFixed(1) }}kg</text>
        </view>
      </view>
      <view class="goal-row">
        <view class="goal-info">
          <text class="goal-label">每日热量目标</text>
          <view class="goal-value-row">
            <text class="goal-value">{{ user.daily_calorie_goal || 2000 }}</text>
            <text class="goal-value-unit">kcal</text>
          </view>
        </view>
        <view class="goal-edit-btn" @tap="openEditSheet"><text>修改</text></view>
      </view>
    </view>

    <!-- Friends Section -->
    <view class="section-title-row">
      <text class="section-title">好友列表</text>
      <view class="add-friend-btn" @tap="openFriendSheet"><text>+ 添加好友</text></view>
    </view>
    <view class="card friends-card">
      <view v-for="friend in friends" :key="friend.id" class="friend-item">
        <view class="friend-avatar"><text>{{ getInitial(friend.friend_name) }}</text></view>
        <view class="friend-info">
          <text class="friend-name">{{ friend.friend_name }}</text>
          <text class="friend-status" :class="friendStatusClass(friend.status)">{{ friendStatusText(friend.status) }}</text>
        </view>
        <view
          v-if="friend.status === 'pending'"
          class="friend-action-btn accept"
          @tap="acceptFriend(friend.id)"
        ><text>接受</text></view>
        <view
          v-else-if="friend.status === 'accepted'"
          class="friend-action-btn battle"
          @tap="goToPK"
        ><text>对战</text></view>
      </view>
      <view v-if="friends.length === 0" class="empty-state">
        <text>还没有好友，快去添加吧</text>
      </view>
    </view>

    <!-- Settings -->
    <text class="section-title">设置</text>
    <view class="card settings-card">
      <view class="setting-item">
        <text class="setting-label">🔔 推送通知</text>
        <switch :checked="settings.notifications" @change="onNotificationChange" color="#34c759" />
      </view>
      <view class="setting-item">
        <text class="setting-label">🌙 深色模式</text>
        <switch :checked="settings.darkMode" @change="onDarkModeChange" color="#34c759" />
      </view>
      <view class="setting-item" @tap="exportData">
        <text class="setting-label">📤 导出数据</text>
        <text class="setting-arrow">›</text>
      </view>
      <view class="setting-item">
        <text class="setting-label">💬 微信账号</text>
        <view class="bind-area">
          <text v-if="user.wechat_bound" class="bind-status bound">已绑定</text>
          <text v-else class="bind-status unbound">未绑定</text>
          <text v-if="user.wechat_bound" class="bind-action" @tap="handleUnbindWechat">解绑</text>
          <text v-else class="bind-action" @tap="handleBindWechat">绑定</text>
        </view>
      </view>
      <view class="setting-item" @tap="openPasswordSheet">
        <text class="setting-label">{{ user.has_password ? '🔐 修改密码' : '🔐 设置密码' }}</text>
        <text class="setting-arrow">›</text>
      </view>
      <view class="setting-item logout" @tap="handleLogout">
        <text class="setting-label logout-label">🚪 退出登录</text>
      </view>
    </view>

    <view class="app-info">
      <text class="app-version">减脂PK v1.0.0</text>
    </view>

    <!-- Bottom Sheet: Edit Profile -->
    <view v-if="showEditSheet" class="bottom-sheet-backdrop" @tap="closeEditSheet"></view>
    <view v-if="showEditSheet" class="bottom-sheet">
      <view class="sheet-header">
        <text class="sheet-title">编辑资料</text>
        <view class="sheet-close" @tap="closeEditSheet"><text>✕</text></view>
      </view>
      <scroll-view scroll-y class="edit-form-scroll">
        <view class="edit-form">
          <view class="form-group">
            <text class="form-label">昵称</text>
            <input
              v-model="editForm.nickname"
              type="nickname"
              placeholder="请输入或点击选择微信昵称"
              class="form-input"
              placeholder-class="ph-class"
              @input="onEditNicknameInput"
              @blur="onEditNicknameBlur"
            />
          </view>
          <view class="form-row">
            <view class="form-group">
              <text class="form-label">性别</text>
              <picker :range="genderOptions" range-key="label" :value="editGenderIndex" @change="onGenderChange" class="form-picker">
                <view class="picker-display">{{ genderOptions[editGenderIndex]?.label || '未设置' }}</view>
              </picker>
            </view>
            <view class="form-group">
              <text class="form-label">年龄</text>
              <input v-model="editForm.age" type="number" placeholder="如 25" class="form-input" placeholder-class="ph-class" />
            </view>
          </view>
          <view class="form-row">
            <view class="form-group">
              <text class="form-label">身高(cm)</text>
              <input v-model="editForm.height" type="digit" placeholder="如 170" class="form-input" placeholder-class="ph-class" />
            </view>
            <view class="form-group">
              <text class="form-label">体重(kg)</text>
              <input v-model="editForm.weight" type="digit" placeholder="如 70.0" class="form-input" placeholder-class="ph-class" />
            </view>
          </view>
          <view class="form-row">
            <view class="form-group">
              <text class="form-label">目标体重(kg)</text>
              <input v-model="editForm.target_weight" type="digit" placeholder="如 60.0" class="form-input" placeholder-class="ph-class" />
            </view>
            <view class="form-group">
              <text class="form-label">每日热量(kcal)</text>
              <input v-model="editForm.daily_calorie_goal" type="number" placeholder="如 1800" class="form-input" placeholder-class="ph-class" />
            </view>
          </view>
          <button class="btn-primary" @tap="saveProfile" :disabled="saving">
            {{ saving ? '保存中...' : '保存' }}
          </button>
        </view>
      </scroll-view>
    </view>

    <!-- Bottom Sheet: Add Friend -->
    <view v-if="showFriendSheet" class="bottom-sheet-backdrop" @tap="closeFriendSheet"></view>
    <view v-if="showFriendSheet" class="bottom-sheet">
      <view class="sheet-header">
        <text class="sheet-title">添加好友</text>
        <view class="sheet-close" @tap="closeFriendSheet"><text>✕</text></view>
      </view>
      <view class="friend-search-section">
        <view class="friend-search-row">
          <input
            v-model="friendSearchQuery"
            placeholder="输入用户名搜索..."
            class="form-input"
            placeholder-class="ph-class"
            @confirm="searchUsers"
          />
          <view class="search-btn" @tap="searchUsers"><text>🔍</text></view>
        </view>
        <scroll-view scroll-y class="search-results-scroll">
          <view
            v-for="u in searchUsersResults"
            :key="u.id"
            class="search-user-item"
          >
            <view class="search-user-avatar"><text>{{ getInitial(u.nickname || u.username) }}</text></view>
            <view class="search-user-info">
              <text class="search-user-name">{{ u.nickname || u.username }}</text>
              <text class="search-user-username">@{{ u.username }}</text>
            </view>
            <view class="add-btn" @tap="sendFriendRequest(u.username)"><text>+ 添加</text></view>
          </view>
          <view v-if="friendSearched && searchUsersResults.length === 0" class="empty-state">
            <text>未找到用户</text>
          </view>
        </scroll-view>
      </view>
    </view>

    <!-- Bottom Sheet: Change Password -->
    <view v-if="showPasswordSheet" class="bottom-sheet-backdrop" @tap="closePasswordSheet"></view>
    <view v-if="showPasswordSheet" class="bottom-sheet">
      <view class="sheet-header">
        <text class="sheet-title">{{ user.has_password ? '修改密码' : '设置密码' }}</text>
        <view class="sheet-close" @tap="closePasswordSheet"><text>✕</text></view>
      </view>
      <view class="edit-form">
        <view v-if="user.has_password" class="form-group">
          <text class="form-label">当前密码</text>
          <input v-model="passwordForm.old_password" :password="true" placeholder="请输入当前密码" class="form-input" placeholder-class="ph-class" />
        </view>
        <view class="form-group">
          <text class="form-label">新密码</text>
          <input v-model="passwordForm.new_password" :password="true" placeholder="请输入新密码（至少8位，两种字符）" class="form-input" placeholder-class="ph-class" />
        </view>
        <view class="form-group">
          <text class="form-label">确认新密码</text>
          <input v-model="passwordForm.confirm_password" :password="true" placeholder="请再次输入新密码" class="form-input" placeholder-class="ph-class" />
        </view>

        <text v-if="passwordError" class="error-msg-mini">{{ passwordError }}</text>
        <text v-if="passwordSuccess" class="success-msg-mini">{{ passwordSuccess }}</text>

        <button class="btn-primary" @tap="savePassword" :disabled="savingPassword">
          {{ savingPassword ? '处理中...' : (user.has_password ? '确认修改' : '确认设置') }}
        </button>
      </view>
    </view>
    <custom-tabbar :current="4" />
  </view>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import { onLoad, onShow } from '@dcloudio/uni-app'
import api from '../../api'
import { useAuthStore } from '../../stores/auth'
import CustomTabbar from '../../components/custom-tabbar/index.vue'

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

const showPasswordSheet = ref(false)
const passwordForm = ref({ old_password: '', new_password: '', confirm_password: '' })
const passwordError = ref('')
const passwordSuccess = ref('')
const savingPassword = ref(false)

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

const editGenderIndex = ref(0)
const genderOptions = [
  { label: '未设置', value: null },
  { label: '男', value: 1 },
  { label: '女', value: 0 },
]

const BASE_URL = 'https://yoyo678.cc.cd'

const userNickname = computed(() => user.value?.nickname || user.value?.username || '用户')
const userInitial = computed(() => {
  const name = user.value?.nickname || user.value?.username || 'U'
  return name.charAt(0).toUpperCase()
})

// Resolve avatar URL: relative paths from backend need server prefix
const avatarUrl = computed(() => {
  const av = user.value?.avatar
  if (!av) return ''
  if (av.startsWith('http') || av.startsWith('wxfile://') || av.startsWith('tmp')) return av
  return BASE_URL + av
})

const genderText = computed(() => {
  if (user.value?.gender === 1) return '男'
  if (user.value?.gender === 0) return '女'
  return ''
})

const monthlyLoss = computed(() => '0.0')
const streakDays = computed(() => 0)

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
    const bf = 1.2 * bmiVal + 0.23 * age - 10.8 * gender - 5.4
    return Math.max(0, bf).toFixed(1)
  }
  return '-'
})

const muscleMass = computed(() => {
  const weight = latestWeight.value?.weight
  const bf = parseFloat(bodyFat.value)
  if (weight && !isNaN(bf)) {
    return (weight * (1 - bf / 100)).toFixed(1)
  }
  return '-'
})

const goalProgressPct = computed(() => {
  const target = user.value?.target_weight
  const current = latestWeight.value?.weight
  if (!target || !current) return 0
  const startWeight = current + 5
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

function onEditNicknameInput(e) {
  if (e?.detail?.value) {
    editForm.value.nickname = e.detail.value
  }
}

function onEditNicknameBlur(e) {
  if (e?.detail?.value) {
    editForm.value.nickname = e.detail.value
  }
}

function onGenderChange(e) {
  editGenderIndex.value = e.detail.value
  editForm.value.gender = genderOptions[e.detail.value].value
}

function onNotificationChange(e) {
  settings.notifications = e.detail.value
}

function onDarkModeChange(e) {
  settings.darkMode = e.detail.value
}

function onChooseAvatar(e) {
  const tempFilePath = e?.detail?.avatarUrl
  if (!tempFilePath) return
  uni.showLoading({ title: '上传中...' })
  api.upload('/auth/avatar', tempFilePath, 'file')
    .then((uploadRes) => {
      authStore.user = uploadRes.data
      uni.setStorageSync('user', JSON.stringify(uploadRes.data))
      uni.showToast({ title: '头像更新成功', icon: 'success' })
    })
    .catch((e2) => {
      const detail = e2?.data?.detail || e2?.response?.data?.detail
      console.error('[avatar upload failed]', e2)
      uni.showToast({ title: '头像上传失败: ' + (typeof detail === 'string' ? detail : ''), icon: 'none', duration: 3000 })
    })
    .finally(() => {
      uni.hideLoading()
    })
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
  // Set gender picker index
  if (user.value?.gender === 1) editGenderIndex.value = 1
  else if (user.value?.gender === 0) editGenderIndex.value = 2
  else editGenderIndex.value = 0
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
    if (editForm.value.weight) {
      await api.post('/weights', { weight: Number(editForm.value.weight) })
    }
    await fetchLatestWeight()
    closeEditSheet()
    uni.showToast({ title: '保存成功', icon: 'success' })
  } catch (e) {
    uni.showToast({ title: '保存失败，请重试', icon: 'none' })
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
    uni.showToast({ title: '好友请求已发送', icon: 'success' })
    closeFriendSheet()
    await fetchFriends()
  } catch (e) {
    uni.showToast({ title: '发送失败，请重试', icon: 'none' })
  }
}

async function acceptFriend(friendshipId) {
  try {
    await api.post('/friends/accept', { friendship_id: friendshipId })
    await fetchFriends()
  } catch (e) {
    uni.showToast({ title: '操作失败', icon: 'none' })
  }
}

function goToPK() {
  uni.switchTab({ url: '/pages/pk/index' })
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

function openPasswordSheet() {
  passwordForm.value = { old_password: '', new_password: '', confirm_password: '' }
  passwordError.value = ''
  passwordSuccess.value = ''
  showPasswordSheet.value = true
}

function closePasswordSheet() {
  showPasswordSheet.value = false
}

async function savePassword() {
  const f = passwordForm.value
  if (!f.new_password || !f.confirm_password) {
    passwordError.value = '请填写新密码和确认密码'
    return
  }
  if (user.value.has_password && !f.old_password) {
    passwordError.value = '请输入当前密码'
    return
  }
  if (f.new_password !== f.confirm_password) {
    passwordError.value = '新密码和确认密码输入不一致'
    return
  }
  if (f.new_password.length < 8) {
    passwordError.value = '新密码长度至少为 8 位'
    return
  }

  savingPassword.value = true
  passwordError.value = ''
  passwordSuccess.value = ''

  try {
    if (user.value.has_password) {
      const res = await api.post('/auth/change-password', {
        old_password: f.old_password,
        new_password: f.new_password,
      })
      passwordSuccess.value = res.data?.message || '密码修改成功！'
    } else {
      // WeChat-only user setting a password for the first time (no old password)
      const res = await authStore.setPassword(f.new_password)
      passwordSuccess.value = res?.message || '密码设置成功！'
    }
    setTimeout(() => {
      closePasswordSheet()
    }, 1500)
  } catch (e) {
    const detail = e?.data?.detail || e?.response?.data?.detail
    passwordError.value = typeof detail === 'string' ? detail : '操作失败，请重试'
  } finally {
    savingPassword.value = false
  }
}

async function handleBindWechat() {
  try {
    const loginRes = await new Promise((resolve, reject) => {
      uni.login({ provider: 'weixin', success: resolve, fail: reject })
    })
    const code = loginRes.code
    if (!code) {
      uni.showToast({ title: '未获取到微信登录凭证', icon: 'none' })
      return
    }
    await authStore.bindWechat(code)
    uni.showToast({ title: '绑定成功', icon: 'success' })
  } catch (e) {
    const detail = e?.response?.data?.detail || e?.data?.detail
    if (typeof e?.errMsg === 'string' && e.errMsg.includes('login:fail')) {
      uni.showToast({ title: '微信授权已取消', icon: 'none' })
    } else {
      uni.showToast({ title: typeof detail === 'string' ? detail : '绑定失败', icon: 'none' })
    }
  }
}

function handleUnbindWechat() {
  uni.showModal({
    title: '解绑微信',
    content: '解绑后将无法使用微信登录此账号，确定解绑吗？',
    success: async (res) => {
      if (!res.confirm) return
      try {
        await authStore.unbindWechat()
        uni.showToast({ title: '已解绑微信', icon: 'success' })
      } catch (e) {
        const detail = e?.response?.data?.detail || e?.data?.detail
        uni.showToast({ title: typeof detail === 'string' ? detail : '解绑失败', icon: 'none' })
      }
    },
  })
}

function exportData() {
  uni.showToast({ title: '数据导出功能开发中...', icon: 'none' })
}

function handleLogout() {
  uni.showModal({
    title: '退出登录',
    content: '确定退出登录吗？',
    success: (res) => {
      if (res.confirm) {
        authStore.logout()
        uni.reLaunch({ url: '/pages/login/index' })
      }
    }
  })
}

onLoad(async () => {
  if (!authStore.user) {
    try { await authStore.fetchUser() } catch {}
  }
  await Promise.all([fetchFriends(), fetchLatestWeight()])
})

onShow(async () => {
  try { uni.hideTabBar({ animation: false }) } catch (e) {}
  if (authStore.user) {
    await Promise.all([fetchFriends(), fetchLatestWeight()])
  }
})
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #f5f5f7;
  padding-bottom: calc(150rpx + env(safe-area-inset-bottom));
}

.profile-header {
  background: linear-gradient(135deg, #007aff 0%, #5ac8fa 100%);
  padding: 40rpx 40rpx 48rpx;
  color: #fff;
  border-radius: 0 0 48rpx 48rpx;
  margin-bottom: 16rpx;
}

.header-top {
  display: flex;
  align-items: center;
  gap: 28rpx;
  margin-bottom: 40rpx;
}

.avatar-large {
  width: 130rpx;
  height: 130rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.25);
  border: 4rpx solid rgba(255, 255, 255, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  flex-shrink: 0;
  padding: 0;
  margin: 0;
  line-height: normal;
  overflow: hidden;
}

.avatar-large::after {
  border: none;
}

.avatar-img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  position: relative;
  z-index: 2;
}

.avatar-text-fallback {
  position: absolute;
  font-size: 56rpx;
  font-weight: 700;
  color: #fff;
  z-index: 1;
}

.avatar-edit-hint {
  position: absolute;
  bottom: 4rpx;
  right: 4rpx;
  font-size: 24rpx;
  background: rgba(0, 0, 0, 0.4);
  border-radius: 50%;
  width: 44rpx;
  height: 44rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.user-name {
  font-size: 40rpx;
  font-weight: 700;
  color: #fff;
}

.user-tags {
  display: flex;
  gap: 12rpx;
  margin-top: 12rpx;
  flex-wrap: wrap;
}

.tag {
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.9);
  background: rgba(255, 255, 255, 0.2);
  padding: 4rpx 16rpx;
  border-radius: 16rpx;
}

.edit-btn {
  padding: 12rpx 28rpx;
  background: rgba(255, 255, 255, 0.2);
  border: 2rpx solid rgba(255, 255, 255, 0.4);
  border-radius: 24rpx;
  color: #fff;
  font-size: 26rpx;
  font-weight: 500;
}

.mini-stats {
  display: flex;
  gap: 16rpx;
}

.mini-stat {
  flex: 1;
  text-align: center;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 24rpx;
  padding: 20rpx 8rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.ms-value-row {
  display: flex;
  align-items: baseline;
  gap: 2rpx;
}

.ms-value {
  font-size: 36rpx;
  font-weight: 700;
  color: #fff;
}

.ms-unit {
  font-size: 22rpx;
  font-weight: 400;
  color: rgba(255,255,255,0.9);
}

.ms-label {
  font-size: 20rpx;
  color: rgba(255, 255, 255, 0.8);
  margin-top: 4rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: 600;
  margin: 32rpx 32rpx 16rpx;
  color: #1d1d1f;
  display: block;
}

.section-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 32rpx 32rpx 16rpx;
}

.section-title-row .section-title {
  margin: 0;
}

.add-friend-btn {
  padding: 8rpx 24rpx;
  background: #007aff;
  color: #fff;
  border-radius: 24rpx;
  font-size: 26rpx;
  font-weight: 500;
}

.card {
  background: #fff;
  border-radius: 32rpx;
  margin: 0 32rpx 16rpx;
  overflow: hidden;
}

.body-data-card {
  padding: 8rpx 32rpx;
}

.bd-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24rpx 0;
  border-bottom: 2rpx solid #f0f0f2;
}

.bd-item:last-child {
  border-bottom: none;
}

.bd-label {
  font-size: 28rpx;
  color: #86868b;
}

.bd-value-row {
  display: flex;
  align-items: baseline;
  gap: 4rpx;
}

.bd-value {
  font-size: 32rpx;
  font-weight: 600;
  color: #1d1d1f;
}

.bd-unit {
  font-size: 24rpx;
  font-weight: 400;
  color: #86868b;
}

.bmi-low { color: #007aff; }
.bmi-normal { color: #34c759; }
.bmi-high { color: #ff9500; }
.bmi-very-high { color: #ff3b30; }

.goals-card {
  padding: 32rpx;
}

.goal-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16rpx 0;
}

.goal-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.goal-label {
  font-size: 26rpx;
  color: #86868b;
  margin-bottom: 4rpx;
}

.goal-value-row {
  display: flex;
  align-items: baseline;
  gap: 4rpx;
}

.goal-value {
  font-size: 36rpx;
  font-weight: 700;
  color: #1d1d1f;
}

.goal-value-unit {
  font-size: 26rpx;
  font-weight: 400;
  color: #86868b;
}

.goal-edit-btn {
  padding: 12rpx 28rpx;
  background: #f0f0f2;
  border-radius: 20rpx;
  color: #007aff;
  font-size: 26rpx;
  font-weight: 500;
}

.goal-progress-section {
  margin: 24rpx 0;
  padding: 24rpx 0;
  border-top: 2rpx solid #f0f0f2;
  border-bottom: 2rpx solid #f0f0f2;
}

.goal-progress-bar {
  height: 16rpx;
  background: #f0f0f2;
  border-radius: 8rpx;
  overflow: hidden;
  margin-bottom: 12rpx;
}

.goal-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #007aff, #5ac8fa);
  border-radius: 8rpx;
  transition: width 0.6s ease;
}

.goal-progress-text-row {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.goal-progress-text {
  font-size: 24rpx;
  color: #86868b;
}

.goal-remain {
  font-size: 24rpx;
  color: #007aff;
}

.friends-card {
  padding: 8rpx 32rpx;
}

.friend-item {
  display: flex;
  align-items: center;
  gap: 24rpx;
  padding: 24rpx 0;
  border-bottom: 2rpx solid #f0f0f2;
}

.friend-item:last-child {
  border-bottom: none;
}

.friend-avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #007aff, #5ac8fa);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36rpx;
  font-weight: 600;
  flex-shrink: 0;
}

.friend-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.friend-name {
  font-size: 30rpx;
  font-weight: 500;
  color: #1d1d1f;
}

.friend-status {
  font-size: 24rpx;
  margin-top: 4rpx;
}

.status-accepted { color: #34c759; }
.status-pending { color: #ff9500; }

.friend-action-btn {
  padding: 12rpx 32rpx;
  border-radius: 20rpx;
  font-size: 26rpx;
  font-weight: 600;
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
  padding: 8rpx 32rpx;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 28rpx 0;
  border-bottom: 2rpx solid #f0f0f2;
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-item.logout {
  justify-content: center;
}

.setting-label {
  font-size: 30rpx;
  color: #1d1d1f;
}

.logout-label {
  color: #ff3b30;
}

.setting-arrow {
  font-size: 40rpx;
  color: #aeaeb2;
}

.bind-area {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.bind-status {
  font-size: 26rpx;
}

.bind-status.bound {
  color: #34c759;
}

.bind-status.unbound {
  color: #aeaeb2;
}

.bind-action {
  font-size: 26rpx;
  color: #007aff;
  padding: 8rpx 24rpx;
  border: 2rpx solid #007aff;
  border-radius: 20rpx;
}

.app-info {
  text-align: center;
  padding: 40rpx;
}

.app-version {
  font-size: 26rpx;
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

.edit-form-scroll {
  max-height: 800rpx;
}

.edit-form {
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

.form-picker {
  width: 100%;
}

.picker-display {
  width: 100%;
  height: 88rpx;
  background: #f5f5f7;
  border-radius: 24rpx;
  padding: 0 28rpx;
  font-size: 30rpx;
  color: #1d1d1f;
  line-height: 88rpx;
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

.friend-search-section {
  padding-top: 8rpx;
}

.friend-search-row {
  display: flex;
  gap: 16rpx;
  margin-bottom: 28rpx;
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

.search-results-scroll {
  max-height: 600rpx;
}

.search-user-item {
  display: flex;
  align-items: center;
  gap: 24rpx;
  padding: 20rpx 0;
  border-bottom: 2rpx solid #f0f0f2;
}

.search-user-avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #007aff, #5ac8fa);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36rpx;
  font-weight: 600;
}

.search-user-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.search-user-name {
  font-size: 30rpx;
  font-weight: 500;
  color: #1d1d1f;
}

.search-user-username {
  font-size: 24rpx;
  color: #86868b;
  margin-top: 4rpx;
}

.add-btn {
  padding: 12rpx 28rpx;
  background: #007aff;
  color: #fff;
  border-radius: 20rpx;
  font-size: 26rpx;
  font-weight: 600;
}

.empty-state {
  text-align: center;
  padding: 80rpx 40rpx;
  color: #aeaeb2;
  font-size: 28rpx;
}

.error-msg-mini {
  color: #ff3b30;
  font-size: 24rpx;
  text-align: center;
  margin-top: 8rpx;
  margin-bottom: 16rpx;
  display: block;
}

.success-msg-mini {
  color: #34c759;
  font-size: 24rpx;
  text-align: center;
  margin-top: 8rpx;
  margin-bottom: 16rpx;
  display: block;
}
</style>
