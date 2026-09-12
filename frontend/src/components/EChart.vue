<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as echarts from 'echarts'

const props = withDefaults(
  defineProps<{
    option: echarts.EChartsOption
    height?: string
    autoresize?: boolean
  }>(),
  {
    height: '300px',
    autoresize: true,
  },
)

const el = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null

function resize() {
  chart?.resize()
}

onMounted(() => {
  if (!el.value) return
  chart = echarts.init(el.value)
  chart.setOption(props.option)
  if (props.autoresize) window.addEventListener('resize', resize)
})

onBeforeUnmount(() => {
  if (props.autoresize) window.removeEventListener('resize', resize)
  chart?.dispose()
  chart = null
})

watch(
  () => props.option,
  (opt) => chart?.setOption(opt),
  { deep: true },
)
</script>

<template>
  <div ref="el" class="echart" :style="{ height }"></div>
</template>

<style scoped>
.echart {
  width: 100%;
}
</style>
