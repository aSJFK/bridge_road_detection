<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { listDatasets } from '@/api'
import { isApiError } from '@/api/http'
import type { DatasetItem } from '@/api/types'

const items = ref<DatasetItem[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = 10
const loading = ref(false)

const statusMap: Record<string, { type: 'success' | 'info' | 'warning'; text: string }> = {
  active: { type: 'success', text: '启用' },
  draft: { type: 'info', text: '草稿' },
  archived: { type: 'warning', text: '已归档' },
}

async function load() {
  loading.value = true
  try {
    const data = await listDatasets({ page: page.value, page_size: pageSize })
    items.value = data.results
    total.value = data.count
  } catch (e) {
    ElMessage.error(isApiError(e) ? e.message : '数据集加载失败，请稍后重试')
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
      <h2>数据集管理</h2>
      <p>管理桥梁与道路缺陷训练数据集</p>
    </div>

    <div class="panel">
      <div class="panel-bar"><span>共 {{ total }} 个数据集</span></div>
      <el-table v-loading="loading" :data="items">
        <el-table-column prop="name" label="数据集名称" min-width="180" />
        <el-table-column prop="description" label="描述" min-width="220" show-overflow-tooltip />
        <el-table-column label="图片数量" width="100">
          <template #default="{ row }"><span class="mono">{{ row.image_count }}</span></template>
        </el-table-column>
        <el-table-column label="标注数量" width="100">
          <template #default="{ row }"><span class="mono">{{ row.annotation_count }}</span></template>
        </el-table-column>
        <el-table-column prop="version" label="版本" width="90">
          <template #default="{ row }"><span class="mono ver">{{ row.version }}</span></template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusMap[row.status]?.type ?? 'info'" effect="light" size="small" round>
              {{ statusMap[row.status]?.text ?? row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_by_name" label="创建人" width="110" />
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

.ver {
  color: var(--blue-light);
  font-size: 12px;
}

.pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
