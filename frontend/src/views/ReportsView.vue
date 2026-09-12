<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listReports, deleteReport } from '@/api'
import { isApiError, mediaUrl } from '@/api/http'
import { authState } from '@/stores/auth'
import type { ReportItem } from '@/api/types'

const router = useRouter()
const items = ref<ReportItem[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = 10
const loading = ref(false)
const startDate = ref('')
const endDate = ref('')

async function load() {
  loading.value = true
  try {
    const params: Record<string, string | number> = { page: page.value, page_size: pageSize }
    if (startDate.value) params.start_date = startDate.value
    if (endDate.value) params.end_date = endDate.value
    const data = await listReports(params)
    items.value = data.results
    total.value = data.count
  } catch (e) {
    ElMessage.error(isApiError(e) ? e.message : '报告数据加载失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

function onPage(p: number) {
  page.value = p
  load()
}

function search() {
  page.value = 1
  load()
}

function clearFilter() {
  startDate.value = ''
  endDate.value = ''
  page.value = 1
  load()
}

function openDetail(id: number) {
  router.push(`/reports/${id}`)
}

async function removeReport(row: ReportItem) {
  try {
    await ElMessageBox.confirm(`确认删除报告「${row.report_name}」？删除后不可恢复。`, '删除报告', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
  } catch {
    return
  }
  try {
    await deleteReport(row.id)
    ElMessage.success('报告已删除')
    load()
  } catch (e) {
    ElMessage.error(isApiError(e) ? e.message : '删除失败')
  }
}

onMounted(load)
</script>

<template>
  <div class="page-wrap">
    <div class="page-head">
      <h2>报告管理</h2>
      <p>查看检测报告详情，并对报告进行评价与打分</p>
    </div>

    <div class="filter-bar">
      <el-date-picker
        v-model="startDate"
        type="date"
        placeholder="开始日期"
        value-format="YYYY-MM-DD"
        style="width: 150px"
      />
      <span class="filter-sep">至</span>
      <el-date-picker
        v-model="endDate"
        type="date"
        placeholder="结束日期"
        value-format="YYYY-MM-DD"
        style="width: 150px"
      />
      <el-button type="primary" @click="search"><i class="bi bi-search"></i> 查询</el-button>
      <el-button @click="clearFilter">重置</el-button>
    </div>

    <div class="panel">
      <div class="panel-bar"><span>共 {{ total }} 份检测报告</span></div>
      <el-table v-loading="loading" :data="items">
        <el-table-column label="编号" width="80">
          <template #default="{ row }"><span class="mono id">#{{ String(row.id).padStart(4, '0') }}</span></template>
        </el-table-column>
        <el-table-column label="结果图" width="90">
          <template #default="{ row }">
            <img v-if="row.result_url" :src="mediaUrl(row.result_url)" class="cell-thumb" alt="" @click="openDetail(row.id)" />
            <span v-else class="cell-thumb empty">—</span>
          </template>
        </el-table-column>
        <el-table-column prop="report_name" label="报告名称" min-width="170" show-overflow-tooltip />
        <el-table-column label="缺陷数" width="90">
          <template #default="{ row }"><span class="mono">{{ row.total_defects }}</span></template>
        </el-table-column>
        <el-table-column label="平均评分" width="110">
          <template #default="{ row }">
            <span v-if="row.average_score != null" class="score">{{ row.average_score }} <span class="star">★</span></span>
            <span v-else class="unrated">未评价</span>
          </template>
        </el-table-column>
        <el-table-column label="评价数" width="90">
          <template #default="{ row }"><span class="mono">{{ row.rating_count }}</span></template>
        </el-table-column>
        <el-table-column prop="created_by_name" label="创建人" width="110" />
        <el-table-column label="时间" width="160">
          <template #default="{ row }"><span class="mono time">{{ row.created_at?.slice(0, 19).replace('T', ' ') }}</span></template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDetail(row.id)">查看详情</el-button>
            <el-button link type="danger" @click="removeReport(row)">删除</el-button>
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

.filter-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
}

.filter-sep {
  color: var(--text-3);
  font-size: 13px;
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

.cell-thumb {
  width: 60px;
  height: 44px;
  border-radius: 6px;
  object-fit: cover;
  cursor: pointer;
  background: #0b1120;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cell-thumb.empty {
  color: var(--text-3);
  font-size: 12px;
}

.id {
  color: var(--blue-light);
  font-size: 12px;
}

.score {
  color: #ffb800;
  font-weight: 600;
}

.star {
  color: #ffb800;
}

.unrated {
  color: var(--text-3);
  font-size: 12px;
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
