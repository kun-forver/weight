<template>
  <view class="ctab" :class="{ 'ctab-dark': isDark }">
    <view
      v-for="(tab, i) in tabs"
      :key="tab.path"
      class="ctab-item"
      @tap="switchTo(i)"
    >
      <view class="ctab-chip" :class="{ on: current === i }">
        <text class="ctab-icon">{{ tab.icon }}</text>
        <text class="ctab-label" :class="{ on: current === i }">{{ tab.text }}</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'

const props = defineProps({
  current: { type: Number, default: 0 },
})

const isDark = ref(false)

onShow(() => {
  isDark.value = !!uni.getStorageSync('dark_mode')
})

const tabs = [
  { icon: '🏠', text: '首页', path: '/pages/dashboard/index' },
  { icon: '🍎', text: '饮食', path: '/pages/food/index' },
  { icon: '⚖️', text: '体重', path: '/pages/weight/index' },
  { icon: '⚔️', text: '对战', path: '/pages/pk/index' },
  { icon: '👤', text: '我的', path: '/pages/profile/index' },
]

function switchTo(i) {
  if (i === props.current) return
  uni.switchTab({ url: tabs[i].path })
}
</script>

<style scoped>
.ctab {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  background: #ffffff;
  border-top: 1rpx solid #e5e5ea;
  padding: 10rpx 0 calc(10rpx + env(safe-area-inset-bottom));
  z-index: 100;
}

.ctab-dark {
  background: #1a1a1a;
  border-top-color: #38383a;
}

.ctab-item {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 选中态圆角底色：把图标和文字一起包住 */
.ctab-chip {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 10rpx 26rpx;
  border-radius: 28rpx;
  transition: background 0.2s;
}

.ctab-chip.on {
  background: rgba(0, 122, 255, 0.13);
}

.ctab-dark .ctab-chip.on {
  background: rgba(10, 132, 255, 0.2);
}

.ctab-icon {
  font-size: 44rpx;
  line-height: 1.15;
}

.ctab-label {
  font-size: 22rpx;
  margin-top: 4rpx;
  color: #86868b;
}

.ctab-dark .ctab-label {
  color: #98989d;
}

.ctab-label.on {
  color: #007aff;
  font-weight: 600;
}

.ctab-dark .ctab-label.on {
  color: #0a84ff;
}
</style>
