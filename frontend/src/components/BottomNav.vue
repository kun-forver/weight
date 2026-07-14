<template>
  <nav class="bottom-nav">
    <router-link
      v-for="tab in tabs"
      :key="tab.path"
      :to="tab.path"
      class="nav-item"
      :class="{ active: isActive(tab.path) }"
    >
      <span class="nav-icon">{{ tab.icon }}</span>
      <span class="nav-label">{{ tab.label }}</span>
    </router-link>
  </nav>
  <button class="fab" @click="$emit('add')">
    <span class="fab-icon">+</span>
  </button>
</template>

<script setup>
import { useRoute } from 'vue-router'
const route = useRoute()

const tabs = [
  { path: '/', label: '首页', icon: '🏠' },
  { path: '/food', label: '饮食', icon: '🍎' },
  { path: '/weight', label: '体重', icon: '⚖️' },
  { path: '/pk', label: '对战', icon: '⚔️' },
  { path: '/profile', label: '我的', icon: '👤' },
]

function isActive(path) {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}
</script>

<style scoped>
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 375px;
  max-width: 100%;
  height: 65px;
  background: #fff;
  border-top: 1px solid #e5e5ea;
  display: flex;
  align-items: center;
  justify-content: space-around;
  z-index: 100;
  padding-bottom: env(safe-area-inset-bottom, 0);
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  flex: 1;
  height: 100%;
  transition: all 0.2s;
}

.nav-icon {
  font-size: 22px;
  line-height: 1;
  transition: transform 0.2s;
}

.nav-label {
  font-size: 10px;
  color: #86868b;
  margin-top: 3px;
  font-weight: 500;
}

.nav-item.active .nav-icon {
  transform: scale(1.15);
}

.nav-item.active .nav-label {
  color: #007aff;
  font-weight: 600;
}

.fab {
  position: fixed;
  bottom: 30px;
  left: 50%;
  transform: translateX(-50%);
  width: 52px;
  height: 52px;
  background: linear-gradient(135deg, #007aff, #5ac8fa);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 20px rgba(0, 122, 255, 0.4);
  z-index: 101;
  transition: transform 0.2s, box-shadow 0.2s;
  border: 3px solid #fff;
}

.fab:active {
  transform: translateX(-50%) scale(0.92);
}

.fab-icon {
  font-size: 28px;
  color: #fff;
  font-weight: 300;
  line-height: 1;
  margin-top: -2px;
}
</style>
