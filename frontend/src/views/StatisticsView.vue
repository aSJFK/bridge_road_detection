<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import EChart from '@/components/EChart.vue'
import { getDefectTypes, getTrend, getHomeStats } from '@/api'
import { isApiError } from '@/api/http'
import type { HomeStats } from '@/api/types'

const loading = ref(true)
const stats = ref<HomeStats | null>(null)
const pieData = ref<{ name: string; value: number }[]>([])
const trendData = ref<{ date: string; count: number }[]>([])

const classMap: Record<string, string> = {
  crack: '裂缝',
  breakage: '破损',
  comb: '梳齿缺陷',
  hole: '孔洞',
  reinforcement: '钢筋外露',
  seepage: '渗水',
  liefeng: '裂缝',
  bolou: '剥落',
  fengwo: '蜂窝',
  mamian: '麻面',
  kongdong: '空洞',
  lujin: '露筋',
  shenshui: '渗水',
  spalling: '剥落',
  pothole: '坑洞',
  corrosion: '钢筋锈蚀',
  other: '其他',
}

const pieOption = computed<echarts.EChartsOption>(() => ({
  tooltip: { trigger: 'item', formatter: '{b}: {c} 处 ({d}%)' },
  legend: { bottom: 0, icon: 'circle', itemWidth: 9, itemHeight: 9, textStyle: { color: '#ffffff', fontSize: 12 } },
  color: ['#1e90ff', '#ffa53d', '#2fd6d6', '#f0574a', '#7c7fdc'],
  series: [
    {
      name: '缺陷类型',
      type: 'pie',
      radius: ['40%', '68%'],
      center: ['50%', '44%'],
      itemStyle: { borderRadius: 7, borderColor: 'rgba(255,255,255,0.12)', borderWidth: 3 },
      label: { show: true, formatter: '{b}', fontSize: 12, color: '#ffffff' },
      data: pieData.value,
    },
  ],
}))

const barOption = computed<echarts.EChartsOption>(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 40, right: 20, top: 30, bottom: 30 },
  xAxis: {
    type: 'category',
    data: trendData.value.map((t) => t.date),
    axisLine: { lineStyle: { color: 'rgba(255,255,255,0.15)' } },
    axisLabel: { color: '#ffffff' },
  },
  yAxis: {
    type: 'value',
    minInterval: 1,
    splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } },
    axisLabel: { color: '#ffffff' },
  },
  series: [
    {
      name: '检测量',
      type: 'bar',
      data: trendData.value.map((t) => t.count),
      barWidth: 28,
      itemStyle: {
        borderRadius: [6, 6, 0, 0],
        color: {
          type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: '#4da3ff' },
            { offset: 1, color: '#1e90ff' },
          ],
        },
      },
    },
  ],
}))

const statCards = computed(() => {
  const s = stats.value
  return [
    { label: '检测图片', value: s?.image_count ?? 0 },
    { label: '缺陷总数', value: s?.defect_count ?? 0 },
    { label: '准确率', value: s?.accuracy ?? 0, suffix: '%' },
  ]
})

onMounted(async () => {
  try {
    const [s, t, trend] = await Promise.all([getHomeStats(), getDefectTypes(), getTrend(7)])
    stats.value = s
    pieData.value = Object.entries(t).map(([k, v]) => ({ name: classMap[k] ?? k, value: v }))
    trendData.value = trend
  } catch (e) {
    ElMessage.error(isApiError(e) ? e.message : '统计数据加载失败，请稍后重试')
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="page-wrap">
    <div class="page-head">
      <h2>统计报表</h2>
      <p>多维度检测数据分析与可视化</p>
    </div>

    <div class="stat-cards">
      <div v-for="c in statCards" :key="c.label" class="stat-card">
        <span class="stat-card-num mono">{{ c.value }}{{ c.suffix ?? '' }}</span>
        <span class="stat-card-label">{{ c.label }}</span>
      </div>
    </div>

    <div class="chart-grid">
      <div class="panel">
        <h3>缺陷类型分布</h3>
        <EChart :option="pieOption" height="360px" />
      </div>
      <div class="panel">
        <h3>近 7 天检测趋势</h3>
        <EChart :option="barOption" height="360px" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-wrap {
  max-width: 1440px;
  margin: 0 auto;
  padding: 24px;
  animation: fadeIn 0.4s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.page-head h2 {
  font-size: 20px;
  font-weight: 700;
  color: #fff;
}

.page-head p {
  font-size: 13px;
  color: var(--text-3);
  margin-top: 6px;
  margin-bottom: 18px;
}

.stat-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 18px;
}

.stat-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 20px;
  backdrop-filter: blur(14px);
  box-shadow: var(--shadow-card);
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.stat-card-num {
  font-size: 28px;
  font-weight: 800;
  color: #ffffff;
}

.stat-card-label {
  font-size: 13px;
  color: var(--text-3);
}

.chart-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
}

.panel {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 18px 20px;
  backdrop-filter: blur(14px);
  box-shadow: var(--shadow-card);
}

.panel h3 {
  font-size: 15px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 12px;
}

@media (max-width: 900px) {
  .stat-cards,
  .chart-grid {
    grid-template-columns: 1fr;
  }
}
</style>

