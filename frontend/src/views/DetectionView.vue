<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, Upload, Loading, RefreshRight } from '@element-plus/icons-vue'
import { createTask } from '@/api'
import { isApiError, mediaUrl } from '@/api/http'
import type { DetectionTask } from '@/api/types'

const router = useRouter()
const loading = ref(false)
const originalUrl = ref('')
const originalName = ref('')
const originalFile = ref<File | null>(null)
const result = ref<ReportResultData | null>(null)
const taskInfo = ref<DetectionTask | null>(null)
const savedReportId = ref<number | null>(null)
const reportFileUrl = ref('')
const resultImageUrl = ref('')

interface ReportResultData {
  total_defects: number
  accuracy: number
  images?: {
    result_image?: string
    image_width?: number
    image_height?: number
    defects?: DefectItem[]
  }[]
}

interface DefectItem {
  id: number
  defect_type: string
  source: string
  confidence: number
  x1: number
  y1: number
  x2: number
  y2: number
  area: number
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

const colorMap: Record<string, string> = {
  crack: '#1e90ff',
  breakage: '#ffa53d',
  comb: '#2fd6d6',
  hole: '#f0574a',
  reinforcement: '#9064fa',
  seepage: '#64b4dc',
  liefeng: '#1e90ff',
  bolou: '#ffa53d',
  fengwo: '#2fd6d6',
  mamian: '#7c7fdc',
  kongdong: '#f0574a',
  lujin: '#9064fa',
  shenshui: '#64b4dc',
  spalling: '#ffa53d',
  pothole: '#2fd6d6',
  corrosion: '#f0574a',
  other: '#7c7fdc',
}

const stats = computed(() => {
  const img = result.value?.images?.[0]
  if (!img?.defects) return []
  const map = new Map<string, { label: string; count: number; color: string }>()
  for (const obj of img.defects) {
    const cur = map.get(obj.defect_type) ?? { label: classMap[obj.defect_type] ?? obj.defect_type, count: 0, color: colorMap[obj.defect_type] ?? '#7c7fdc' }
    cur.count += 1
    map.set(obj.defect_type, cur)
  }
  return [...map.values()]
})

// 缺陷明细列表 + 当前选中的缺陷
const defects = computed(() => result.value?.images?.[0]?.defects ?? [])
const selectedDefectId = ref<number | null>(null)

function selectDefect(id: number) {
  // 同一时间只有一个红色框：悬停选中
  selectedDefectId.value = id
}

function clearDefect() {
  selectedDefectId.value = null
}

function readAsDataURL(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result as string)
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

async function handleFile(file: File) {
  if (!file.type.startsWith('image/')) {
    ElMessage.warning('请选择图片文件')
    return
  }
  loading.value = true
  result.value = null
  taskInfo.value = null
  savedReportId.value = null
  reportFileUrl.value = ''
  resultImageUrl.value = ''
  selectedDefectId.value = null
  originalName.value = file.name
  originalFile.value = file
  try {
    originalUrl.value = await readAsDataURL(file)
    // 上传后自动生成报告（无需再点击按钮）
    const fd = new FormData()
    fd.append('task_name', `单图检测-${new Date().toLocaleString('zh-CN', { hour12: false })}`)
    fd.append('files', file)
    const res = await createTask(fd)
    taskInfo.value = res.task
    result.value = res as unknown as ReportResultData
    savedReportId.value = res.report_ids?.[0] ?? null
    resultImageUrl.value = mediaUrl(res.images?.[0]?.result_image as string) ?? ''
    // 拉取报告详情获取可下载文件
    try {
      const { getReportDetail } = await import('@/api')
      const detail = await getReportDetail(savedReportId.value as number)
      reportFileUrl.value = detail.report_file ? mediaUrl(detail.report_file) : ''
    } catch {
      // 报告文件获取失败不影响检测结果展示
    }
    ElMessage.success(`检测完成，共发现 ${res.total_defects} 处缺陷，已生成报告`)
  } catch (err) {
    originalUrl.value = ''
    ElMessage.error(isApiError(err) ? err.message : '分析失败，请检查后端服务是否启动')
  } finally {
    loading.value = false
  }
}

function onSelect(files: File[]) {
  if (files.length) handleFile(files[0])
}

function resetSingle() {
  originalUrl.value = ''
  originalName.value = ''
  originalFile.value = null
  result.value = null
  taskInfo.value = null
  savedReportId.value = null
  reportFileUrl.value = ''
  resultImageUrl.value = ''
  selectedDefectId.value = null
}

function goToReport() {
  if (savedReportId.value != null) {
    router.push(`/reports/${savedReportId.value}`)
  }
}

function downloadReport() {
  if (reportFileUrl.value) {
    const a = document.createElement('a')
    a.href = reportFileUrl.value
    a.download = `检测报告-${savedReportId.value ?? ''}.html`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
  } else {
    ElMessage.warning('报告文件暂不可用')
  }
}
</script>

<template>
  <div class="detect">
    <div class="mode-bar">
      <div class="panel-title-wrap">
        <h2>智能检测</h2>
        <p>基于 YOLOv8 模型，上传图片即可自动识别裂缝、剥落、坑洞等缺陷</p>
      </div>
    </div>

    <div class="single-grid">
      <!-- 上传/预览 -->
      <section class="panel">
        <div v-if="!originalUrl" class="dropzone" @dragover.prevent @drop.prevent="onSelect($event.dataTransfer.files)">
          <div class="scan-frame">
            <div class="dz-inner">
              <div class="dz-icon"><el-icon :size="28"><Upload /></el-icon></div>
              <p class="dz-main">将图片拖入此处开始检测</p>
              <p class="dz-sub">支持 JPG / PNG / BMP</p>
              <el-upload
                :show-file-list="false"
                :before-upload="() => false"
                :on-change="(f: any) => onSelect([f.raw!])"
                accept="image/*"
              >
                <el-button type="primary" size="large" :icon="Plus">选择图片</el-button>
              </el-upload>
            </div>
          </div>
        </div>
        <div v-else class="stage">
          <div class="stage-head">
            <span class="mono fname">{{ originalName }}</span>
            <el-button :icon="RefreshRight" size="small" text @click="resetSingle">重新上传</el-button>
          </div>
          <div class="stage-body">
            <img :src="originalUrl" alt="预览" />
            <div v-if="loading" class="processing">
              <div class="scanline"></div>
              <div class="proc-text">
                <el-icon class="is-loading" :size="16"><Loading /></el-icon>
                <span class="mono">DETECTING...</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 检测结果 -->
      <section class="panel">
        <div v-if="!result && !loading" class="empty">
          <div class="empty-mark"><el-icon :size="24"><Upload /></el-icon></div>
          <p class="empty-main">等待检测</p>
          <p class="empty-sub">上传图片后，系统将自动调用桥梁、公路双模型识别缺陷并生成检测报告。</p>
        </div>
        <div v-else-if="loading" class="empty">
          <el-icon class="is-loading" :size="30" color="#1e90ff"><Loading /></el-icon>
          <p class="empty-main">正在分析图片...</p>
          <p class="empty-sub">双模型推理中，请稍候</p>
        </div>

        <template v-else-if="result">
          <div class="result-head">
            <span class="result-count mono">{{ result.total_defects }} 处缺陷</span>
            <el-tag type="success" effect="light" size="small">报告已生成 (任务 #{{ taskInfo?.id }})</el-tag>
          </div>

          <!-- 融合标注图（前端绘制检测框，可交互高亮） -->
          <div class="annotated">
            <div class="annotated-head">
              <span class="mono">FUSED RESULT</span>
              <span class="legend mono"><i class="sw bridge"></i>桥梁模型 <i class="sw road"></i>公路模型</span>
            </div>
            <div v-if="originalUrl" class="img-wrap">
              <img :src="originalUrl" alt="检测原图" class="base-img" />
              <svg class="overlay" viewBox="0 0 100 100" preserveAspectRatio="none">
                <rect
                  v-for="d in defects"
                  :key="d.id"
                  :x="d.x1 * 100"
                  :y="d.y1 * 100"
                  :width="(d.x2 - d.x1) * 100"
                  :height="(d.y2 - d.y1) * 100"
                  class="defect-box"
                  :class="{ active: selectedDefectId === d.id, bridge: d.source === 'bridge', road: d.source === 'road' }"
                />
              </svg>
            </div>
            <div v-else class="no-img">无标注图</div>
          </div>

          <!-- 缺陷明细（悬停高亮对应检测框） -->
          <div v-if="defects.length" class="defect-list">
            <div class="defect-list-head">缺陷明细（悬停查看标注）</div>
            <div
              v-for="d in defects"
              :key="d.id"
              class="defect-item"
              :class="{ active: selectedDefectId === d.id }"
              @mouseenter="selectDefect(d.id)"
              @mouseleave="clearDefect"
            >
              <span class="d-src" :class="d.source">{{ d.source === 'bridge' ? '桥梁' : '公路' }}</span>
              <span class="d-type">{{ classMap[d.defect_type] ?? d.defect_type }}</span>
              <span class="d-conf">{{ (d.confidence * 100).toFixed(1) }}%</span>
            </div>
          </div>

          <div class="telemetry">
            <div class="tel tel-total">
              <span class="tel-num mono">{{ String(result.total_defects).padStart(2, '0') }}</span>
              <span class="tel-label">缺陷总数</span>
            </div>
            <div v-for="s in stats" :key="s.label" class="tel">
              <span class="tel-num mono" :style="{ color: s.color }">{{ String(s.count).padStart(2, '0') }}</span>
              <span class="tel-label">{{ s.label }}</span>
            </div>
          </div>

          <div class="result-actions">
            <el-button v-if="reportFileUrl" type="primary" @click="downloadReport">
              <i class="bi bi-download"></i>
              <span>下载报告</span>
            </el-button>
            <el-button type="success" @click="goToReport">
              <i class="bi bi-file-earmark-text"></i>
              <span>查看报告</span>
            </el-button>
          </div>
        </template>
      </section>
    </div>
  </div>
</template>

<style scoped>
.detect {
  display: flex;
  flex-direction: column;
  gap: 18px;
  max-width: 1440px;
  margin: 0 auto;
  padding: 24px;
  animation: fadeIn 0.4s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.mode-bar {
  display: flex;
  align-items: flex-start;
}

.panel-title-wrap h2 {
  font-size: 20px;
  font-weight: 700;
  color: #fff;
}

.panel-title-wrap p {
  font-size: 13px;
  color: var(--text-3);
  margin-top: 6px;
}

.single-grid {
  display: grid;
  grid-template-columns: 1.15fr 1fr;
  gap: 18px;
}

.panel {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 18px;
  backdrop-filter: blur(14px);
  box-shadow: var(--shadow-card);
  min-height: 420px;
}

/* 上传区 */
.dropzone {
  min-height: 420px;
  border-radius: 12px;
  background: var(--surface-2);
  cursor: pointer;
}

.scan-frame {
  position: relative;
  height: 100%;
  min-height: 420px;
  border: 1.5px dashed var(--border-strong);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: border-color 0.2s, background 0.2s;
}

.dropzone:hover .scan-frame {
  border-color: var(--blue);
  background: var(--blue-soft);
}

.dz-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 24px;
  text-align: center;
}

.dz-icon {
  width: 58px;
  height: 58px;
  border-radius: 50%;
  border: 1px solid var(--border-strong);
  background: var(--surface);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--blue);
}

.dz-main {
  font-size: 15px;
  font-weight: 500;
  color: var(--text);
}

.dz-sub {
  font-size: 11px;
  color: var(--text-3);
  margin-bottom: 6px;
}

/* 预览 */
.stage-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
  color: var(--text-3);
  padding: 8px 2px;
}

.fname {
  color: var(--text-2);
  max-width: 70%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.stage-body {
  position: relative;
  border: 1px solid var(--border);
  border-radius: 10px;
  overflow: hidden;
  background: #0b1120;
}

.stage-body img {
  display: block;
  width: 100%;
  max-height: 460px;
  object-fit: contain;
}

.processing {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  background: rgba(11, 17, 32, 0.55);
  overflow: hidden;
}

.scanline {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--blue), transparent);
  animation: scan 2.2s linear infinite;
}

@keyframes scan {
  0% { transform: translateY(0); }
  100% { transform: translateY(460px); }
}

.proc-text {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(13, 22, 38, 0.9);
  border: 1px solid rgba(30, 144, 255, 0.4);
  border-radius: 8px;
  padding: 8px 14px;
  margin-bottom: 16px;
  font-size: 11px;
  color: var(--blue-light);
  letter-spacing: 0.1em;
}

/* 结果 */
.empty {
  min-height: 420px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  text-align: center;
  padding: 0 32px;
  border: 1px dashed var(--border-strong);
  border-radius: 12px;
}

.empty-mark {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  border: 1px solid var(--border-strong);
  background: var(--surface-2);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-3);
}

.empty-main {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-2);
}

.empty-sub {
  font-size: 12px;
  line-height: 1.7;
  color: var(--text-3);
  max-width: 300px;
}

.result-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.result-count {
  font-size: 18px;
  font-weight: 700;
  color: var(--blue-light);
}

.telemetry {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(84px, 1fr));
  gap: 10px;
  margin-bottom: 16px;
}

.tel {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 12px 6px;
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: 9px;
}

.tel-total {
  border-color: var(--accent-line);
  background: var(--blue-soft);
}

.tel-num {
  font-size: 18px;
  font-weight: 700;
  color: var(--text);
}

.tel-total .tel-num {
  color: var(--blue);
}

.tel-label {
  font-size: 11px;
  color: var(--text-3);
}

/* 融合标注图 */
.annotated {
  border: 1px solid var(--border);
  border-radius: 10px;
  overflow: hidden;
  background: #0b1120;
  margin-bottom: 16px;
}

.annotated-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  font-size: 10px;
  letter-spacing: 0.14em;
  color: var(--text-3);
  background: var(--surface-2);
  border-bottom: 1px solid var(--border);
}

.legend {
  display: flex;
  align-items: center;
  gap: 10px;
}

.legend .sw {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 2px;
  margin-right: 4px;
  vertical-align: -1px;
}

.legend .sw.bridge {
  background: #1e90ff;
}

.legend .sw.road {
  background: #ff8c1a;
}

.annotated img {
  display: block;
  width: 100%;
  max-height: 400px;
  object-fit: contain;
}

/* 可交互标注图 */
.img-wrap {
  position: relative;
}

.img-wrap .base-img {
  display: block;
  width: 100%;
  max-height: 400px;
  object-fit: contain;
}

.overlay {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.defect-box {
  fill: rgba(30, 144, 255, 0.12);
  stroke: #1e90ff;
  stroke-width: 0.6;
  transition: stroke 0.15s ease, fill 0.15s ease;
}

.defect-box.bridge {
  stroke: #1e90ff;
  fill: rgba(30, 144, 255, 0.12);
}

.defect-box.road {
  stroke: #ff8c1a;
  fill: rgba(255, 140, 26, 0.12);
}

.defect-box.active {
  stroke: #f0574a;
  stroke-width: 1.2;
  fill: rgba(240, 87, 74, 0.25);
}

/* 缺陷明细列表 */
.defect-list {
  margin-bottom: 16px;
}

.defect-list-head {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-2);
  margin-bottom: 8px;
}

.defect-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  margin-bottom: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
  background: var(--surface-2);
}

.defect-item:hover {
  border-color: var(--blue-light);
  background: rgba(30, 144, 255, 0.18);
}

.defect-item.active {
  border-color: #f0574a;
  background: rgba(240, 87, 74, 0.1);
}

.d-src {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 5px;
  border: 1px solid;
  font-weight: 500;
  white-space: nowrap;
}

.d-src.bridge {
  color: #1e90ff;
  border-color: #1e90ff;
  background: rgba(30, 144, 255, 0.1);
}

.d-src.road {
  color: #ff8c1a;
  border-color: #ff8c1a;
  background: rgba(255, 140, 26, 0.1);
}

.d-type {
  flex: 1;
  font-size: 13px;
  color: var(--text);
}

.d-conf {
  font-size: 13px;
  font-weight: 600;
  color: #f0574a;
}

.no-img {
  height: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-3);
  font-size: 12px;
}

.result-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 8px;
}

@media (max-width: 1100px) {
  .single-grid {
    grid-template-columns: 1fr;
  }
}
</style>
