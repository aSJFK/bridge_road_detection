<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import EChart from '@/components/EChart.vue'
import AiHudPanel from '@/components/AiHudPanel.vue'
import CountUp from '@/components/CountUp.vue'
import { getHomeStats, getDefectTypes, getRecentRecords } from '@/api'
import type { HomeStats, RecentRecord } from '@/api/types'
import { isApiError } from '@/api/http'
import { authState } from '@/stores/auth'

const router = useRouter()

const stats = ref<HomeStats | null>(null)
const defectTypes = ref<{ name: string; value: number }[]>([])
const records = ref<RecentRecord[]>([])
const loading = ref(true)
const loadError = ref(false)

// 功能模块滚动入场动画：进入视口时卡片从左向右展开，滑出视口时收回
const featureVisible = ref(false)
const featureGridRef = ref<HTMLElement | null>(null)
let featureObserver: IntersectionObserver | null = null

function setupFeatureObserver() {
  featureObserver = new IntersectionObserver(
    ([entry]) => {
      featureVisible.value = entry.isIntersecting
    },
    { threshold: 0.2 },
  )
  if (featureGridRef.value) featureObserver.observe(featureGridRef.value)
}

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

const metricCards = computed(() => {
  const s = stats.value
  return [
    { label: '检测图片', value: s?.image_count ?? 0, unit: '张', icon: 'bi-images' },
    { label: '缺陷总数', value: s?.defect_count ?? 0, unit: '处', icon: 'bi-bug' },
    { label: '准确率', value: s?.accuracy ?? 0, unit: '%', icon: 'bi-bullseye', decimal: true },
  ]
})

const allFeatureCards = [
  {
    icon: 'bi-camera',
    title: '智能检测',
    desc: '基于YOLOv8模型，支持图像和视频的自动缺陷检测',
    path: '/detection',
    grad: 'linear-gradient(135deg, #2f9cff, #1e90ff)',
    soft: '#e8f3ff',
    color: '#1e90ff',
  },
  {
    icon: 'bi-search',
    title: '缺陷管理',
    desc: '对检测出的缺陷进行分类、记录与跟踪管理',
    path: '/defects',
    grad: 'linear-gradient(135deg, #2fd6d6, #17a8a8)',
    soft: '#e6fbfb',
    color: '#17a8a8',
  },
  {
    icon: 'bi-bar-chart',
    title: '数据统计',
    desc: '多维度数据分析与可视化，生成检测统计报表',
    path: '/statistics',
    grad: 'linear-gradient(135deg, #7c7fdc, #6a6dd0)',
    soft: '#efeffb',
    color: '#6a6dd0',
  },
  {
    icon: 'bi-images',
    title: '数据集管理',
    desc: '管理训练数据集，支持数据标注与模型训练',
    path: '/datasets',
    grad: 'linear-gradient(135deg, #ffa53d, #ff8c1a)',
    soft: '#fff4e6',
    color: '#ff8c1a',
  },
  {
    icon: 'bi-shield-check',
    title: '系统管理',
    desc: '用户权限、角色管理及系统配置与维护',
    path: '/system',
    grad: 'linear-gradient(135deg, #f0574a, #e0402f)',
    soft: '#fdeceb',
    color: '#e0402f',
    adminOnly: true,
  },
]

// 系统管理仅管理员可见
const featureCards = computed(() =>
  allFeatureCards.filter((c) => !c.adminOnly || authState.user?.role === 'admin'),
)

const statusTagMap: Record<string, 'success' | 'warning' | 'info' | 'danger'> = {
  completed: 'success',
  running: 'warning',
  pending: 'info',
  failed: 'danger',
}

const pieOption = computed<echarts.EChartsOption>(() => ({
  tooltip: { trigger: 'item', formatter: '{b}: {c} 处 ({d}%)' },
  legend: { bottom: 0, icon: 'circle', itemWidth: 9, itemHeight: 9, textStyle: { color: '#ffffff', fontSize: 12 } },
  color: ['#1e90ff', '#ffa53d', '#2fd6d6', '#f0574a', '#7c7fdc'],
  series: [
    {
      name: '缺陷类型',
      type: 'pie',
      radius: ['46%', '72%'],
      center: ['50%', '44%'],
      avoidLabelOverlap: true,
      itemStyle: { borderRadius: 7, borderColor: 'rgba(255,255,255,0.12)', borderWidth: 3 },
      label: { show: true, formatter: '{b}', fontSize: 12, color: '#ffffff' },
      labelLine: { length: 12, length2: 10, lineStyle: { color: 'rgba(255,255,255,0.25)' } },
      emphasis: {
        scaleSize: 6,
        label: { show: true, fontSize: 14, fontWeight: 600 },
      },
      data: defectTypes.value,
    },
  ],
}))

async function viewDetail(id: number | string) {
  try {
    // 跳转到该任务关联的报告详情
    const { listReports } = await import('@/api')
    const data = await listReports({ task: id, page_size: 1 })
    if (data.results?.length) {
      router.push(`/reports/${data.results[0].id}`)
    } else {
      ElMessage.info('该记录暂无关联报告')
    }
  } catch (e) {
    ElMessage.error('详情加载失败，请稍后重试')
  }
}

function go(path: string) {
  router.push(path)
}

onMounted(async () => {
  try {
    const [s, t, r] = await Promise.all([getHomeStats(), getDefectTypes(), getRecentRecords()])
    stats.value = s
    defectTypes.value = Object.entries(t).map(([key, val]) => ({ name: classMap[key] ?? key, value: val }))
    records.value = r
    loadError.value = false
  } catch (e) {
    loadError.value = true
    ElMessage.error(isApiError(e) ? e.message : '数据加载失败，请稍后重试')
  } finally {
    loading.value = false
  }
  setupFeatureObserver()
})

onBeforeUnmount(() => {
  featureObserver?.disconnect()
})
</script>

<template>
  <div class="home">
    <!-- ===== Hero 区域 ===== -->
    <section class="hero">
      <div class="hero-inner">
        <!-- 左侧文字 -->
        <div class="hero-left">
          <div class="hero-eyebrow mono">AI · DEFECT DETECTION PLATFORM</div>
          <h1 class="hero-title">桥路缺陷检测系统</h1>
          <p class="hero-sub">基于深度学习的智能检测与分析平台</p>
          <p class="hero-desc">
            利用YOLOv8深度学习模型，对桥梁、路面等结构进行高精度缺陷检测与识别，助力工程安全与智能化管理。
          </p>
          <div class="hero-actions">
            <el-button class="btn-primary" size="large" @click="go('/detection')">
              <i class="bi bi-camera"></i>
              <span>开始检测</span>
            </el-button>
            <el-button class="btn-ghost" size="large" @click="go('/statistics')">
              <i class="bi bi-file-earmark-text"></i>
              <span>查看报告</span>
            </el-button>
          </div>
          <div class="hero-tags">
            <span class="tag"><i class="bi bi-check-circle-fill"></i>桥梁裂缝检测</span>
            <span class="tag"><i class="bi bi-check-circle-fill"></i>混凝土剥落</span>
            <span class="tag"><i class="bi bi-check-circle-fill"></i>道路坑洞识别</span>
          </div>
        </div>

        <!-- 右侧 AI 面板 -->
        <div class="hero-right">
          <AiHudPanel />
        </div>
      </div>

      <!-- 下滑提示 -->
      <div class="hero-scroll">
        <span class="hero-scroll-line"></span>
        <span>向下滚动</span>
      </div>
    </section>

    <!-- ===== 功能模块 ===== -->
    <section class="section features">
      <h2 class="section-title">功能模块</h2>
      <p class="section-sub">覆盖检测、管理、统计与维护的全流程智能平台</p>
      <div ref="featureGridRef" class="feature-grid" :class="{ 'in-view': featureVisible }">
        <div
          v-for="(f, i) in featureCards"
          :key="f.title"
          class="feature-card"
          :style="{ transitionDelay: `${i * 90}ms` }"
          @click="go(f.path)"
        >          <span class="feature-index mono">0{{ i + 1 }}</span>
          <div class="feature-icon" :style="{ background: f.grad, boxShadow: `0 6px 16px ${f.color}44` }">
            <i :class="`bi ${f.icon}`"></i>
          </div>
          <h3>{{ f.title }}</h3>
          <p>{{ f.desc }}</p>
          <span class="feature-more">
            <span>进入模块</span>
            <i class="bi bi-arrow-right"></i>
          </span>
          <span class="feature-glow" :style="{ background: f.grad }"></span>
        </div>
      </div>
    </section>

    <!-- ===== 统计数据条 ===== -->
    <section class="stats-bar">
      <div class="stats-inner">
        <div v-for="(m, i) in metricCards" :key="m.label" class="stat-item">
          <div class="stat-value mono">
            <CountUp :value="m.value" :decimals="m.decimal ? 1 : 0" :suffix="m.unit === '%' ? '%' : ''" />
          </div>
          <div class="stat-label">{{ m.label }}</div>
          <span v-if="i < metricCards.length - 1" class="stat-sep-mobile"></span>
        </div>
      </div>
    </section>

    <!-- ===== 缺陷类型分析 ===== -->
    <section class="section">
      <div class="container">
        <el-alert
          v-if="loadError"
          title="数据加载失败，请稍后重试"
          description="无法获取统计数据，请检查后端服务是否已启动。"
          type="error"
          :closable="false"
          show-icon
          class="load-alert"
        />
        <div class="section-head">
          <h2>缺陷类型分析</h2>
        </div>
        <div class="panel">
          <EChart :option="pieOption" height="320px" />
        </div>
      </div>
    </section>

    <!-- ===== 最近检测记录 ===== -->
    <section class="section">
      <div class="container">
        <div class="section-head">
          <h2>最近检测记录</h2>
        </div>
        <div class="panel">
          <el-table v-loading="loading" :data="records" class="record-table">
            <el-table-column label="检测编号" min-width="90">
              <template #default="{ row }">
                <span class="mono record-id">#{{ String(row.id).padStart(4, '0') }}</span>
              </template>
            </el-table-column>
            <el-table-column label="检测时间" min-width="160">
              <template #default="{ row }">
                <span class="mono">{{ row.created_at }}</span>
              </template>
            </el-table-column>
            <el-table-column label="任务名称" min-width="170">
              <template #default="{ row }">
                <span>{{ row.task_name }}</span>
              </template>
            </el-table-column>
            <el-table-column label="图片数量" width="100">
              <template #default="{ row }">
                <span class="mono">{{ row.image_count }}</span>
              </template>
            </el-table-column>
            <el-table-column label="缺陷数量" width="100">
              <template #default="{ row }">
                <span class="mono defect-num">{{ row.defect_count }}</span>
              </template>
            </el-table-column>
            <el-table-column label="检测状态" width="110">
              <template #default="{ row }">
                <el-tag :type="statusTagMap[row.status] ?? 'info'" effect="light" size="small" round>
                  {{ row.status_text }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="viewDetail(row.id)">查看详情</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.home {
  overflow-x: hidden;
}

/* ---------- Hero ---------- */
.hero {
  position: relative;
  min-height: calc(100vh - 64px);
  overflow: hidden;
}

.hero-inner {
  position: relative;
  z-index: 2;
  max-width: 1440px;
  min-height: calc(100vh - 64px);
  margin: 0 auto;
  padding: 48px 24px;
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  align-items: center;
  gap: 40px;
}

/* 下滑提示 */
.hero-scroll {
  position: absolute;
  bottom: 22px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 3;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  letter-spacing: 0.2em;
  color: rgba(255, 255, 255, 0.75);
  text-shadow: 0 1px 6px rgba(0, 0, 0, 0.4);
}

.hero-scroll-line {
  width: 1.5px;
  height: 34px;
  border-radius: 2px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.9), transparent);
  animation: scrollHint 1.8s ease-in-out infinite;
}

@keyframes scrollHint {
  0% {
    transform: scaleY(0);
    transform-origin: top;
    opacity: 0;
  }
  40% {
    transform: scaleY(1);
    transform-origin: top;
    opacity: 1;
  }
  60% {
    transform: scaleY(1);
    transform-origin: bottom;
    opacity: 1;
  }
  100% {
    transform: scaleY(0);
    transform-origin: bottom;
    opacity: 0;
  }
}

.hero-eyebrow {
  font-size: 11px;
  letter-spacing: 0.22em;
  color: #6fb3ff;
  margin-bottom: 14px;
}

.hero-title {
  font-size: 46px;
  font-weight: 800;
  color: #fff;
  line-height: 1.15;
  letter-spacing: 1px;
}

.hero-sub {
  font-size: 23px;
  font-weight: 500;
  color: #ffffff;
  margin-top: 12px;
}

.hero-desc {
  font-size: 15px;
  line-height: 1.8;
  color: #f0f4fa;
  max-width: 560px;
  margin-top: 14px;
}

.hero-actions {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-top: 28px;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, #2f9cff, #1e90ff);
  border: none;
  color: #fff;
  font-weight: 600;
  border-radius: 10px;
  padding: 12px 26px;
  box-shadow: 0 8px 20px rgba(30, 144, 255, 0.4);
  transition: all 0.25s ease;
}

.btn-primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 28px rgba(30, 144, 255, 0.55);
  background: linear-gradient(135deg, #3aa6ff, #2b92fb);
}

.btn-primary i {
  font-size: 17px;
}

.btn-ghost {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: transparent;
  border: 1.5px solid rgba(255, 255, 255, 0.65);
  color: #fff;
  font-weight: 500;
  border-radius: 10px;
  padding: 12px 26px;
  transition: all 0.25s ease;
}

.btn-ghost:hover {
  transform: translateY(-3px);
  background: rgba(255, 255, 255, 0.12);
  border-color: #fff;
  color: #fff;
}

.hero-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 22px;
}

.tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #cfe4fb;
  background: rgba(30, 144, 255, 0.14);
  border: 1px solid rgba(30, 144, 255, 0.3);
  border-radius: 20px;
  padding: 5px 12px;
}

.tag i {
  color: #2fd6d6;
  font-size: 11px;
}

.hero-right {
  display: flex;
  justify-content: center;
  animation: fadeInUp 0.6s ease;
}

.hero-right .hud {
  width: 100%;
  max-width: 520px;
}

/* ---------- 功能卡片 ---------- */
.features {
  padding: 64px 24px 30px;
  max-width: 1440px;
  margin: 0 auto;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 20px;
  perspective: 1200px;
}

.feature-card {
  position: relative;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 30px 22px 24px;
  text-align: center;
  cursor: pointer;
  overflow: hidden;
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  box-shadow: var(--shadow-card);
  opacity: 0;
  transform: translateX(-60px) scale(0.92);
  transition:
    opacity 0.55s cubic-bezier(0.22, 1, 0.36, 1),
    transform 0.55s cubic-bezier(0.22, 1, 0.36, 1),
    box-shadow 0.32s ease,
    border-color 0.32s ease,
    background 0.32s ease;
}

.feature-grid.in-view .feature-card {
  opacity: 1;
  transform: translateX(0) scale(1);
}

.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 18px 44px rgba(0, 0, 0, 0.5);
  border-color: rgba(255, 255, 255, 0.22);
  background: rgba(255, 255, 255, 0.085);
  transition-delay: 0s;
}

/* 底部光晕（hover 时浮现） */
.feature-glow {
  position: absolute;
  left: 50%;
  bottom: -60px;
  width: 180px;
  height: 120px;
  transform: translateX(-50%);
  border-radius: 50%;
  opacity: 0;
  filter: blur(40px);
  transition: opacity 0.32s ease, bottom 0.32s ease;
  pointer-events: none;
}

.feature-card:hover .feature-glow {
  opacity: 0.16;
  bottom: -40px;
}

/* 编号角标 */
.feature-index {
  position: absolute;
  top: 14px;
  right: 16px;
  font-size: 13px;
  font-weight: 700;
  color: #ffffff;
  letter-spacing: 0.05em;
  transition: color 0.28s ease;
}

.feature-card:hover .feature-index {
  color: #ffffff;
}

.feature-icon {
  position: relative;
  width: 62px;
  height: 62px;
  margin: 0 auto 16px;
  border-radius: 16px;
  color: #fff;
  font-size: 26px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.32s cubic-bezier(0.22, 1, 0.36, 1);
}

.feature-card:hover .feature-icon {
  transform: translateY(-4px) scale(1.06) rotate(-4deg);
}

.feature-card h3 {
  font-size: 17px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 9px;
  transition: color 0.28s ease;
}

.feature-card p {
  font-size: 12.5px;
  line-height: 1.75;
  color: var(--text-3);
  min-height: 44px;
  margin-bottom: 6px;
}

.feature-more {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12.5px;
  font-weight: 600;
  color: var(--blue);
  margin-top: 10px;
  opacity: 0;
  transform: translateX(-8px);
  transition: all 0.3s ease;
}

.feature-more i {
  transition: transform 0.3s ease;
}

.feature-card:hover .feature-more {
  opacity: 1;
  transform: translateX(0);
}

.feature-card:hover .feature-more i {
  transform: translateX(4px);
}

/* ---------- 统计条 ---------- */
.stats-bar {
  background: var(--surface);
  border-top: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  padding: 30px 24px;
}

.stats-inner {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}

.stat-item {
  text-align: center;
  flex: 1;
}

.stat-value {
  font-size: 40px;
  font-weight: 800;
  color: #fff;
  letter-spacing: 1px;
  background: linear-gradient(180deg, #ffffff, #8fc4ff);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-label {
  font-size: 14px;
  color: #ffffff;
  margin-top: 8px;
  letter-spacing: 1px;
}

.stat-sep {
  width: 1px;
  height: 44px;
  background: linear-gradient(180deg, transparent, rgba(77, 163, 255, 0.5), transparent);
}

/* ---------- 区块 ---------- */
.section {
  padding: 30px 0;
}

.container {
  max-width: 1440px;
  margin: 0 auto;
  padding: 0 24px;
}

.panel {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 16px;
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  box-shadow: var(--shadow-card);
  padding: 20px;
}

.load-alert {
  margin-bottom: 18px;
}

/* ---------- 表格 ---------- */
.record-id {
  color: var(--blue-light);
  font-size: 12.5px;
  font-weight: 600;
}

.defect-num {
  color: var(--danger);
  font-weight: 600;
}

/* ---------- 响应式 ---------- */
@media (max-width: 1200px) {
  .hero-inner {
    grid-template-columns: 1fr;
    gap: 24px;
    align-content: center;
    padding-top: 40px;
    padding-bottom: 60px;
  }
  .hero {
    min-height: auto;
    padding-bottom: 60px;
  }
  .hero-right {
    justify-content: flex-start;
  }
  .hero-right .hud {
    max-width: 640px;
  }
  .feature-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 900px) {
  .feature-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .stats-inner {
    flex-wrap: wrap;
  }
  .stat-sep {
    display: none;
  }
}

@media (max-width: 640px) {
  .hero-title {
    font-size: 30px;
  }
  .hero-sub {
    font-size: 17px;
  }
  .hero-desc {
    font-size: 14px;
  }
  .hero-actions {
    flex-direction: column;
    align-items: stretch;
  }
  .feature-grid {
    grid-template-columns: 1fr;
  }
  .hero {
    background: linear-gradient(180deg, #0a0d14, #000000);
  }
  .stat-value {
    font-size: 30px;
  }
}
</style>
