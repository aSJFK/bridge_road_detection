<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue'

const props = withDefaults(
  defineProps<{
    value: number
    duration?: number
    decimals?: number
    suffix?: string
    prefix?: string
  }>(),
  {
    duration: 1600,
    decimals: 0,
    suffix: '',
    prefix: '',
  },
)

const display = ref('0')
let raf = 0

function animate() {
  const start = performance.now()
  const from = 0
  const to = props.value

  const tick = (now: number) => {
    const p = Math.min((now - start) / props.duration, 1)
    const eased = 1 - Math.pow(1 - p, 3)
    const val = from + (to - from) * eased
    display.value =
      props.prefix +
      val.toLocaleString('en-US', {
        minimumFractionDigits: props.decimals,
        maximumFractionDigits: props.decimals,
      }) +
      props.suffix
    if (p < 1) raf = requestAnimationFrame(tick)
  }

  raf = requestAnimationFrame(tick)
}

onMounted(animate)
onUnmounted(() => cancelAnimationFrame(raf))

watch(() => props.value, animate)
</script>

<template>
  <span class="count-up">{{ display }}</span>
</template>
