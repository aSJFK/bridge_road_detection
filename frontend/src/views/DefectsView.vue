<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { listDefects } from '@/api'
import { isApiError } from '@/api/http'
import type { DefectItem } from '@/api/types'

const items = ref<DefectItem[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = 10
const loading = ref(false)

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

const typeTagMap: Record<string, 'primary' | 'warning' | 'info' | 'danger' | 'success'> = {
  crack: 'primary',
  breakage: 'warning',
  comb: 'success',
  hole: 'danger',
  reinforcement: 'primary',
  seepage: 'info',
  liefeng: 'primary',
  bolou: 'warning',
  fengwo: 'success',
  mamian: 'info',
  kongdong: 'danger',
  lujin: 'primary',
  shenshui: 'info',
  spalling: 'warning',
  pothole: 'success',
  corrosion: 'danger',
  other: 'info',
}

async function load() {
  loading.value = true
  try {
    const data = await listDefects({ page: page.value, page_size: pageSize })
    items.value = data.results
    total.value = data.count
  } catch (e) {
    ElMessage.error(isApiError(e) ? e.message : '缺陷数据加载失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

function onPage(p: number) {
  page.value = p
  load()
}

onMounted(load)
</script>

<template>
  <div class="page-wrap">
    <div class="page-head">
      <h2>缺陷管理</h2>
      <p>对检测出的缺陷进行分类、记录与跟踪管理</p>
    </div>

    <div class="panel">
      <div class="panel-bar">
        <span>共 {{ total }} 条缺陷记录</span>
      </div>
      <el-table v-loading="loading" :data="items">
        <el-table-column label="ID" width="80">
          <template #default="{ row }"><span class="mono">#{{ row.id }}</span></template>
        </el-table-column>
        <el-table-column label="缺陷类型" width="130">
          <template #default="{ row }">
            <el-tag :type="typeTagMap[row.defect_type] ?? 'info'" effect="light" size="small" round>
              {{ classMap[row.defect_type] ?? row.defect_type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="置信度" width="110">
          <template #default="{ row }">
            <span class="mono conf" :class="{ low: row.confidence < 0.6 }">{{ (row.confidence * 100).toFixed(1) }}%</span>
          </template>
        </el-table-column>
        <el-table-column label="检测框坐标" min-width="180">
          <template #default="{ row }">
            <code class="mono bbox">[{{ row.x1 }}, {{ row.y1 }}, {{ row.x2 }}, {{ row.y2 }}]</code>
          </template>
        </el-table-column>
        <el-table-column label="时间" width="160">
          <template #default="{ row }">
            <span class="mono time">{{ row.created_at?.slice(0, 19).replace('T', ' ') }}</span>
          </template>
        </el-table-column>
      </el-table>

      <div class="pager">
        <el-pagination background layout="prev, pager, next, total" :total="total" :page-size="pageSize" :current-page="page" @current-change="onPage" />
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

.panel {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 18px 20px;
  backdrop-filter: blur(14px);
  box-shadow: var(--shadow-card);
}

.panel-bar {
  font-size: 13px;
  color: var(--text-3);
  margin-bottom: 14px;
}

.conf {
  color: var(--success);
  font-weight: 600;
}

.conf.low {
  color: var(--warning);
}

.bbox {
  font-size: 11px;
  color: var(--text-3);
}

.time {
  font-size: 12px;
  color: var(--text-3);
}

.pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
