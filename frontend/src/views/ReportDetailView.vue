<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getReportDetail, listReportRatings, rateReport, updateRating, deleteRating } from '@/api'
import { isApiError, mediaUrl } from '@/api/http'
import { authState } from '@/stores/auth'
import type { ReportDetail, ReportRating } from '@/api/types'

const route = useRoute()
const router = useRouter()
const reportId = Number(route.params.id)

const loading = ref(true)
const report = ref<ReportDetail | null>(null)
const ratings = ref<ReportRating[]>([])
const loadError = ref(false)

// 评价表单
const score = ref(5)
const comment = ref('')
const submitting = ref(false)

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

const sourceMap: Record<string, { label: string; color: string }> = {
  bridge: { label: '桥梁', color: '#f0574a' },
  road: { label: '公路', color: '#ff8c1a' },
}

const myRating = computed(() => report.value?.my_rating ?? null)
const isAdmin = computed(() => authState.user?.role === 'admin')

// 缺陷明细悬停高亮：悬停某行 -> 对应框变红，移开 -> 恢复
const selectedDefectId = ref<number | null>(null)

function selectDefect(id: number) {
  selectedDefectId.value = id
}

function clearDefect() {
  selectedDefectId.value = null
}

const originalImageUrl = computed(() => (report.value?.image_url ? mediaUrl(report.value.image_url) : ''))

async function load() {
  loading.value = true
  loadError.value = false
  try {
    report.value = await getReportDetail(reportId)
    ratings.value = await listReportRatings(reportId)
  } catch (e) {
    loadError.value = true
    ElMessage.error(isApiError(e) ? e.message : '报告加载失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

async function submitRating() {
  if (!report.value) return
  if (myRating.value) {
    ElMessage.warning('您已评价过该报告，提交后不可修改')
    return
  }
  try {
    await ElMessageBox.confirm(
      `评分：${score.value} 星\n\n评价提交后将无法修改，是否确认提交？`,
      '确认提交评价',
      { confirmButtonText: '确认提交', cancelButtonText: '再想想', type: 'warning' },
    )
  } catch {
    return // 用户取消
  }
  submitting.value = true
  try {
    await rateReport(reportId, score.value, comment.value.trim())
    ElMessage.success('评价已提交，提交后无法修改')
    await load()
  } catch (e) {
    ElMessage.error(isApiError(e) ? e.message : '评价提交失败')
  } finally {
    submitting.value = false
  }
}

async function onAdminEdit(r: ReportRating) {
  try {
    const { value } = await ElMessageBox.prompt('修改评分（1-5）', '编辑评价', {
      confirmButtonText: '保存',
      cancelButtonText: '取消',
      inputValue: String(r.score),
      inputValidator: (v: string) => (/^[1-5]$/.test(v) ? true : '评分必须为 1~5 的整数'),
    })
    await updateRating(r.id, { score: Number(value), comment: r.comment })
    ElMessage.success('评价已更新')
    await load()
  } catch {
    // 取消
  }
}

async function onAdminDelete(r: ReportRating) {
  try {
    await ElMessageBox.confirm(`确认删除 ${r.username} 的评价？`, '删除评价', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
  } catch {
    return
  }
  try {
    await deleteRating(r.id)
    ElMessage.success('评价已删除')
    await load()
  } catch (e) {
    ElMessage.error(isApiError(e) ? e.message : '删除失败')
  }
}

onMounted(load)
</script>

<template>
  <div class="page-wrap">
    <div class="back-bar">
      <el-button text @click="router.push('/reports')">
        <i class="bi bi-arrow-left"></i>
        <span>返回报告列表</span>
      </el-button>
    </div>

    <div v-if="loadError" class="error-box">
      <el-alert title="报告加载失败，请稍后重试" type="error" :closable="false" show-icon />
    </div>

    <template v-else-if="report">
      <div class="page-head">
        <h2>{{ report.report_name }}</h2>
        <p>
          {{ report.created_by_name }} 创建 · {{ report.created_at?.slice(0, 19).replace('T', ' ') }}
          <template v-if="report.average_score != null">
            · 平均评分 {{ report.average_score }} ★ ({{ report.rating_count }} 条评价)
          </template>
        </p>
      </div>

      <div class="grid">
        <!-- 标注图（原图 + 前端绘制的检测框，可交互高亮） -->
        <div class="panel image-panel">
          <h3>检测结果（双模型融合标注）</h3>
          <div class="legend-row">
            <span class="legend-item"><i class="dot bridge"></i>桥梁模型</span>
            <span class="legend-item"><i class="dot road"></i>公路模型</span>
            <span class="legend-item"><i class="dot active"></i>选中缺陷</span>
          </div>
          <div v-if="originalImageUrl" class="result-image img-wrap">
            <img :src="originalImageUrl" alt="检测原图" class="base-img" />
            <svg class="overlay" viewBox="0 0 100 100" preserveAspectRatio="none">
              <rect
                v-for="d in report.defects"
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
          <div v-else-if="report.result_url" class="result-image">
            <img :src="mediaUrl(report.result_url)" alt="检测结果" />
          </div>
          <div v-else class="no-img">无结果图</div>
        </div>

        <!-- 缺陷明细（鼠标悬停高亮对应标注框） -->
        <div class="panel">
          <h3>缺陷明细（共 {{ report.total_defects }} 处，悬停查看标注）</h3>
          <div class="defect-list">
            <div
              v-for="d in report.defects"
              :key="d.id"
              class="defect-row"
              :class="{ active: selectedDefectId === d.id }"
              @mouseenter="selectDefect(d.id)"
              @mouseleave="clearDefect"
            >
              <span class="src-tag" :style="{ background: sourceMap[d.source]?.color + '22', color: sourceMap[d.source]?.color, borderColor: sourceMap[d.source]?.color }">
                {{ sourceMap[d.source]?.label ?? d.source }}
              </span>
              <span class="dt">{{ classMap[d.defect_type] ?? d.defect_type }}</span>
              <span class="mono conf">{{ (d.confidence * 100).toFixed(1) }}%</span>
              <code class="mono bbox">[{{ d.x1 }},{{ d.y1 }},{{ d.x2 }},{{ d.y2 }}]</code>
            </div>
          </div>
        </div>
      </div>

      <!-- 我的评价 / 提交评价 -->
      <div class="panel rating-panel">
        <h3>我的评价</h3>
        <template v-if="myRating">
          <div class="my-rating">
            <el-rate :model-value="myRating.score" disabled />
            <p class="my-comment">{{ myRating.comment || '（无评价内容）' }}</p>
            <el-alert title="您已评价过该报告，提交后无法修改" type="info" :closable="false" show-icon />
          </div>
        </template>
        <template v-else>
          <el-form label-position="top">
            <el-form-item label="评分">
              <el-rate v-model="score" show-score score-template="{value} 星" />
            </el-form-item>
            <el-form-item label="评价内容">
              <el-input v-model="comment" type="textarea" :rows="3" maxlength="500" show-word-limit placeholder="请输入您对检测结果的评价（可选）" />
            </el-form-item>
            <el-button type="primary" :loading="submitting" @click="submitRating">
              <i class="bi bi-check-circle"></i>
              <span>提交评价</span>
            </el-button>
            <p class="hint"><i class="bi bi-info-circle"></i> 提交后无法修改评价，请确认后提交</p>
          </el-form>
        </template>
      </div>

      <!-- 全部评价 -->
      <div class="panel">
        <h3>全部评价（{{ ratings.length }}）</h3>
        <div v-if="ratings.length" class="rating-list">
          <div v-for="r in ratings" :key="r.id" class="rating-item">
            <div class="rating-item-head">
              <span class="rating-avatar">{{ r.username.charAt(0) }}</span>
              <div class="rating-meta">
                <span class="rating-user">{{ r.username }}</span>
                <el-rate :model-value="r.score" disabled size="small" />
              </div>
              <span class="rating-time mono">{{ r.created_at?.slice(0, 19).replace('T', ' ') }}</span>
              <div v-if="isAdmin" class="rating-admin">
                <el-button link type="primary" size="small" @click="onAdminEdit(r)">
                  <i class="bi bi-pencil"></i> 编辑
                </el-button>
                <el-button link type="danger" size="small" @click="onAdminDelete(r)">
                  <i class="bi bi-trash"></i> 删除
                </el-button>
              </div>
            </div>
            <p v-if="r.comment" class="rating-comment">{{ r.comment }}</p>
          </div>
        </div>
        <div v-else class="no-rating">暂无评价</div>
      </div>
    </template>
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

.back-bar {
  margin-bottom: 10px;
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

.grid {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 18px;
  margin-bottom: 18px;
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
  margin-bottom: 14px;
}

.legend-row {
  display: flex;
  gap: 18px;
  margin-bottom: 12px;
}

.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-2);
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 3px;
}

.dot.bridge {
  background: #1e90ff;
}

.dot.road {
  background: #ff8c1a;
}

.dot.active {
  background: #f0574a;
}

.result-image {
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid var(--border);
  background: #0b1120;
}

.result-image img {
  display: block;
  width: 100%;
  max-height: 480px;
  object-fit: contain;
}

/* 可交互标注图 */
.img-wrap {
  position: relative;
}

.img-wrap .base-img {
  display: block;
  width: 100%;
  max-height: 480px;
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

.no-img {
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-3);
}

.src-tag {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 5px;
  border: 1px solid;
  font-weight: 500;
}

.conf {
  color: #f0574a;
  font-weight: 600;
}

.bbox {
  font-size: 10px;
  color: var(--text-3);
}

/* 缺陷明细列表（悬停高亮） */
.defect-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 380px;
  overflow-y: auto;
  padding-right: 4px;
}

.defect-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 9px 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface-2);
  cursor: pointer;
  transition: background 0.15s ease, border-color 0.15s ease;
}

.defect-row:hover {
  background: rgba(30, 144, 255, 0.18);
  border-color: var(--blue-light);
}

.defect-row.active {
  background: rgba(240, 87, 74, 0.18);
  border-color: #f0574a;
}

.defect-row .dt {
  flex: 1;
  font-size: 13px;
  color: var(--text);
}

.rating-panel {
  margin-bottom: 18px;
}

.hint {
  font-size: 12px;
  color: var(--text-3);
  margin-top: 10px;
}

.hint i {
  color: var(--blue-light);
}

.my-rating {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.my-comment {
  font-size: 13px;
  color: var(--text-2);
}

.rating-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.rating-item {
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 12px 14px;
}

.rating-item-head {
  display: flex;
  align-items: center;
  gap: 10px;
}

.rating-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #4da3ff, #1e90ff);
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.rating-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.rating-user {
  font-size: 13px;
  color: #fff;
  font-weight: 500;
}

.rating-time {
  font-size: 11px;
  color: var(--text-3);
  margin-left: auto;
}

.rating-admin {
  display: flex;
  gap: 4px;
}

.rating-comment {
  font-size: 13px;
  color: var(--text-2);
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid var(--border);
}

.no-rating {
  text-align: center;
  color: var(--text-3);
  padding: 24px 0;
  font-size: 13px;
}

.error-box {
  margin-bottom: 18px;
}

@media (max-width: 900px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>
