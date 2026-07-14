<template>
  <div class="calorie-ring">
    <svg :width="size" :height="size" :viewBox="`0 0 ${size} ${size}`">
      <!-- Background ring -->
      <circle
        :cx="center"
        :cy="center"
        :r="radius"
        fill="none"
        stroke="#f0f0f2"
        :stroke-width="strokeWidth"
      />
      <!-- Progress ring -->
      <circle
        :cx="center"
        :cy="center"
        :r="radius"
        fill="none"
        stroke="#007aff"
        :stroke-width="strokeWidth"
        stroke-linecap="round"
        :stroke-dasharray="circumference"
        :stroke-dashoffset="dashOffset"
        :transform="`rotate(-90 ${center} ${center})`"
        style="transition: stroke-dashoffset 0.6s ease"
      />
    </svg>
    <div class="ring-center">
      <div class="consumed-value">{{ Math.round(consumed) }}</div>
      <div class="consumed-label">kcal 已摄入</div>
      <div class="goal-text">目标 {{ goal }} kcal</div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  consumed: { type: Number, default: 0 },
  goal: { type: Number, default: 2000 },
  size: { type: Number, default: 180 },
})

const center = computed(() => props.size / 2)
const strokeWidth = 14
const radius = computed(() => (props.size - strokeWidth * 2) / 2)
const circumference = computed(() => 2 * Math.PI * radius.value)
const percentage = computed(() => {
  if (props.goal <= 0) return 0
  return Math.min(props.consumed / props.goal, 1)
})
const dashOffset = computed(() => circumference.value * (1 - percentage.value))
</script>

<style scoped>
.calorie-ring {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ring-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.consumed-value {
  font-size: 32px;
  font-weight: 700;
  color: #1d1d1f;
  line-height: 1.1;
}

.consumed-label {
  font-size: 12px;
  color: #86868b;
  margin-top: 2px;
}

.goal-text {
  font-size: 11px;
  color: #aeaeb2;
  margin-top: 6px;
}
</style>
