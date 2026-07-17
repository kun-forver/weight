<template>
  <view class="calorie-ring" :style="{ width: size + 'px', height: size + 'px' }">
    <canvas
      type="2d"
      :id="canvasId"
      :canvas-id="canvasId"
      class="ring-canvas"
      :style="{ width: size + 'px', height: size + 'px' }"
    ></canvas>
    <view class="ring-center">
      <text class="ring-value">{{ Math.round(consumed) }}</text>
      <text class="ring-label">kcal 已摄入</text>
      <text class="ring-goal" v-if="size >= 120">目标 {{ goal }} kcal</text>
    </view>
  </view>
</template>

<script setup>
import { computed, getCurrentInstance, watch, onMounted } from 'vue'

let canvasId = 'ringCanvas' + Math.floor(Math.random() * 1000000)

const props = defineProps({
  consumed: { type: Number, default: 0 },
  goal: { type: Number, default: 2000 },
  size: { type: Number, default: 180 },
})

const instance = getCurrentInstance()

const progress = computed(() => {
  const pct = props.goal > 0 ? props.consumed / props.goal : 0
  return Math.min(1, pct)
})

function drawRing() {
  const query = uni.createSelectorQuery().in(instance.proxy)
  query.select('#' + canvasId).fields({ node: true, size: true }).exec((res) => {
    if (!res[0] || !res[0].node) return
    const canvas = res[0].node
    const ctx = canvas.getContext('2d')
    const dpr = uni.getSystemInfoSync().pixelRatio
    const size = res[0].width
    canvas.width = size * dpr
    canvas.height = size * dpr
    ctx.scale(dpr, dpr)
    ctx.clearRect(0, 0, size, size)

    const cx = size / 2
    const cy = size / 2
    const lineWidth = Math.max(4, size * 0.06)
    const radius = size / 2 - lineWidth

    // Track circle
    ctx.beginPath()
    ctx.arc(cx, cy, radius, 0, 2 * Math.PI)
    ctx.strokeStyle = '#f0f0f2'
    ctx.lineWidth = lineWidth
    ctx.stroke()

    // Progress arc
    if (progress.value > 0) {
      ctx.beginPath()
      ctx.arc(cx, cy, radius, -Math.PI / 2, -Math.PI / 2 + 2 * Math.PI * progress.value)
      ctx.strokeStyle = '#007aff'
      ctx.lineWidth = lineWidth
      ctx.lineCap = 'round'
      ctx.stroke()
    }
  })
}

onMounted(() => {
  setTimeout(() => drawRing(), 100)
})

watch([() => props.consumed, () => props.goal], () => {
  setTimeout(() => drawRing(), 50)
})
</script>

<style scoped>
.calorie-ring {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
}

.ring-canvas {
  position: absolute;
  top: 0;
  left: 0;
}

.ring-center {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1;
}

.ring-value {
  font-size: 28px;
  font-weight: 700;
  color: #1d1d1f;
}

.ring-label {
  font-size: 11px;
  color: #86868b;
  margin-top: 2px;
}

.ring-goal {
  font-size: 10px;
  color: #aeaeb2;
  margin-top: 2px;
}
</style>
